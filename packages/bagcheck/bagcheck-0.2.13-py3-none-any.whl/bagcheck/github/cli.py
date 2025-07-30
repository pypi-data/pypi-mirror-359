import os
import yaml
import logging
import rich_click as click
import bagcheck.github.checks as checks
import bagcheck.github.summary as summary
import bagcheck.luggage as luggage

context_settings = dict(help_option_names=['-h', '--help'])
log = logging.getLogger("rich")

def perform_checks(log: logging.Logger, path: str, indent: int=4, max_depth: int=-1) -> None:
    bagcheck_config = luggage.load_bagcheck_file()

    checks.check(log, path, bagcheck_config, indent=indent, max_depth=max_depth)

def perform_summary(log: logging.Logger, path: str, collapse: bool, indent: int=4, max_depth: int=-1) -> None:
    summary.summarize(log, path, collapse=collapse, indent=indent, max_depth=max_depth)

@click.command(context_settings=context_settings)
@click.option('-f', '--file', 'yaml_path', help="Path to the GitHub Actions pipeline to summarize.")
@click.option('-c', '--collapse', default=False, help="Collapse summary to top-level jobs only", is_flag=True)
@click.option('-i', '--indent', 'indent', help="Number of spaces to use for indentation", default=4)
@click.option('-d', '--depth', "depth", help="Max recursion depth to check. Set to -1 to disable", default=-1)
@click.option('-l', '--log-level', default="INFO", type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], case_sensitive=True), help="Log level to use with this command.")
def summarize(yaml_path: str, collapse: bool, indent: int, depth: int, log_level: str) -> None:
    log.setLevel(log_level)

    perform_summary(log, yaml_path, collapse=collapse, indent=indent, max_depth=depth)

@click.command(context_settings=context_settings)
@click.option('-f', '--file', 'yaml_path', help="Path to the GitHub Actions pipeline to check.")
@click.option('-i', '--indent', 'indent', help="Number of spaces to use for indentation", default=4)
@click.option('-d', '--depth', "depth", help="Max recursion depth to check. Set to -1 to disable", default=-1)
@click.option('-l', '--log-level', default="INFO", type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], case_sensitive=True), help="Log level to use with this command.")
def check(yaml_path: str, indent: int, depth: int, log_level: str) -> None:
    log.setLevel(log_level)
    
    perform_checks(log, yaml_path, indent=indent, max_depth=depth)

    
