"""
Pyroform CLI Interface
"""

import click
import json
import yaml
import sys
# import pysnooper

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .src.models import ActionType
from .src.logging import STDOUTMsg
from .pyroform import Pyroform

# GLOBAL

stdout: STDOUTMsg

# GRAFFITTY


def format_banner():
    banner_text = """
    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x

"""
    return banner_text


# @pysnooper.snoop()
def display_banner():
    """Display the Pyroform banner"""
    banner_text = format_banner()
    click.echo(banner_text)


# CLICK


# @pysnooper.snoop()
class BannerCommand(click.Command):

    # @pysnooper.snoop()
    def invoke(self, ctx):
        # Display banner for all commands unless help is being shown
        if not ctx.args or not any(arg in ctx.args for arg in ["--help", "-h"]):
            self._display_banner()
        return super().invoke(ctx)

    # @pysnooper.snoop()
    def get_help(self, ctx):
        """Executed on subcommands"""
        # Display banner before help text
        banner = self._display_banner(return_text=True)
        original_help = super().get_help(ctx)
        return f"{banner}{original_help}"

    # @pysnooper.snoop()
    def _display_banner(self, return_text=False):
        banner_text = format_banner()
        if return_text:
            return banner_text
        click.echo(banner_text)


# @pysnooper.snoop()
class BannerGroup(click.Group):

    # @pysnooper.snoop()
    def _display_banner(self, return_text=False):
        banner_text = format_banner()
        if return_text:
            return banner_text
        click.echo(banner_text)

    # @pysnooper.snoop()
    def format_usage(self, ctx, formatter):
        # Ensure banner is included in main cli usage formatting
        banner_text = self._display_banner(return_text=True)
        formatter.write(banner_text)
        super().format_usage(ctx, formatter)


def display_version(ctx, param, value):
    """Callback function to print version and exit"""
    if not value or ctx.resilient_parsing:
        return
    display_banner()
    try:
        from pyroform import __version__

        click.echo(f"Pyroform version {__version__}")
    except ImportError:
        click.echo("Pyroform version 0.0.0 (unknown)")
    ctx.exit()


@click.group(cls=BannerGroup)
@click.option(
    "--version",
    is_flag=True,
    callback=display_version,
    expose_value=False,
    is_eager=True,
    help="Display PyrDisplay Pyroform  version",
)
def cli():
    """Pyroform Linux Configurator

    A tool that receives input file(s) containing list of users, user groups,
    block storage device mountpoints, files and directories with owners and permissions,
    generates on the fly FlowCTRL sketch files based on input pyro file(s),
    and runs them using the flow_ctrl library.
    """


# ACTION CONFIGURE


@cli.command(cls=BannerCommand)
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(exists=False),
    required=True,
    help="Path to Pyro file (JSON|YAML) or directory containing Pyro files",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(exists=False),
    help="Path to FlowCTRL sketch file (JSON) or directory for generated files",
)
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=click.Path(exists=False),
    help="Path to Pyroform config file (JSON|YAML)",
)
@click.option(
    "-l",
    "--log-file",
    "log_file",
    type=click.Path(exists=False),
    help="Path to Pyroform and FlowCTRL log file",
)
@click.option(
    "-r",
    "--dump-report",
    is_flag=True,
    help="Flag to generate report file with STDOUT, STDERR plus summary",
)
@click.option("-s", "--silent", is_flag=True, help="Flag to suppress STDOUT")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Flag that makes logging and STDOUT messages more verbose",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Flag to confirm all manual prompts such that manual interaction from user is not required",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a trial run without making any changes",
)
#   @common_options
def configure(
    input_path: str,
    output_path: Optional[str],
    config_file: Optional[str],
    log_file: Optional[str],
    dump_report: bool,
    silent: bool,
    debug: bool,
    yes: bool,
    dry_run: bool,
):
    """Configure system according to Pyro file(s)"""
    _execute_action(
        action_type=ActionType.CONFIGURE,
        input_path=Path(input_path) if input_path else None,
        output_path=Path(output_path) if output_path else None,
        config_file=Path(config_file) if config_file else None,
        log_file=Path(log_file) if log_file else None,
        dump_report=dump_report,
        silent=silent,
        debug=debug,
        auto_confirm=yes,
        dry_run=dry_run,
    )


# ACTION SCORCH


@cli.command(cls=BannerCommand)
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(exists=False),
    required=True,
    help="Path to Pyro file (JSON|YAML) or directory containing Pyro files",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(exists=False),
    help="Path to FlowCTRL sketch file (JSON) or directory for generated files",
)
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=click.Path(exists=False),
    help="Path to Pyroform config file (JSON|YAML)",
)
@click.option(
    "-l",
    "--log-file",
    "log_file",
    type=click.Path(exists=False),
    help="Path to Pyroform and FlowCTRL log file",
)
@click.option(
    "-r",
    "--dump-report",
    is_flag=True,
    help="Flag to generate report file with STDOUT, STDERR plus summary",
)
@click.option("-s", "--silent", is_flag=True, help="Flag to suppress STDOUT")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Flag that makes logging and STDOUT messages more verbose",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Flag to confirm all manual prompts such that manual interaction from user is not required",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a trial run without making any changes",
)
#   @common_options
def scorch(
    input_path: str,
    output_path: Optional[str],
    config_file: Optional[str],
    log_file: Optional[str],
    dump_report: bool,
    silent: bool,
    debug: bool,
    yes: bool,
    dry_run: bool,
):
    """Remove system resources not specified in Pyro file(s)"""
    _execute_action(
        action_type=ActionType.SCORCH,
        input_path=Path(input_path) if input_path else None,
        output_path=Path(output_path) if output_path else None,
        config_file=Path(config_file) if config_file else None,
        log_file=Path(log_file) if log_file else None,
        dump_report=dump_report,
        silent=silent,
        debug=debug,
        auto_confirm=yes,
        dry_run=dry_run,
    )


# ACTION MOUNT


@cli.command(cls=BannerCommand)
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(exists=False),
    required=True,
    help="Path to Pyro file (JSON|YAML) or directory containing Pyro files",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(exists=False),
    help="Path to FlowCTRL sketch file (JSON) or directory for generated files",
)
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=click.Path(exists=False),
    help="Path to Pyroform config file (JSON|YAML)",
)
@click.option(
    "-l",
    "--log-file",
    "log_file",
    type=click.Path(exists=False),
    help="Path to Pyroform and FlowCTRL log file",
)
@click.option(
    "-r",
    "--dump-report",
    is_flag=True,
    help="Flag to generate report file with STDOUT, STDERR plus summary",
)
@click.option("-s", "--silent", is_flag=True, help="Flag to suppress STDOUT")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Flag that makes logging and STDOUT messages more verbose",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Flag to confirm all manual prompts such that manual interaction from user is not required",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a trial run without making any changes",
)
#   @common_options
def mount(
    input_path: str,
    output_path: Optional[str],
    config_file: Optional[str],
    log_file: Optional[str],
    dump_report: bool,
    silent: bool,
    debug: bool,
    yes: bool,
    dry_run: bool,
):
    """Mount devices according to Pyro file(s)"""
    _execute_action(
        action_type=ActionType.MOUNT,
        input_path=Path(input_path) if input_path else None,
        output_path=Path(output_path) if output_path else None,
        config_file=Path(config_file) if config_file else None,
        log_file=Path(log_file) if log_file else None,
        dump_report=dump_report,
        silent=silent,
        debug=debug,
        auto_confirm=yes,
        dry_run=dry_run,
    )


# ACTION VALIDATE


@cli.command(cls=BannerCommand)
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(exists=False),
    required=True,
    help="Path to Pyro file (JSON|YAML) or directory containing Pyro files",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(exists=False),
    help="Path to FlowCTRL sketch file (JSON) or directory for generated files",
)
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=click.Path(exists=False),
    help="Path to Pyroform config file (JSON|YAML)",
)
@click.option(
    "-l",
    "--log-file",
    "log_file",
    type=click.Path(exists=False),
    help="Path to Pyroform and FlowCTRL log file",
)
@click.option(
    "-r",
    "--dump-report",
    is_flag=True,
    help="Flag to generate report file with STDOUT, STDERR plus summary",
)
@click.option("-s", "--silent", is_flag=True, help="Flag to suppress STDOUT")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Flag that makes logging and STDOUT messages more verbose",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Flag to confirm all manual prompts such that manual interaction from user is not required",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a trial run without making any changes",
)
#   @common_options
def validate(
    input_path: str,
    output_path: Optional[str],
    config_file: Optional[str],
    log_file: Optional[str],
    dump_report: bool,
    silent: bool,
    debug: bool,
    yes: bool,
    dry_run: bool,
):
    """Validate system against Pyro file(s)"""
    _execute_action(
        action_type=ActionType.VALIDATE,
        input_path=Path(input_path) if input_path else None,
        output_path=Path(output_path) if output_path else None,
        config_file=Path(config_file) if config_file else None,
        log_file=Path(log_file) if log_file else None,
        dump_report=dump_report,
        silent=silent,
        debug=debug,
        auto_confirm=yes,
        dry_run=dry_run,
    )


# ACTION SNAPSHOT


@cli.command(cls=BannerCommand)
@click.option(
    "-i",
    "--input",
    "input_path",
    type=click.Path(exists=False),
    help="Path to Pyro file (JSON|YAML) or directory containing Pyro files",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    type=click.Path(exists=False),
    help="Path to FlowCTRL sketch file (JSON) or directory for generated files",
)
@click.option(
    "-c",
    "--config-file",
    "config_file",
    type=click.Path(exists=False),
    help="Path to Pyroform config file (JSON|YAML)",
)
@click.option(
    "-l",
    "--log-file",
    "log_file",
    type=click.Path(exists=False),
    help="Path to Pyroform and FlowCTRL log file",
)
@click.option(
    "-r",
    "--dump-report",
    is_flag=True,
    help="Flag to generate report file with STDOUT, STDERR plus summary",
)
@click.option("-s", "--silent", is_flag=True, help="Flag to suppress STDOUT")
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Flag that makes logging and STDOUT messages more verbose",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Flag to confirm all manual prompts such that manual interaction from user is not required",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a trial run without making any changes",
)
#   @common_options
def snapshot(
    input_path: Optional[str],
    output_path: Optional[str],
    config_file: Optional[str],
    log_file: Optional[str],
    dump_report: bool,
    silent: bool,
    debug: bool,
    yes: bool,
    dry_run: bool,
):
    """Validate system against Pyro file(s)"""
    _execute_action(
        action_type=ActionType.SNAPSHOT,
        input_path=Path(input_path) if input_path else None,
        output_path=Path(output_path) if output_path else None,
        config_file=Path(config_file) if config_file else None,
        log_file=Path(log_file) if log_file else None,
        dump_report=dump_report,
        silent=silent,
        debug=debug,
        auto_confirm=yes,
    )


# COMPOSED ACTION WORKFLOW


@cli.command(cls=BannerCommand)
@click.option(
    "-w",
    "--workflow-file",
    "workflow_file",
    type=click.Path(exists=True),
    required=True,
    help="Path to workflow configuration file (JSON/YAML)",
)
def workflow(workflow_file: str):
    """
    Execute a complete Pyroform workflow from configuration file
    """
    # NOTE: Banner is automatically displayed by BannerCommand before this function runs
    workflow_path = Path(workflow_file)

    if not workflow_path.exists():
        raise click.UsageError(f"Workflow file not found: {workflow_file}")

    try:
        if workflow_path.suffix.lower() in [".yaml", ".yml"]:
            with open(workflow_path, "r") as f:
                workflow_config = yaml.safe_load(f)
        elif workflow_path.suffix.lower() == ".json":
            with open(workflow_path, "r") as f:
                workflow_config = json.load(f)
        else:
            raise click.UsageError(
                f"Unsupported workflow file format: {workflow_path.suffix}"
            )

        success = execute_workflow(workflow_config)
        exit(0 if success else 1)

    except Exception as e:
        click.echo(f"[ ERROR ]: Error executing workflow: {e}")
        exit(1)


# UTILS


# @pysnooper.snoop()
def _get_action_type(
    scorch: bool, mount: bool, configure: bool, validate: bool, snapshot: bool
) -> ActionType:
    """Determine action type from CLI flags"""
    if scorch:
        return ActionType.SCORCH
    elif mount:
        return ActionType.MOUNT
    elif configure:
        return ActionType.CONFIGURE
    elif validate:
        return ActionType.VALIDATE
    elif snapshot:
        return ActionType.SNAPSHOT
    else:
        raise ValueError("No action specified")


# @pysnooper.snoop()
def _execute_action(
    action_type: ActionType,
    input_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    config_file: Optional[Path] = None,
    log_file: Optional[Path] = None,
    dump_report: bool = None,
    silent: bool = None,
    debug: bool = None,
    auto_confirm: bool = None,
    dry_run: bool = None,
):
    """
    Execute the specified action with given parameters

    Args:
        action_type: Type of action to perform
        input_path: Path to input Pyro file(s)
        output_path: Path for output files (optional)
        config_file: Path to config file (optional)
        log_file: Path to log file (optional)
        dump_report: Whether to generate report
        silent: Whether to suppress STDOUT
        debug: Whether to enable debug mode
        auto_confirm: Whether to auto-confirm prompts
    """
    stdout = STDOUTMsg(debug_mode=debug)
    start_time = datetime.now().isoformat()
    stdout.debug(f"Exec start timestamp: {start_time}")

    try:
        # Initialize Pyroform with configuration
        pyroform_kwargs = {
            "input_path": input_path,
            "output_path": output_path,
            "log_file": log_file,
            "auto_confirm": auto_confirm,
            "dry_run": dry_run,
            "debug": debug,
            "silent": silent,
            "report": dump_report,
        }

        stdout.debug(f"Pyroform kwargs - {pyroform_kwargs}")

        pf = Pyroform(
            config_file, **{k: v for k, v in pyroform_kwargs.items() if v != None}
        )

        # Execute the action
        if action_type == ActionType.CONFIGURE:
            result = pf.configure(str(input_path))
            success = result.success
        elif action_type == ActionType.SCORCH:
            result = pf.scorch(str(input_path))
            success = result.success
        elif action_type == ActionType.MOUNT:
            result = pf.mount(str(input_path))
            success = result.success
        elif action_type == ActionType.VALIDATE:
            result = pf.validate(str(input_path))
            success = result.success
        elif action_type == ActionType.SNAPSHOT:
            result = pf.snapshot(str(output_path))
            success = result.success
        else:
            raise ValueError(f"Unsupported action type: {action_type}")

    except Exception as e:
        import traceback

        stdout.debug(traceback.format_exc())


# @pysnooper.snoop()
def execute_workflow(workflow_config: Dict[str, Any]) -> bool:
    """
    Execute a complete Pyroform workflow

    Args:
        workflow_config: Workflow configuration dictionary

    Returns:
        True if workflow completed successfully, False otherwise
    """
    stdout = STDOUTMsg(debug_mode=workflow_config.get("debug", False))
    try:
        steps = workflow_config.get("steps", [])
        stdout.debug(f"Workflow steps: {steps}")

        auto_confirm = workflow_config.get("auto_confirm", False)

        pf = Pyroform(
            config_file=workflow_config.get("config_file"),
            log_file=workflow_config.get("log_config"),
            debug=workflow_config.get("debug", False),
            auto_confirm=auto_confirm,
        )

        result = pf.execute_workflow(steps)

    except Exception as e:
        stdout.err(f"Workflow execution failed: {e}")
        import traceback

        stdout.debug(traceback.format_exc())
        return False


# Allow running as script
if __name__ == "__main__":
    cli()

# CODE DUMP

# TODO - Currently broken. Pick up when cleaning CLI interface code
#   def common_options(func):
#       """Decorator for common command options."""
#       options = [
#           click.option(
#               "-i", "--input", "input_path",
#               type=click.Path(exists=False),
#               required=False,
#               help="Path to Pyro file (JSON|YAML) or directory containing Pyro files"
#           ),
#           click.option(
#               "-o", "--output", "output_path",
#               type=click.Path(exists=False),
#               help="Path to FlowCTRL sketch file (JSON) or directory for generated files"
#           ),
#           click.option(
#               "-c", "--config-file", "config_file",
#               type=click.Path(exists=False),
#               help="Path to Pyroform config file (JSON|YAML)"
#           ),
#           click.option(
#               "-l", "--log-file", "log_file",
#               type=click.Path(exists=False),
#               help="Path to Pyroform and FlowCTRL log file"
#           ),
#           click.option(
#               "-r", "--dump-report",
#               is_flag=True,
#               help="Generate report file with STDOUT, STDERR plus summary"
#           ),
#           click.option(
#               "-s", "--silent",
#               is_flag=True,
#               help="Suppress STDOUT output"
#           ),
#           click.option(
#               "-d", "--debug",
#               is_flag=True,
#               help="Enable verbose logging and debug messages"
#           ),
#           click.option(
#               "-y", "--yes",
#               is_flag=True,
#               help="Auto-confirm all prompts without user interaction"
#           ),
#           click.option(
#               "--dry-run",
#               is_flag=True,
#               help="Perform trial run without making changes"
#           )
#       ]

#       for option in options: #reversed(options):
#           func = option(func)
#       return func
