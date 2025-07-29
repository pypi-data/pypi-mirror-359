import ipaddress
import re

from dataclasses import dataclass, field
from copy import copy, deepcopy

from typing import Optional, Union, List, Dict

type IPAddress = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]

LOCAL_PROTOCOLS = [
    "Access-internal",
    "am",
    "connected",
    "direct",
    "Direct",
    "hmm",
    "local",
    "VPN",
    "vrrpv3",
]

def is_ip_address(input_str:str, version:Optional[int]=None):
    try:
        ip = ipaddress.ip_address(input_str)
    except ValueError:
        return False

    if version and version != ip.version:
        return False

    return True


def is_ip_network(input_str:str, version:Optional[int]=None):
    # First check that this is a valid IP or network
    try:
        net = ipaddress.ip_network(input_str)
    except ValueError:
        return False

    if version and version != net.version:
        return False

    return True


def is_mac_address(input_str:str):
    """
    Validates the input string as a mac address. Valid formats are
    XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXX.XXXX.XXXX
    where 'X' is a hexadecimal digit (upper or lowercase).
    """
    mac = input_str.lower()
    if re.match(r"[0-9a-f]{2}([-:])[0-9a-f]{2}(\1[0-9a-f]{2}){4}$", mac):
        return True
    if re.match(r"[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$", mac):
        return True

    return False


@dataclass(order=True)
class Packet:
    """
    Modeling a packet as it traverses the network
    """

    dst_ip: IPAddress
    #ttl: int = 255
    inner_dst_ip: Optional[IPAddress] = None
    label_stack: Optional[list[int]] = None
    vni: Optional[int] = None

    def __str__(self):
        if self.label_stack:
            return f"MPLS: {self.label_stack}"
        if self.vni:
            return f"VXLAN: {self.dst_ip}:{self.vni}"
        return f"{self.dst_ip}"

    # def decrement_ttl(self):
    #     new_packet = copy(self)
    #     new_packet.ttl -= 1
    #     return new_packet

    def vxlan_encap(self, vni:int, tunnel_destination: ipaddress.IPv4Address) -> "Packet":
        """
        Return a copy of the existing packet, but with a vxlan encap
        """
        if self.vni or self.inner_dst_ip or self.label_stack:
            raise ValueError(f"Can't encapsulate an already-encapsulated packet: {self}")
        
        # new_packet = deepcopy(self)
        # new_packet.inner_dst_ip = self.dst_ip
        # new_packet.vni = vni
        # new_packet.dst_ip = tunnel_destination

        # return new_packet
        self.inner_dst_ip = self.dst_ip
        self.vni = vni
        self.dst_ip = tunnel_destination
    
    def vxlan_decap(self) -> "Packet":
        """
        Return a copy of the existing packet, but with a vxlan decap
        """
        if not self.vni or not self.inner_dst_ip or self.label_stack:
            raise ValueError(f"Can't decap a non-VXLAN packet: {self}")
        
        # new_packet = deepcopy(self)
        # new_packet.dst_ip = self.inner_dst_ip
        # new_packet.vni = None
        # new_packet.inner_dst_ip = None

        # return new_packet
        self.dst_ip = self.inner_dst_ip
        self.vni = None
        self.inner_dst_ip = None

    def mpls_push(self, label:Union[int,list[int]]) -> "Packet":
        """
        Retrun a copy of the existing packet but with MPLS labels pushed on the stack
        """
        if self.vni or self.inner_dst_ip:
            raise ValueError(f"Can't do mpls on a VXLAN packet: {self}")
        
        # new_packet = deepcopy(self)
        # if not new_packet.label_stack:
        #     new_packet.label_stack = []
        
        # if isinstance(label, int):
        #     new_packet.label_stack.append(label)
        # else:
        #     new_packet.label_stack.extend(label)

        # return new_packet
        if not self.label_stack:
            self.label_stack = []
        
        if isinstance(label, list):
            self.label_stack.extend(label)
        else:
            self.label_stack.append(label)

    def mpls_pop(self, num_pops:int=1) -> "Packet":
        """
        Return a copy of the existing packet but with MPLS label(s) popped
        """
        if not self.label_stack:
            raise ValueError(f"Can't pop from an empty label stack!: {self}")
        if len(self.label_stack) < num_pops:
            raise ValueError(f"Can't pop {num_pops} labels from packet: {self}")
        
        # new_packet = copy(self)
        # for _ in range(num_pops):
        #     new_packet.label_stack.pop()

        # return new_packet

        for _ in range(num_pops):
            self.label_stack.pop()


    def mpls_swap(self, label:Union[int,list[int]]) -> "Packet":
        """
        Rerturn a copy of the existing packet but with MPLS label swap
        """
        if not self.label_stack:
            raise ValueError(f"Can't pop from an empty label stack!: {self}")   

        # new_packet = copy(self)
        # new_packet.label_stack.pop()
        # if isinstance(label, int):
        #     new_packet.label_stack.append(label)

        # # inconsistency in mpls table where this really should be a 'pop' but
        # # it shows up as a single blank entry in a list.
        # elif label == [""]:
        #     new_packet.label_stack = []
        # else:
        #     new_packet.label_stack.extend(label)   
        
        # return new_packet
        self.label_stack.pop()
        if label == [""]:
            self.lable_stack = []
        elif isinstance(label, list):
            self.label_stack.extend(label)
        else:
            self.label_stack.append(label)
    
    def is_encapped(self):
        return bool(self.vni or self.label_stack)
        

@dataclass(order=True)
class Hop:
    """
    A hop along the path and the corresponding packet at that location
    """
    router: str
    vrf: str
    interface: str
    packet: Packet

    _parent: "Hop" = field(init=False, compare=False, default=None)
    _children: List["Hop"] = field(init=False, compare=False, default_factory=list)

    def __str__(self):
        vrf = "" if self.vrf == "default" else f" VRF {self.vrf}"
        return f"{self.router}{vrf} {self.interface}, Packet: {self.packet}"

    def copy(self):
        return deepcopy(self)
    
    @classmethod
    def unknown(self, packet=Packet):
        """
        Returns an "unknown" hop for a specific packet
        """
        return Hop("","","", packet)
    
    def is_unknown(self):
        return self.router == ""

    def __hash__(self):
        return(hash(str(self)))
    
    def add_next_hop(self, other:"Hop"):
        """
        creates parent/child relationship between this hop and another one
        """
        self._children.append(other)
        other._parent = self
    


class Path:
    """
    Keeps track of all our paths
    """
    def __init__(self, first_hop:Hop):

        self.first_hop = first_hop
        self.hops = {str(first_hop): first_hop}
    
    def add_hop(self, curr_hop:Hop, next_hop:Hop) -> bool:
        """
        Adds a hop to our current hop. If this is a new hop,
        which means we're on a new path, returns true. Otherwise
        returns false to indicate we don't have to walk this path
        since it's a duplicate of another.
        """

        # if we've seen this hop already we will check for loops.
        if str(next_hop) in self.hops:
            new_path = False

            # parent = self.curr_hop._parent
            # while parent:
            #     if parent == next_hop:
            #         raise ValueError(f"Loop detected for {self.curr_hop} -> {next_hop}")
            #     parent = parent._parent

            self.hops[str(next_hop)]

        else:
            new_path = True
            self.hops[str(next_hop)] = next_hop
            
        curr_hop.add_next_hop(next_hop)
        return new_path
    


    def walk_path(self) -> Dict[int, List[Hop]]:
        """
        'Flattens' path from first hop to last into a dict
        of list of hops keyed on hop number.
        """
        hop_num = 1
        result = { hop_num: {self.first_hop}}
        self._walk_path(self.first_hop, hop_num, result)
        return result
        
            
    def _walk_path(self, curr_hop, hop_num, result):
        hop_num +=1
        for child in curr_hop._children:
            if hop_num not in result:
                result[hop_num] = set()
            result[hop_num].add(child)
            self._walk_path(child, hop_num, result)

 
    def print_path(self):
        """
        Prints out the path, hop by hop
        """
        for hop_num, hops in self.walk_path().items():
            hop_list = list(hops)
            hop_list.sort()
            print(f"***** hop {hop_num} *****")
            for hop in hop_list:
                print(f"\t{hop}")


    def get_path(self) -> list[dict]:
        """
        Returns hops as a list of dicts - for very basic displaying in
        a table. In the future want to beef up the cli script
        so that it can do nested tables, which is really
        what we need for this.
        """
        result = []
        for hop_num, hops in self.walk_path().items():
            hop_list = list(hops)
            hop_list.sort()
            hop_str = "\n".join([str(h) for h in hop_list]) + "\n"              
            result.append({'hop_num':hop_num, 'hops': hop_str})

        return result