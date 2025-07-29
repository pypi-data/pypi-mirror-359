import typer
from umnetdb_utils import UMnetdb
import inspect
from functools import wraps

from rich.console import Console
from rich.table import Table

from typing import Callable, List
from typing_extensions import Annotated

app = typer.Typer()

def print_result(result:List[dict]):
    """
    Takes the result of a umnetdb call and prints it as a table
    """
    if len(result) == 0:
        print("No results found")
        return
    
    if isinstance(result, dict):
        result = [result]
        
    # instantiate table with columns based on entry dict keys
    table = Table(*result[0].keys())
    for row in result:
        table.add_row(*[str(i) for i in row.values()])

    console = Console()
    console.print(table)
    

def command_generator(method_name:str, method:Callable):
    """
    Generates a typer command function for an arbitrary method
    in the umnetdb class. The generated function opens a connection with 
    the database, executes the method, and prints out the results.

    Note that the docstring of each method is interrogated to generate
    help text for each typer command.

    :method_name: The name of the method
    :method: The method itself
    """

    # first we're going to tease out the 'help' portions of the method
    # from the docstring.
    docstr = method.__doc__
    docstr_parts = docstr.split("\n:")

    # first section of the docstring is always a generic 'this is what the method does'.
    cmd_help = docstr_parts.pop(0)

    # next sections are details on the specific arguments that we want to pass to typer as
    # special annotated type hints
    arg_help = {}
    for arg_str in docstr_parts:
        if ":" in arg_str:
            arg, help = arg_str.split(":")
            arg_help[arg] = help.strip()
        
    sig = inspect.signature(method)

    # going through the method's arguments and augmenting the 'help' section for each one
    # from the docstring if applicable
    new_params = []
    for p_name, p in sig.parameters.items():

        # need to skip self
        if p_name == "self":
            continue

        # if there wasn't any helper text then just append the parameter as is
        if p_name not in arg_help:
            new_params.append(p)
            continue

        # params without default values should be typer 'arguments'
        if p.default == inspect._empty:
            new_params.append(p.replace(annotation=Annotated[p.annotation, typer.Argument(help=arg_help[p_name])]))
            continue

        # params with default values should be typer 'options'
        new_params.append(p.replace(annotation=Annotated[p.annotation, typer.Option(help=arg_help[p_name])]))

    new_sig = sig.replace(parameters=new_params)


    # new munged function based on the origional method, with a new signature
    # and docstring for typer
    @wraps(method)
    def wrapper(*args, **kwargs):
        with UMnetdb() as db:
            result = getattr(db, method_name)(*args, **kwargs)
        print_result(result)
    
    wrapper.__signature__ = new_sig
    wrapper.__doc__ = cmd_help

    return wrapper


def main():
    for f_name,f in UMnetdb.__dict__.items():
        if not(f_name.startswith("_")) and callable(f):
            app.command()(command_generator(f_name, f))

    app()

if __name__ == "__main__":
    main()

    
