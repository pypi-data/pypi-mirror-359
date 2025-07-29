import os
import yaml
import logging
import rich_click as click
import bagcheck.concourse.checks as checks
import bagcheck.concourse.summary as summary
import bagcheck.luggage as luggage

context_settings = dict(help_option_names=['-h', '--help'])
log = logging.getLogger("rich")

def perform_checks(doc: str, log: logging.Logger) -> int:
    bagcheck_config = luggage.load_bagcheck_file()

    issue_count = 0
    for test in checks.TEST_MAPPING:
        if not test in bagcheck_config['disable']['global']:
            issue_count += checks.TEST_MAPPING[test](doc, log, bagcheck_config['disable']['local'])
    return issue_count

def perform_summary(doc: str) -> None:
    summary.print_summary(doc)

@click.command(context_settings=context_settings)
@click.option('-f', '--file', 'yaml_path', help="Path to the Concourse pipeline to summarize.")
@click.option('-l', '--log-level', default="INFO", type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], case_sensitive=True), help="Log level to use with this command.")
def summarize(yaml_path: str, log_level: str) -> None:
    log.setLevel(log_level)

    if not os.path.exists(yaml_path):
        log.fatal(f"File does not exist: {yaml_path}")
        exit(1)
    try:
        # Load in the YAML file
        with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
            yaml_data = yaml.load_all(yaml_file, yaml.FullLoader)

            # Summarize each doc
            for doc in yaml_data:
                perform_summary(doc)
    except Exception as e:
        log.fatal(e)

@click.command(context_settings=context_settings)
@click.option('-f', '--file', 'yaml_path', help="Path to the Concourse pipeline to check.")
@click.option('-l', '--log-level', default="INFO", type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'], case_sensitive=True), help="Log level to use with this command.")
def check(yaml_path: str, log_level: str) -> None:
    log.setLevel(log_level)
    issue_count = 0

    # Check if the file exists
    if not os.path.exists(yaml_path):
        log.fatal(f"File does not exist: {yaml_path}")
        exit(1)
    try:
        # Load in the YAML file
        with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
            yaml_data = yaml.load_all(yaml_file, yaml.FullLoader)

            # Check each doc
            for doc in yaml_data:
                issue_count += perform_checks(doc, log)
    except Exception as e:
        log.fatal(e)

    # Print out success or failure
    if issue_count == 0:
        log.info("No issues found")
        exit(0)
    elif issue_count == 1:
        log.error('Found 1 issue')
    else:
        log.error(f"Found {issue_count} issues")
        exit(1)
