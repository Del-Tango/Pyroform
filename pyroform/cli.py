"""
Pyroform CLI Interface
"""

import click
import json
import yaml
import sys

import pysnooper

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .src.models import ActionType
from .src.logging import STDOUTMsg
from .pyroform import Pyroform

# GLOBAL

stdout = STDOUTMsg(debug_mode=True)

# GRAFFITTY

def format_banner():
    banner_text = """
    ___________________________________________________________________________

    *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x

"""
    return banner_text


# #@pysnooper.snoop()
def display_banner():
    """Display the Pyroform banner"""
    banner_text = format_banner()
    click.echo(banner_text)

# CLICK

##@pysnooper.snoop()
class BannerCommand(click.Command):

#   #@pysnooper.snoop()
    def invoke(self, ctx):
        # Display banner for all commands unless help is being shown
        if not ctx.args or not any(arg in ctx.args for arg in ['--help', '-h']):
            self._display_banner()
        return super().invoke(ctx)

#   #@pysnooper.snoop()
    def get_help(self, ctx):
        '''Executed on subcommands'''
        # Display banner before help text
        banner = self._display_banner(return_text=True)
        original_help = super().get_help(ctx)
        return f"{banner}{original_help}"

#   #@pysnooper.snoop()
    def _display_banner(self, return_text=False):
        banner_text = format_banner()
        if return_text:
            return banner_text
        click.echo(banner_text)


# #@pysnooper.snoop()
class BannerGroup(click.Group):

#   #@pysnooper.snoop()
    def _display_banner(self, return_text=False):
        banner_text = format_banner()
        if return_text:
            return banner_text
        click.echo(banner_text)

#   #@pysnooper.snoop()
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
    '--version',
    is_flag=True,
    callback=display_version,
    expose_value=False,
    is_eager=True,
    help='Display PyrDisplay Pyroform  version'
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
#   @cli.command(cls=BannerCommand)
#   @common_options
def configure(input_path: str, output_path: Optional[str], config_file: Optional[str],
            log_file: Optional[str], dump_report: bool, silent: bool, debug: bool,
            yes: bool, dry_run: bool):
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
#   @cli.command(cls=BannerCommand)
#   @common_options
def scorch(input_path: str, output_path: Optional[str], config_file: Optional[str],
        log_file: Optional[str], dump_report: bool, silent: bool, debug: bool,
        yes: bool, dry_run: bool):
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
#   @cli.command(cls=BannerCommand)
#   @common_options
def mount(input_path: str, output_path: Optional[str], config_file: Optional[str],
        log_file: Optional[str], dump_report: bool, silent: bool, debug: bool,
        yes: bool, dry_run: bool):
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
#   @cli.command(cls=BannerCommand)
#   @common_options
def validate(input_path: str, output_path: Optional[str], config_file: Optional[str],
            log_file: Optional[str], dump_report: bool, silent: bool, debug: bool,
            yes: bool, dry_run: bool):
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
#   @cli.command(cls=BannerCommand)
#   @common_options
def snapshot(input_path: Optional[str], output_path: Optional[str], config_file: Optional[str],
            log_file: Optional[str], dump_report: bool, silent: bool, debug: bool,
            yes: bool, dry_run: bool):
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
    # Banner is automatically displayed by BannerCommand before this function runs

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
        click.echo(f"Error executing workflow: {e}")
        exit(1)

# UTILS

#@pysnooper.snoop()
def _get_action_type(
    scorch: bool, mount: bool, configure: bool, validate: bool
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
    else:
        raise ValueError("No action specified")

#@pysnooper.snoop()
def _execute_action(
    action_type: ActionType,
    input_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
    config_file: Optional[Path] = None,
    log_file: Optional[Path] = None,
    dump_report: bool = False,
    silent: bool = False,
    debug: bool = False,
    auto_confirm: bool = False,
    dry_run: bool = False,
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
    start_time = datetime.now().isoformat()

    try:
        # Initialize Pyroform with configuration
        pyroform_kwargs = {
            "auto_confirm": auto_confirm,
            'dry_run': dry_run,
            'debug': debug,
            'silent': silent,
            'dump_report': dump_report,
        }
        if config_file and config_file.exists():
            pyroform_kwargs["config_file"] = str(config_file)


        stdout.debug(f'Pyroform kwargs - {pyroform_kwargs}')

        pf = Pyroform(**pyroform_kwargs)

        # Prepare kwargs for the action
        action_kwargs = {}
        if output_path:
            action_kwargs["output_dir"] = str(output_path)
        if debug:
            action_kwargs["verbose"] = True
        if dry_run:
            action_kwargs['dry_run'] = True

        # Execute the action
        if action_type == ActionType.CONFIGURE:
            result = pf.configure(str(input_path), **action_kwargs)
            success = result
        elif action_type == ActionType.SCORCH:
            result = pf.scorch(str(input_path), **action_kwargs)
            success = result
        elif action_type == ActionType.MOUNT:
            # TODO - take into account dry run
            result = pf.mount(str(input_path), **action_kwargs)
            success = result
        elif action_type == ActionType.VALIDATE:
            result = pf.validate(str(input_path), **action_kwargs)
            success = result.is_valid
        elif action_type == ActionType.SNAPSHOT:
            result = pf.snapshot(str(output_path), **action_kwargs)
            success = result.is_valid
        else:
            raise ValueError(f"Unsupported action type: {action_type}")

        # Store result for reporting
        pf._last_action = action_type
        pf._last_result = result

        # Generate report if requested
        if dump_report:
            end_time = datetime.now().isoformat()

            if output_path:
                if output_path.is_dir():
                    report_file = (
                        output_path / f"pyroform_report_{action_type.value}.json"
                    )
                else:
                    report_file = output_path
            else:
                report_file = Path(f"pyroform_report_{action_type.value}.json")

            report_success = pf.generate_report(str(report_file))

            if not silent:
                if report_success:
                    click.echo(f"Report saved to: {report_file}")
                else:
                    click.echo(f"Failed to save report to: {report_file}")

    except Exception as e:
        if debug:
            import traceback

            click.echo(traceback.format_exc())

#@pysnooper.snoop()
def execute_workflow(workflow_config: Dict[str, Any]) -> bool:
    """
    Execute a complete Pyroform workflow

    Args:
        workflow_config: Workflow configuration dictionary

    Returns:
        True if workflow completed successfully, False otherwise
    """
    try:
        steps = workflow_config.get("steps", [])
        auto_confirm = workflow_config.get("auto_confirm", False)
        config_file = workflow_config.get("config_file")

        pf = Pyroform(config_file=config_file, auto_confirm=auto_confirm)

        workflow_results = []

        for step in steps:
            action = step.get("action")
            input_path = step.get("input_path")
            dry_run = step.get("dry_run", False)

            if not action or not input_path:
                click.echo(f"Invalid workflow step: {step}")
                return False

            try:
                if action == "validate":
                    result = pf.validate(input_path, dry_run=dry_run)
                    success = result.is_valid
                elif action == "configure":
                    result = pf.configure(input_path, dry_run=dry_run)
                    success = result
                elif action == "mount":
                    result = pf.mount(input_path, dry_run=dry_run)
                    success = result
                elif action == "scorch":
                    result = pf.scorch(input_path, dry_run=dry_run)
                    success = result.success
                else:
                    click.echo(f"Unknown action in workflow: {action}")
                    return False

                workflow_results.append(
                    {
                        "action": action,
                        "input_path": input_path,
                        "success": success,
                        "result": result,
                    }
                )

                if not success:
                    return False

            except Exception as e:
                click.echo(f"Error in workflow step {action}: {e}")
                return False

        # Generate workflow report
        if workflow_config.get("generate_report", True):
            report_file = workflow_config.get(
                "report_file", "pyroform_workflow_report.json"
            )
            pf._generate_workflow_report(workflow_results, report_file)

        click.echo("Workflow completed successfully")
        return True

    except Exception as e:
        click.echo(f"Workflow execution failed: {e}")
        return False


# Allow running as script
if __name__ == "__main__":
    cli()

# CODE DUMP


# TODO - Common option decorators for command consistency
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




#   """
#   Pyroform CLI Interface

#   A comprehensive command-line interface for Pyroform Linux Configurator that manages
#   system configuration through declarative Pyro files. Supports end-to-end workflows
#   for system configuration, validation, and resource management.

#   Key Features:
#   - Configuration management via Pyro files (JSON/YAML)
#   - System validation and snapshot capabilities
#   - Dry-run and auto-confirmation modes
#   - Comprehensive reporting and logging
#   - Workflow execution from configuration files

#   Author: Alveare Solutions
#   Version: 1.0.0
#   """

#   import json
#   import sys
#   import click
#   import yaml
#   from pathlib import Path
#   from typing import Optional, Dict, Any, List
#   from datetime import datetime

#   from .src.models import ActionType
#   from .src.logging import STDOUTMsg
#   from .pyroform import Pyroform


#   class PyroformCLI:
#       """Main CLI handler for Pyroform operations."""

#       def __init__(self):
#           self.stdout = STDOUTMsg(debug_mode=True)
#           self.start_time = None

#       # Banner Management
#       @staticmethod
#       def format_banner() -> str:
#           """
#           Create the Pyroform banner text.

#           Returns:
#               Formatted banner string
#           """
#           return """
#       ___________________________________________________________________________

#       *                          *   Pyroform   *                           *
#       ___________________________________________________________________________
#                       Regards, the Alveare Solutions #!/Society -x

#   """

#       @classmethod
#       def display_banner(cls) -> None:
#           """Display the Pyroform banner to stdout."""
#           click.echo(cls.format_banner())


#   class BannerCommand(click.Command):
#       """Click command that displays banner before execution."""

#       def invoke(self, ctx: click.Context) -> Any:
#           """Invoke command with banner display."""
#           if not self._is_help_requested(ctx):
#               PyroformCLI.display_banner()
#           return super().invoke(ctx)

#       def get_help(self, ctx: click.Context) -> str:
#           """Get help text with banner."""
#           banner = PyroformCLI.format_banner()
#           original_help = super().get_help(ctx)
#           return f"{banner}{original_help}"

#       @staticmethod
#       def _is_help_requested(ctx: click.Context) -> bool:
#           """Check if help was requested in command arguments."""
#           return any(arg in ctx.args for arg in ['--help', '-h']) if ctx.args else False


#   class BannerGroup(click.Group):
#       """Click group that includes banner in usage formatting."""

#       def format_usage(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
#           """Format usage with banner."""
#           banner_text = PyroformCLI.format_banner()
#           formatter.write(banner_text)
#           super().format_usage(ctx, formatter)


#   def display_version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
#       """
#       Callback function to display version information.

#       Args:
#           ctx: Click context
#           param: Click parameter
#           value: Flag value
#       """
#       if not value or ctx.resilient_parsing:
#           return

#       PyroformCLI.display_banner()
#       try:
#           from pyroform import __version__
#           click.echo(f"Pyroform version {__version__}")
#       except ImportError:
#           click.echo("Pyroform version 0.0.0 (unknown)")
#       ctx.exit()


#   # Common option decorators for command consistency
#   def common_options(func):
#       """Decorator for common command options."""
#       options = [
#           click.option(
#               "-i", "--input", "input_path",
#               type=click.Path(exists=False),
#               required=True,
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

#       for option in reversed(options):
#           func = option(func)
#       return func


#   @click.group(cls=BannerGroup)
#   @click.option(
#       '--version',
#       is_flag=True,
#       callback=display_version,
#       expose_value=False,
#       is_eager=True,
#       help='Display Pyroform version information'
#   )
#   def cli() -> None:
#       """
#       Pyroform Linux Configurator

#       A declarative system configuration tool that processes Pyro files to manage:
#       - User and group configurations
#       - Filesystem permissions and ownership
#       - Block storage device mountpoints
#       - System resource validation

#       The tool generates FlowCTRL sketch files from Pyro configuration files
#       and executes them using the flow_ctrl library for reliable system management.
#       """


#   @cli.command(cls=BannerCommand)
#   @common_options
#   def configure(
#       input_path: str,
#       output_path: Optional[str],
#       config_file: Optional[str],
#       log_file: Optional[str],
#       dump_report: bool,
#       silent: bool,
#       debug: bool,
#       yes: bool,
#       dry_run: bool
#   ) -> None:
#       """
#       Configure system according to Pyro file specifications.

#       Applies the configuration defined in Pyro files to the system, creating
#       users, groups, setting permissions, and configuring mountpoints as specified.

#       Example:
#           pyroform configure -i config.yaml -o output/ --dry-run
#       """
#       _execute_action(
#           action_type=ActionType.CONFIGURE,
#           input_path=Path(input_path) if input_path else None,
#           output_path=Path(output_path) if output_path else None,
#           config_file=Path(config_file) if config_file else None,
#           log_file=Path(log_file) if log_file else None,
#           dump_report=dump_report,
#           silent=silent,
#           debug=debug,
#           auto_confirm=yes,
#           dry_run=dry_run,
#       )


#   @cli.command(cls=BannerCommand)
#   @common_options
#   def scorch(
#       input_path: str,
#       output_path: Optional[str],
#       config_file: Optional[str],
#       log_file: Optional[str],
#       dump_report: bool,
#       silent: bool,
#       debug: bool,
#       yes: bool,
#       dry_run: bool
#   ) -> None:
#       """
#       Remove system resources not specified in Pyro files.

#       Performs cleanup of users, groups, and configurations that exist on the
#       system but are not declared in the provided Pyro files.

#       WARNING: This operation can be destructive. Use --dry-run to preview changes.

#       Example:
#           pyroform scorch -i config.yaml --dry-run -y
#       """
#       _execute_action(
#           action_type=ActionType.SCORCH,
#           input_path=Path(input_path) if input_path else None,
#           output_path=Path(output_path) if output_path else None,
#           config_file=Path(config_file) if config_file else None,
#           log_file=Path(log_file) if log_file else None,
#           dump_report=dump_report,
#           silent=silent,
#           debug=debug,
#           auto_confirm=yes,
#           dry_run=dry_run,
#       )


#   @cli.command(cls=BannerCommand)
#   @common_options
#   def mount(
#       input_path: str,
#       output_path: Optional[str],
#       config_file: Optional[str],
#       log_file: Optional[str],
#       dump_report: bool,
#       silent: bool,
#       debug: bool,
#       yes: bool,
#       dry_run: bool
#   ) -> None:
#       """
#       Mount block storage devices according to Pyro file specifications.

#       Configures and mounts storage devices based on the mountpoint definitions
#       in the provided Pyro files.

#       Example:
#           pyroform mount -i storage.yaml -o mounts/
#       """
#       _execute_action(
#           action_type=ActionType.MOUNT,
#           input_path=Path(input_path) if input_path else None,
#           output_path=Path(output_path) if output_path else None,
#           config_file=Path(config_file) if config_file else None,
#           log_file=Path(log_file) if log_file else None,
#           dump_report=dump_report,
#           silent=silent,
#           debug=debug,
#           auto_confirm=yes,
#           dry_run=dry_run,
#       )


#   @cli.command(cls=BannerCommand)
#   @common_options
#   def validate(
#       input_path: str,
#       output_path: Optional[str],
#       config_file: Optional[str],
#       log_file: Optional[str],
#       dump_report: bool,
#       silent: bool,
#       debug: bool,
#       yes: bool,
#       dry_run: bool
#   ) -> None:
#       """
#       Validate system configuration against Pyro file specifications.

#       Compares the current system state with the desired state defined in Pyro files
#       and reports any discrepancies without making changes.

#       Example:
#           pyroform validate -i config.yaml -r --debug
#       """
#       _execute_action(
#           action_type=ActionType.VALIDATE,
#           input_path=Path(input_path) if input_path else None,
#           output_path=Path(output_path) if output_path else None,
#           config_file=Path(config_file) if config_file else None,
#           log_file=Path(log_file) if log_file else None,
#           dump_report=dump_report,
#           silent=silent,
#           debug=debug,
#           auto_confirm=yes,
#           dry_run=dry_run,
#       )


#   @cli.command(cls=BannerCommand)
#   @click.option(
#       "-i", "--input", "input_path",
#       type=click.Path(exists=False),
#       help="Path to Pyro file (JSON|YAML) or directory containing Pyro files"
#   )
#   @click.option(
#       "-o", "--output", "output_path",
#       type=click.Path(exists=False),
#       help="Path to FlowCTRL sketch file (JSON) or directory for generated files"
#   )
#   @click.option(
#       "-c", "--config-file", "config_file",
#       type=click.Path(exists=False),
#       help="Path to Pyroform config file (JSON|YAML)"
#   )
#   @click.option(
#       "-l", "--log-file", "log_file",
#       type=click.Path(exists=False),
#       help="Path to Pyroform and FlowCTRL log file"
#   )
#   @click.option(
#       "-r", "--dump-report",
#       is_flag=True,
#       help="Generate report file with STDOUT, STDERR plus summary"
#   )
#   @click.option(
#       "-s", "--silent",
#       is_flag=True,
#       help="Suppress STDOUT output"
#   )
#   @click.option(
#       "-d", "--debug",
#       is_flag=True,
#       help="Enable verbose logging and debug messages"
#   )
#   @click.option(
#       "-y", "--yes",
#       is_flag=True,
#       help="Auto-confirm all prompts without user interaction"
#   )
#   def snapshot(
#       input_path: Optional[str],
#       output_path: Optional[str],
#       config_file: Optional[str],
#       log_file: Optional[str],
#       dump_report: bool,
#       silent: bool,
#       debug: bool,
#       yes: bool
#   ) -> None:
#       """
#       Capture current system state as Pyro configuration.

#       Creates a snapshot of the current system configuration including users,
#       groups, permissions, and mountpoints in Pyro file format.

#       Example:
#           pyroform snapshot -o system_snapshot.yaml
#       """
#       _execute_action(
#           action_type=ActionType.SNAPSHOT,
#           input_path=Path(input_path) if input_path else None,
#           output_path=Path(output_path) if output_path else None,
#           config_file=Path(config_file) if config_file else None,
#           log_file=Path(log_file) if log_file else None,
#           dump_report=dump_report,
#           silent=silent,
#           debug=debug,
#           auto_confirm=yes,
#       )


#   @cli.command(cls=BannerCommand)
#   @click.option(
#       "-w", "--workflow-file", "workflow_file",
#       type=click.Path(exists=True),
#       required=True,
#       help="Path to workflow configuration file (JSON/YAML)"
#   )
#   def workflow(workflow_file: str) -> None:
#       """
#       Execute a complete Pyroform workflow from configuration file.

#       Runs a sequence of Pyroform actions defined in a workflow configuration file.
#       Supports complex multi-step operations with conditional execution.

#       Example workflow configuration:
#           steps:
#           - action: validate
#               input_path: config.yaml
#           - action: configure
#               input_path: config.yaml
#           - action: mount
#               input_path: storage.yaml

#       Example:
#           pyroform workflow -w deployment.yaml
#       """
#       workflow_path = Path(workflow_file)

#       if not workflow_path.exists():
#           raise click.UsageError(f"Workflow file not found: {workflow_file}")

#       try:
#           workflow_config = _load_workflow_config(workflow_path)
#           success = execute_workflow(workflow_config)
#           sys.exit(0 if success else 1)

#       except Exception as e:
#           click.echo(f"Error executing workflow: {e}", err=True)
#           sys.exit(1)


#   def _load_workflow_config(workflow_path: Path) -> Dict[str, Any]:
#       """
#       Load workflow configuration from file.

#       Args:
#           workflow_path: Path to workflow configuration file

#       Returns:
#           Parsed workflow configuration

#       Raises:
#           click.UsageError: For unsupported file formats or parse errors
#       """
#       suffix = workflow_path.suffix.lower()

#       try:
#           with open(workflow_path, "r") as f:
#               if suffix in [".yaml", ".yml"]:
#                   return yaml.safe_load(f)
#               elif suffix == ".json":
#                   return json.load(f)
#               else:
#                   raise click.UsageError(f"Unsupported workflow file format: {suffix}")
#       except (yaml.YAMLError, json.JSONDecodeError) as e:
#           raise click.UsageError(f"Invalid workflow file format: {e}")


#   def _execute_action(
#       action_type: ActionType,
#       input_path: Optional[Path] = None,
#       output_path: Optional[Path] = None,
#       config_file: Optional[Path] = None,
#       log_file: Optional[Path] = None,
#       dump_report: bool = False,
#       silent: bool = False,
#       debug: bool = False,
#       auto_confirm: bool = False,
#       dry_run: bool = False,
#   ) -> None:
#       """
#       Execute Pyroform action with standardized error handling and reporting.

#       Args:
#           action_type: Type of action to perform
#           input_path: Path to input Pyro file(s)
#           output_path: Path for output files
#           config_file: Path to configuration file
#           log_file: Path to log file
#           dump_report: Whether to generate execution report
#           silent: Whether to suppress stdout output
#           debug: Whether to enable debug mode
#           auto_confirm: Whether to auto-confirm prompts
#           dry_run: Whether to perform dry run without changes
#       """
#       start_time = datetime.now().isoformat()
#       cli_handler = PyroformCLI()

#       try:
#           # Initialize Pyroform instance
#           pyroform_kwargs = _build_pyroform_kwargs(
#               config_file=config_file,
#               auto_confirm=auto_confirm,
#               dry_run=dry_run,
#               debug=debug,
#               silent=silent,
#               dump_report=dump_report,
#           )

#           cli_handler.stdout.debug(f'Pyroform initialization kwargs: {pyroform_kwargs}')
#           pf = Pyroform(**pyroform_kwargs)

#           # Prepare action-specific parameters
#           action_kwargs = _build_action_kwargs(output_path, debug, dry_run)

#           # Execute the requested action
#           result = _perform_action(pf, action_type, input_path, action_kwargs)

#           # Store results for reporting
#           pf._last_action = action_type
#           pf._last_result = result

#           # Generate report if requested
#           if dump_report:
#               _generate_action_report(pf, action_type, output_path, start_time, silent)

#       except Exception as e:
#           _handle_execution_error(e, debug)


#   def _build_pyroform_kwargs(**base_kwargs) -> Dict[str, Any]:
#       """
#       Build kwargs for Pyroform initialization.

#       Args:
#           **base_kwargs: Base keyword arguments

#       Returns:
#           Dictionary of Pyroform initialization parameters
#       """
#       kwargs = base_kwargs.copy()

#       # Add config file if it exists
#       config_file = kwargs.pop('config_file', None)
#       if config_file and config_file.exists():
#           kwargs["config_file"] = str(config_file)

#       return kwargs


#   def _build_action_kwargs(
#       output_path: Optional[Path],
#       debug: bool,
#       dry_run: bool
#   ) -> Dict[str, Any]:
#       """
#       Build kwargs for action execution.

#       Args:
#           output_path: Output path for generated files
#           debug: Whether debug mode is enabled
#           dry_run: Whether dry run mode is enabled

#       Returns:
#           Dictionary of action parameters
#       """
#       kwargs = {}

#       if output_path:
#           kwargs["output_dir"] = str(output_path)
#       if debug:
#           kwargs["verbose"] = True
#       if dry_run:
#           kwargs['dry_run'] = True

#       return kwargs


#   def _perform_action(
#       pf: Pyroform,
#       action_type: ActionType,
#       input_path: Optional[Path],
#       action_kwargs: Dict[str, Any]
#   ) -> Any:
#       """
#       Execute the specified Pyroform action.

#       Args:
#           pf: Pyroform instance
#           action_type: Type of action to perform
#           input_path: Path to input file(s)
#           action_kwargs: Additional action parameters

#       Returns:
#           Action execution result

#       Raises:
#           ValueError: For unsupported action types
#       """
#       input_str = str(input_path) if input_path else None

#       action_map = {
#           ActionType.CONFIGURE: pf.configure,
#           ActionType.SCORCH: pf.scorch,
#           ActionType.MOUNT: pf.mount,
#           ActionType.VALIDATE: pf.validate,
#           ActionType.SNAPSHOT: pf.snapshot,
#       }

#       if action_type not in action_map:
#           raise ValueError(f"Unsupported action type: {action_type}")

#       action_method = action_map[action_type]
#       result = action_method(input_str, **action_kwargs)

#       # Extract success flag based on action type
#       if action_type == ActionType.VALIDATE:
#           return result.is_valid
#       elif action_type == ActionType.SNAPSHOT:
#           return result.is_valid
#       else:
#           return result


#   def _generate_action_report(
#       pf: Pyroform,
#       action_type: ActionType,
#       output_path: Optional[Path],
#       start_time: str,
#       silent: bool
#   ) -> None:
#       """
#       Generate and save action execution report.

#       Args:
#           pf: Pyroform instance
#           action_type: Type of action performed
#           output_path: Base output path for reports
#           start_time: ISO format start time string
#           silent: Whether to suppress output
#       """
#       end_time = datetime.now().isoformat()

#       # Determine report file path
#       if output_path:
#           if output_path.is_dir():
#               report_file = output_path / f"pyroform_report_{action_type.value}.json"
#           else:
#               report_file = output_path
#       else:
#           report_file = Path(f"pyroform_report_{action_type.value}.json")

#       # Generate report
#       report_success = pf.generate_report(str(report_file))

#       if not silent:
#           if report_success:
#               click.echo(f"Execution report saved to: {report_file}")
#           else:
#               click.echo(f"Failed to save execution report to: {report_file}")


#   def _handle_execution_error(error: Exception, debug: bool) -> None:
#       """
#       Handle execution errors with appropriate messaging.

#       Args:
#           error: Exception that occurred
#           debug: Whether debug mode is enabled
#       """
#       if debug:
#           import traceback
#           click.echo(traceback.format_exc(), err=True)
#       else:
#           click.echo(f"Error executing action: {error}", err=True)


#   def execute_workflow(workflow_config: Dict[str, Any]) -> bool:
#       """
#       Execute a complete Pyroform workflow from configuration.

#       Args:
#           workflow_config: Workflow configuration dictionary

#       Returns:
#           True if workflow completed successfully, False otherwise
#       """
#       try:
#           steps = workflow_config.get("steps", [])
#           auto_confirm = workflow_config.get("auto_confirm", False)
#           config_file = workflow_config.get("config_file")

#           pf = Pyroform(config_file=config_file, auto_confirm=auto_confirm)
#           workflow_results = []

#           for step in steps:
#               if not _validate_workflow_step(step):
#                   return False

#               success = _execute_workflow_step(pf, step, workflow_results)
#               if not success:
#                   return False

#           # Generate workflow report if requested
#           if workflow_config.get("generate_report", True):
#               report_file = workflow_config.get(
#                   "report_file", "pyroform_workflow_report.json"
#               )
#               pf._generate_workflow_report(workflow_results, report_file)

#           click.echo("Workflow completed successfully")
#           return True

#       except Exception as e:
#           click.echo(f"Workflow execution failed: {e}", err=True)
#           return False


#   def _validate_workflow_step(step: Dict[str, Any]) -> bool:
#       """
#       Validate workflow step configuration.

#       Args:
#           step: Workflow step configuration

#       Returns:
#           True if step is valid, False otherwise
#       """
#       action = step.get("action")
#       input_path = step.get("input_path")

#       if not action or not input_path:
#           click.echo(f"Invalid workflow step configuration: {step}", err=True)
#           return False

#       return True


#   def _execute_workflow_step(
#       pf: Pyroform,
#       step: Dict[str, Any],
#       results: List[Dict[str, Any]]
#   ) -> bool:
#       """
#       Execute a single workflow step.

#       Args:
#           pf: Pyroform instance
#           step: Step configuration
#           results: List to collect step results

#       Returns:
#           True if step executed successfully, False otherwise
#       """
#       action = step["action"]
#       input_path = step["input_path"]
#       dry_run = step.get("dry_run", False)

#       try:
#           action_map = {
#               "validate": lambda: pf.validate(input_path, dry_run=dry_run),
#               "configure": lambda: pf.configure(input_path, dry_run=dry_run),
#               "mount": lambda: pf.mount(input_path, dry_run=dry_run),
#               "scorch": lambda: pf.scorch(input_path, dry_run=dry_run),
#           }

#           if action not in action_map:
#               click.echo(f"Unknown action in workflow: {action}", err=True)
#               return False

#           result = action_map[action]()
#           success = _get_step_success(action, result)

#           results.append({
#               "action": action,
#               "input_path": input_path,
#               "success": success,
#               "result": result,
#           })

#           return success

#       except Exception as e:
#           click.echo(f"Error in workflow step {action}: {e}", err=True)
#           return False


#   def _get_step_success(action: str, result: Any) -> bool:
#       """
#       Determine success status for workflow step based on action type.

#       Args:
#           action: Action type
#           result: Action execution result

#       Returns:
#           True if step was successful, False otherwise
#       """
#       if action == "validate":
#           return result.is_valid
#       elif action == "scorch":
#           return getattr(result, 'success', False)
#       else:
#           return bool(result)


#   if __name__ == "__main__":
#       cli()

#   # CODE DUMP


