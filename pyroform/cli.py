"""
Pyroform CLI Interface - Enhanced for Phase 5 End-to-End Workflows
"""

import click
import json
import yaml
import sys

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from .src.models import ActionType
from .pyroform import Pyroform


def format_banner():
    banner_text = """
    ___________________________________________________________________________

      *                          *   Pyroform   *                           *
    ___________________________________________________________________________
                    Regards, the Alveare Solutions #!/Society -x
"""
    return banner_text


class BannerCommand(click.Command):
    def invoke(self, ctx):
        # Display banner for all commands unless help is being shown
        if not ctx.args or not any(arg in ctx.args for arg in ['--help', '-h']):
            self._display_banner()
        return super().invoke(ctx)

    def get_help(self, ctx):
        # Display banner before help text
        banner = self._display_banner(return_text=True)
        original_help = super().get_help(ctx)
        return f"{banner}\n{original_help}"

    def _display_banner(self, return_text=False):
        banner_text = format_banner()
        if return_text:
            return banner_text
        click.echo(banner_text)


class BannerGroup(click.Group):
    def invoke(self, ctx):
        # Display banner for all group commands unless help is being shown
        if not ctx.args or not any(arg in ctx.args for arg in ['--help', '-h']):
            self._display_banner()
        return super().invoke(ctx)

    def get_help(self, ctx):
        # Display banner before help text
        banner = self._display_banner(return_text=True)
        original_help = super().get_help(ctx)
        return f"{banner}\n{original_help}"

    def _display_banner(self, return_text=False):
        banner_text = format_banner()
        if return_text:
            return banner_text
        click.echo(banner_text)

    def format_usage(self, ctx, formatter):
        # Ensure banner is included in usage formatting
        banner_text = self._display_banner(return_text=True)
        formatter.write(banner_text)
        super().format_usage(ctx, formatter)


def display_banner():
    """Display the Pyroform banner"""
    banner_text = format_banner()
    click.echo(banner_text)


@click.group(cls=BannerGroup)
def cli():
    """Pyroform Linux Configurator

    A tool that receives input file(s) containing list of users, user groups,
    block storage device mountpoints, files and directories with owners and permissions,
    generates on the fly FlowCTRL sketch files based on input pyro file(s),
    and runs them using the flow_ctrl library.
    """


@cli.command(cls=BannerCommand)
@click.option(
    "-S",
    "--scorch",
    is_flag=True,
    help="Trigger action scorch using input Pyro file(s)",
)
@click.option(
    "-M", "--mount", is_flag=True, help="Trigger action mount using input Pyro file(s)"
)
@click.option(
    "-C",
    "--configure",
    is_flag=True,
    help="Trigger action configure using input Pyro file(s)",
)
@click.option(
    "-V",
    "--validate",
    is_flag=True,
    help="Trigger action validate using input Pyro file(s)",
)
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
    "-v", "--version", is_flag=True, help="Action that displays Pyroform version"
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Flag to confirm all manual prompts such that manual interaction from user is not required",
)
def main(
    scorch: bool,
    mount: bool,
    configure: bool,
    validate: bool,
    input_path: Optional[str],
    output_path: Optional[str],
    config_file: Optional[str],
    log_file: Optional[str],
    dump_report: bool,
    silent: bool,
    debug: bool,
    version: bool,
    yes: bool,
):
    """
    Pyroform Linux Configurator
    """
    # Banner is automatically displayed by BannerCommand before this function runs

    if version:
        _display_version()
        return

    # Validate action selection
    actions = [scorch, mount, configure, validate]
    action_count = sum(actions)

    if action_count == 0:
        # No action specified, show help
        raise click.UsageError(
            "No action specified. Use --scorch, --mount, --configure, or --validate"
        )
    elif action_count > 1:
        raise click.UsageError(
            "Exactly one action must be specified: --scorch, --mount, --configure, or --validate"
        )

    # Validate input path (only required for actions, not for version)
    if not input_path:
        raise click.UsageError(
            "Input path must be specified with --input for action execution"
        )

    # Determine action type
    action_type = _get_action_type(scorch, mount, configure, validate)

    # Execute the action
    _execute_action(
        action_type=action_type,
        input_path=Path(input_path) if input_path else None,
        output_path=Path(output_path) if output_path else None,
        config_file=Path(config_file) if config_file else None,
        log_file=Path(log_file) if log_file else None,
        dump_report=dump_report,
        silent=silent,
        debug=debug,
        auto_confirm=yes,
    )


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


def _display_version():
    """Display Pyroform version"""
    try:
        from pyroform import __version__

        click.echo(f"Pyroform version {__version__}")
    except ImportError:
        click.echo("Pyroform version 0.1.0 (development)")


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


def _execute_action(
    action_type: ActionType,
    input_path: Path,
    output_path: Optional[Path],
    config_file: Optional[Path],
    log_file: Optional[Path],
    dump_report: bool,
    silent: bool,
    debug: bool,
    auto_confirm: bool,
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

    if not silent:
        click.echo(f"Executing {action_type.value} action with input: {input_path}")

    try:
        # Initialize Pyroform with configuration
        pyroform_kwargs = {"auto_confirm": auto_confirm}
        if config_file and config_file.exists():
            pyroform_kwargs["config_file"] = str(config_file)

        pf = Pyroform(**pyroform_kwargs)

        # Prepare kwargs for the action
        action_kwargs = {}
        if output_path:
            action_kwargs["output_dir"] = str(output_path)
        if debug:
            action_kwargs["verbose"] = True

        # Execute the action
        if action_type == ActionType.CONFIGURE:
            result = pf.configure(str(input_path), **action_kwargs)
            success = result
        elif action_type == ActionType.SCORCH:
            result = pf.scorch(str(input_path), **action_kwargs)
            success = result.success
        elif action_type == ActionType.MOUNT:
            result = pf.mount(str(input_path), **action_kwargs)
            success = result
        elif action_type == ActionType.VALIDATE:
            result = pf.validate(str(input_path), **action_kwargs)
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

        if not silent:
            if success:
                click.echo(
                    f"✓ {action_type.value.capitalize()} action completed successfully"
                )
            else:
                click.echo(f"✗ {action_type.value.capitalize()} action failed")

    except Exception as e:
        if not silent:
            click.echo(f"Error during {action_type.value} execution: {e}")
        if debug:
            import traceback

            click.echo(traceback.format_exc())


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

            click.echo(f"Executing workflow step: {action} with {input_path}")

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
                    click.echo(f"Workflow step failed: {action}")
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

        click.echo("✓ Workflow completed successfully")
        return True

    except Exception as e:
        click.echo(f"Workflow execution failed: {e}")
        return False


# Allow running as script
if __name__ == "__main__":
    cli()

# CODE DUMP

