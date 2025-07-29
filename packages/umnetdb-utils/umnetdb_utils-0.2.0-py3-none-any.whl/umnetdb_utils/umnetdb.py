from typing import List, Optional
import logging
import re
import ipaddress
from copy import deepcopy

from .base import UMnetdbBase
from .utils import is_ip_address, Packet, Hop, Path, LOCAL_PROTOCOLS

logger = logging.getLogger(__name__)

class UMnetdb(UMnetdbBase):
    URL = "postgresql+psycopg://{UMNETDB_USER}:{UMNETDB_PASSWORD}@wintermute.umnet.umich.edu/umnetdb"

    def get_neighbors(self, device: str, known_devices_only: bool = True, interface:Optional[str]=None) -> List[dict]:
        """
        Gets a list of the neighbors of a particular device. If the port
        has a parent in the LAG table that is included as well.
        Neighbor hostname is also looked up in the device table and
        the "source of truth" hostname is returned instead of what shows
        up in lldp neighbor.

        Setting 'known_devices_only' to true only returns neighbors that are found
        in umnet_db's device table. Setting it to false will return all lldp neighbors
        and will include things like phones and APs.

        Returns results as a list of dictionary entries keyed on column names.
        :device: Name of the device
        :known_devices_only: If set to true, will only return neighbors found in umnetdb's device table.
        :interface: If supplied, restrict to only find neighbors on a particular interface on the device
        """

        if known_devices_only:
            select = [
                "n.port",
                "n_d.name as remote_device",
                "n.remote_port",
                "l.parent",
                "n_l.parent as remote_parent",
            ]
            joins = [
                "join device n_d on n_d.hostname=n.remote_device",
                "left outer join lag l on l.device=n.device and l.member=n.port",
                "left outer join lag n_l on n_l.device=n_d.name and n_l.member=n.remote_port",
            ]
        else:
            select = [
                "n.port",
                "coalesce(n_d.name, n.remote_device) as remote_device",
                "n.remote_port",
                "l.parent",
                "n_l.parent as remote_parent",
            ]
            joins = [
                "left outer join device n_d on n_d.hostname=n.remote_device",
                "left outer join lag l on l.device=n.device and l.member=n.port",
                "left outer join lag n_l on n_l.device=n_d.name and n_l.member=n.remote_port",
            ]

        table = "neighbor n"

        where = [f"n.device='{device}'"]
        if interface:
            where.append(f"n.port='{interface}'")

        query = self._build_select(select, table, joins, where)

        return self.execute(query)

    def get_dlzone(self, zone_name: str) -> List[dict]:
        """
        Gets all devices within a DL zone based on walking the 'neighbors'
        table.
        
        For each device, the following attributes are returned:
        "name", "ip", "version", "vendor", "model", "serial"

        :zone_name: Name of the DL zone
        """
        device_cols = ["name", "ip", "version", "vendor", "model", "serial"]

        # step 1 is to find DLs in the database - we'll seed our zone with them
        query = self._build_select(
            select=device_cols,
            table="device",
            where=f"name similar to '(d-|dl-){zone_name}-(1|2)'",
        )
        dls = self.execute(query)

        if not dls:
            raise ValueError(f"No DLs found in umnetdb for zone {zone_name}")

        devices_by_name = {d["name"]: d for d in dls}

        # now we'll look for neighbors on each device within the zone.
        # Note that outside of the DLs we only expect to find devices that start with
        # "s-" anything else is considered 'outside the zone'
        todo = list(devices_by_name.keys())
        while len(todo) != 0:
            device = todo.pop()

            # note that by default this method only returns neighbors in the 'device' table,
            # any others are ignored
            neighs = self.get_neighbors(device)
            devices_by_name[device]["neighbors"] = {}
            for neigh in neighs:

                # only want 'd- or 'dl-' or 's-' devices, and we don't want out of band devices
                if re.match(r"(dl?-|s-)", neigh["remote_device"]) and not re.match(
                    r"s-oob-", neigh["remote_device"]
                ):
                    # adding neighbor to local device's neighbor list
                    devices_by_name[device]["neighbors"][neigh["port"]] = {
                        k: v for k, v in neigh.items() if k != "port"
                    }

                    # if we haven't seen this neighbor yet, pull data from our device table for it, and
                    # add it to our 'to do' list to pull its neighbors.
                    if neigh["remote_device"] not in devices_by_name:
                        query = self._build_select(
                            select=device_cols,
                            table="device",
                            where=f"name = '{neigh['remote_device']}'",
                        )
                        neigh_device = self.execute(query, fetch_one=True)
                        devices_by_name[neigh_device["name"]] = neigh_device

                        todo.append(neigh_device["name"])

        return list(devices_by_name.values())


    def l3info(self, search_str:str, detail:bool=False, num_results:int=10, exact:bool=False)->list[dict]:
        """
        Does a search of the umnetdb ip_interface table.
        
        :search_str: Can be an IP address, 'VlanX', or a full or partial netname
        :detail: Adds admin/oper status, primary/secondary, helpers, and timestamps to output.
        :num_results: Limits number of results printed out.
        :exact: Only return exact matches, either for IP addresses or for string matches.
        """

        cols = ["device", "ip_address", "interface", "description", "vrf"]
        if detail:
            cols.extend(["admin_up", "oper_up", "secondary", "helpers", "first_seen", "last_updated"])

        # 'is contained within' IP search - reference:
        # https://www.postgresql.org/docs/9.3/functions-net.html

        # VlanX based searches are always 'exact'
        if re.match(r"Vlan\d+$", search_str):
                where = [f"interface = '{search_str}'"]

        # ip or description based searches can be 'exact' or inexact
        elif exact:
            if is_ip_address(search_str):
                where = [f"host(ip_address) = '{search_str}'"]
            else:
                where = [f"description = '{search_str}'"]

        else:
            if is_ip_address(search_str):
                where = [f"ip_address >>= '{search_str}'"]
            else:
                where = [f"description like '{search_str}%'"]
        
        # removing IPs assigned to mgmt interfaces
        where.append("vrf != 'management'")

        query = self._build_select(
            select=cols,
            table="ip_interface",
            where=where,
            limit=num_results,
        )
        return self.execute(query)

    
    def route(self, router:str, prefix:str, vrf:str, resolve_nh:bool=True, details:bool=False) -> list[dict]:
        """
        Does an lpm query on a particular router for a particular prefix
        in a particular VRF.

        :router: Name of the router to query
        :prefix: Prefix to query for
        :vrf: Name of the VRF to query against
        :resolve_nh: If no nh_interface is present in the database, recursively resolve for it.
        :details: Set to true to get output of all columns in the route table.
        """
        if details:
            cols = ["*"]
        else:
            cols = ["device", "vrf", "prefix", "nh_ip", "nh_table", "nh_interface"]
            
        lpms = self.lpm_query(router, prefix, vrf, columns=cols)

        if not lpms:
            return []
        
        if not resolve_nh:
            return lpms

        resolved_results = []
        for route in lpms:
            if route["nh_interface"]:
                resolved_results.append(route)
            else:
                self._resolve_nh(route, resolved_results, 0)

        return resolved_results

    def lpm_query(self, router:str, prefix:str, vrf:str, columns:Optional[str]=None)->list[dict]:
        """
        Does an lpm query against a particular router, prefix, and vrf. Optionally specify
        which columns you want to limit the query to.
        """

        select = columns if columns else ["*"]

        query = self._build_select(
            select=select,
            table="route",
            where=[f"device='{router}'", f"prefix >>= '{prefix}'", f"vrf='{vrf}'"],
            order_by="prefix"
        )

        result = self.execute(query)

        if not result:
            return None
        
        if len(result) == 1:
            return result
        
        # peeling the longest matching prefix of the end of the results, which
        # are ordered by ascending prefixlength
        lpm_results = [result.pop()]

        # finding any other equivalent lpms. As soon as we run into one that
        # doesn't match we know we're done.
        result.reverse()
        for r in result:
            if r["prefix"] == lpm_results[0]["prefix"]:
                lpm_results.append(r)
            else:
                break
    
        return lpm_results
    
    def mpls_label(self, router:str, label:str) -> list[dict]:
        """
        Looks up a particular label for a particular device in the mpls table.
        :router: device name
        :label: label value
        """
        query = self._build_select(
            select=["*"],
            table="mpls",
            where=[f"device='{router}'", f"in_label='{label}'"]
        )
        return self.execute(query)
    
    def vni(self, router:str, vni:int) -> dict:
        """
        Looks up a particular vni on the router and returns
        the VRF or vlan_id it's associated with
        """

        query = self._build_select(
            select=["*"],
            table="vni",
            where=[f"device='{router}'", f"vni='{vni}'"]
        )
        return self.execute(query, fetch_one=True)

    
    def _resolve_nh(self, route:dict, resolved_routes:list[dict], depth:int) -> dict:
        """
        Recursively resolves next hop of a route till we find a nh interface.
        If we hit a recursion depth of 4 then an exception is thrown - the max depth on our
        network I've seen is like 2 (for a static route to an indirect next hop)
        """
        if route["nh_interface"]:
            return route
        
        depth += 1        
        if depth == 4:
            raise RecursionError(f"Reached max recursion depth of 4 trying to resolve route {route}")
        
        nh_ip = route["nh_ip"]
        nh_table = route["nh_table"]
        router = route["device"]

        nh_routes = self.lpm_query(router, nh_ip, nh_table)

        for nh_route in nh_routes:
            r = self._resolve_nh(nh_route, resolved_routes, depth)
            resolved_route = deepcopy(route)
            resolved_route["nh_interface"] = r["nh_interface"]
            if r["mpls_label"] and resolved_route["mpls_label"] is not None:
                resolved_route["mpls_label"].extend(r["mpls_label"])
            elif r["mpls_label"]:
                resolved_route["mpls_label"] = r["mpls_label"]
            resolved_route["nh_ip"] = r["nh_ip"]
            resolved_routes.append(resolved_route)


    def get_all_paths(self, src_ip:str, dst_ip:str):
        """
        Traces the path between a particular source and destination IP
        :src_ip: A source IP address, must be somewhere on our network
        :dst_ip: A destination IP address, does not have to be on our network.
        """
        for ip_name, ip in [("source", src_ip), ("destination", dst_ip)]:
            if not is_ip_address(ip):
                raise ValueError(f"invalid {ip_name} IP address {ip}")
        
        src_l3info = self.l3info(src_ip, num_results=1)
        if not src_l3info:
            raise ValueError(f"Could not find where {src_ip} is routed")
        
        packet = Packet(dst_ip=ipaddress.ip_address(dst_ip))
        hop = Hop(src_l3info[0]["device"], src_l3info[0]["vrf"], src_l3info[0]["interface"], packet)
        path = Path(hop)

        self._walk_path(path, hop, hop.router, hop.vrf, packet)

        return path.get_path()

    
    def _walk_path(self, path:Path, curr_hop:Hop, nh_router:str, nh_table:str, packet:Packet):

        logger.debug(f"\n******* walking path - current hop: {curr_hop}, nh_route: {nh_router}, nh_table {nh_table} *******")
        logger.debug(f"Known hops: {path.hops.keys()}")

        # mpls-based lookup
        if packet.label_stack:
            logger.debug("")
            routes = self.mpls_label(router=nh_router, label=packet.label_stack[-1])

        # otherwise we want to do an ip based lokup
        else:
            routes = self.route(router=nh_router, prefix=packet.dst_ip, vrf=nh_table, details=True)

        if not routes:
            raise ValueError(f"No route found for {curr_hop}")

        for idx, route in zip(range(1,len(routes)+1), routes):

            logger.debug(f"*** Processing route {idx} of {len(routes)}:{route} ***")
            nh_router = None
            nh_table = None
            new_packet = deepcopy(packet)

            # if the packet is not encapsulated and the route is local, we have reached our destination
            if not packet.is_encapped() and route.get("protocol") in LOCAL_PROTOCOLS:
                logger.debug(f"Destination reached at {curr_hop}")
                final_hop = Hop(route["device"], vrf=route["vrf"], interface=route["nh_interface"], packet=new_packet)
                path.add_hop(curr_hop, final_hop)
                continue

            # VXLAN decap - requires local lookup in the vrf that maps to the packet's VNI
            if route.get("protocol") == "direct" and packet.vni and curr_hop.router == route["device"]:
                vni = self.vni(router=route["device"], vni=packet.vni)
                new_packet.vxlan_decap()
                nh_table = vni["vrf"]
                nh_router = route["device"]
                logger.debug(f"vxlan-decapping packet, new packet {new_packet}")

            # MPLS decap - requires local lookup in the vrf indicated by 'nh_interface' field
            # of this aggregate route
            elif route.get("aggregate"):
                new_packet.mpls_pop()
                nh_table = route["nh_interface"]
                nh_router = route["device"]
                logger.debug(f"mpls aggregate route, new packet {new_packet}")

            # VXLAN encap - requires local lookup of encapped packet in the nh table
            elif route.get("vxlan_vni") and not packet.is_encapped():
                new_packet.vxlan_encap(route["vxlan_vni"], route["vxlan_endpoint"])
                logger.debug(f"vxlan-encapping packet, new packet {new_packet}")

            # MPLS encap for an IP route. Resolved routes will have both transport and vrf
            # labels if applicable - this 'push' will add both to the packet.
            elif route.get("mpls_label"):
                new_packet.mpls_push(route["mpls_label"])
                logger.debug(f"mpls-encapping packet, new packet {new_packet}")

            # MPLS route - note in our environment we don't have anything that requires a
            # push on an already-labeled packet (!)
            elif route.get("in_label"):

                if route["out_label"] == ["pop"]:
                    new_packet.mpls_pop()
                else:
                    new_packet.mpls_swap(route["out_label"])
                logger.debug(f"mpls push or swap, new packet {new_packet}")
            
            # if the next hop isn't local we need to figure out which router it's on. In our environment
            # the easiest way to do that is to use l3info against the nh_ip of the route.
            if not nh_router and route["nh_ip"]:
                
                l3i_router = self.l3info(str(route["nh_ip"]), exact=True)
                if l3i_router:
                    nh_router = l3i_router[0]["device"]
                    nh_table = nh_table if nh_table else l3i_router[0]["vrf"]
                    logger.debug(f"found router {nh_router} for nh ip {route['nh_ip']}")

            if not nh_router:
                raise ValueError(f"Unknown next hop for {curr_hop} route {route}")

            # add this hop to our path and if it's a new hop, keep waking
            new_hop = Hop(route["device"], vrf=route.get("nh_table", "default"), interface=route["nh_interface"], packet=new_packet)
            logger.debug(f"new hop generated: {new_hop}")
            new_path = path.add_hop(curr_hop, new_hop)
            if new_path:
                logger.debug("New path detected - still walking")
                self._walk_path(path, new_hop, nh_router, nh_table, new_packet)