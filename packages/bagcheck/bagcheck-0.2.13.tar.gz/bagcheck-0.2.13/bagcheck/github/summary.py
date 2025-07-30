import rich
from bagcheck.github.workflow import build_tree
from bagcheck.github.triggers import format_triggers
from rich.spinner import Spinner
import logging
from pprint import pprint
from bagcheck.github.constants import *

def __print_summary__(log: logging.Logger, node: dict=None, collapse: bool = False, indent: int=4, max_depth: int=-1, depth: int=0):
    if not node:
        return
    log.debug(node)
    rich.print(f'{" " * indent * depth}- [bold blue]{node["name"]}[/bold blue]')
    if max_depth == -1 or depth < max_depth:
        if node['kind'] == GH_KIND_JOB:
            if len(node['children']) == 1:
                if node['children'][0]['kind'] == GH_KIND_WORKFLOW:
                    rich.print(f'{" " * indent * (depth+1)}[bold yellow]Workflows[/bold yellow]')
                    __print_summary__(log, node=node['children'][0], collapse=collapse, indent=indent, max_depth=max_depth, depth=depth+1)
                    return
            rich.print(f'{" " * indent * (depth+1)}[bold yellow]Steps[/bold yellow]')
            for child in node['children']:
                __print_summary__(log, node=child, collapse=collapse, indent=indent, max_depth=max_depth, depth=depth+1)
        elif node['kind'] == GH_KIND_WORKFLOW:
            rich.print(f'{" " * indent * (depth+1)}[bold yellow]Jobs[/bold yellow]')
            for child in node['children']:
                __print_summary__(log, node=child, collapse=collapse, indent=indent, max_depth=max_depth, depth=depth+1)
        elif node['kind'] == GH_KIND_ACTION:
            rich.print(f'{" " * indent * (depth+1)}[bold yellow]Steps[/bold yellow]')
            for child in node['children']:
                __print_summary__(log, node=child, collapse=collapse, indent=indent, max_depth=max_depth, depth=depth+1)

def summarize(log: logging.Logger, path: str, collapse: bool=False, indent: int=4, max_depth: int=-1) -> None:
    for root in build_tree(log, path, indent=indent, max_depth=max_depth):
        summary_tree = root.get_summary()

        if root.kind == GH_KIND_WORKFLOW:
            rich.print(f'[bold yellow]Workflows[/bold yellow]')
        elif root.kind == GH_KIND_JOB:
            rich.print(f'[bold yellow]Jobs[/bold yellow]')

        __print_summary__(log, node=summary_tree, collapse=collapse, indent=indent, max_depth=max_depth)

