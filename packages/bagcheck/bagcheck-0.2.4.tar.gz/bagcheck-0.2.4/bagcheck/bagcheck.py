import os
import yaml
import logging
import rich
import rich.logging
import rich_click as click
from .concourse import cli as concourse
from .github import cli as github

context_settings = dict(help_option_names=['-h', '--help'])

# Setup logger
custom_styles=rich.default_styles.DEFAULT_STYLES
custom_styles["logging.level.debug"] = rich.style.Style(color="cyan")
custom_styles["logging.level.info"] = rich.style.Style(color="green")
custom_styles["logging.level.warning"] = rich.style.Style(color="yellow")
custom_theme = rich.theme.Theme(styles=custom_styles)
custom_console = rich.console.Console(theme=custom_theme)

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[rich.logging.RichHandler(console=custom_console)]
)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3").propagate = False

log = logging.getLogger("rich")

@click.group(context_settings=context_settings)
def cli() -> None:
    pass

@cli.group('concourse', context_settings=context_settings)
def concourse_cli() -> None:
    pass

concourse_cli.add_command(concourse.check)
concourse_cli.add_command(concourse.summarize)

@cli.group('github', context_settings=context_settings)
def github_cli() -> None:
    pass

github_cli.add_command(github.check)
github_cli.add_command(github.summarize)

if __name__ == '__main__':
    cli()
