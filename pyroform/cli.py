"""
Pyroform CLI Interface - Updated with Phase 2 functionality
"""
import click
from pathlib import Path
from typing import Optional

from .src.models import ActionType
from .src.parser import PyroParser
from .src.sketch_generator import SketchGenerator
from .src.flow_engine import PyroflowEngine


@click.command()
@click.option('-S', '--scorch', is_flag=True, help='Trigger action scorch using input Pyro file(s)')
@click.option('-M', '--mount', is_flag=True, help='Trigger action mount using input Pyro file(s)')
@click.option('-C', '--configure', is_flag=True, help='Trigger action configure using input Pyro file(s)')
@click.option('-V', '--validate', is_flag=True, help='Trigger action validate using input Pyro file(s)')
@click.option('-i', '--input', 'input_path', type=click.Path(exists=False),
              help='Path to Pyro file (JSON|YAML) or directory containing Pyro files')
@click.option('-o', '--output', 'output_path', type=click.Path(exists=False),
              help='Path to FlowCTRL sketch file (JSON) or directory for generated files')
@click.option('-c', '--config-file', 'config_file', type=click.Path(exists=False),
              help='Path to Pyroform config file (JSON|YAML)')
@click.option('-l', '--log-file', 'log_file', type=click.Path(exists=False),
              help='Path to Pyroform and FlowCTRL log file')
@click.option('-r', '--dump-report', is_flag=True,
              help='Flag to generate report file with STDOUT, STDERR plus summary')
@click.option('-s', '--silent', is_flag=True, help='Flag to suppress STDOUT')
@click.option('-d', '--debug', is_flag=True, help='Flag that makes logging and STDOUT messages more verbose')
@click.option('-v', '--version', is_flag=True, help='Action that displays Pyroform version')
@click.option('-y', '--yes', is_flag=True,
              help='Flag to confirm all manual prompts such that manual interaction from user is not required')
def main(scorch: bool, mount: bool, configure: bool, validate: bool,
         input_path: Optional[str], output_path: Optional[str],
         config_file: Optional[str], log_file: Optional[str],
         dump_report: bool, silent: bool, debug: bool, version: bool, yes: bool):
    """
    Pyroform Linux Configurator

    A tool that receives input file(s) containing list of users, user groups,
    block storage device mountpoints, files and directories with owners and permissions,
    generates on the fly FlowCTRL sketch files based on input pyro file(s),
    and runs them using the flow_ctrl library.
    """

    if version:
        _display_version()
        return

    # Validate action selection
    actions = [scorch, mount, configure, validate]
    action_count = sum(actions)

    if action_count == 0:
        # No action specified, show help
        raise click.UsageError("No action specified. Use --scorch, --mount, --configure, or --validate")
    elif action_count > 1:
        raise click.UsageError("Exactly one action must be specified: --scorch, --mount, --configure, or --validate")

    # Validate input path (only required for actions, not for version)
    if not input_path:
        raise click.UsageError("Input path must be specified with --input for action execution")

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
        auto_confirm=yes
    )


def _display_version():
    """Display Pyroform version"""
    try:
        from pyroform import __version__
        click.echo(f"Pyroform version {__version__}")
    except ImportError:
        click.echo("Pyroform version 0.1.0 (development)")


def _get_action_type(scorch: bool, mount: bool, configure: bool, validate: bool) -> ActionType:
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


def _execute_action(action_type: ActionType, input_path: Path, output_path: Optional[Path],
                   config_file: Optional[Path], log_file: Optional[Path],
                   dump_report: bool, silent: bool, debug: bool, auto_confirm: bool):
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
    if not silent:
        click.echo(f"Executing {action_type.value} action with input: {input_path}")

    try:
        # Parse input configuration
        parser = PyroParser()
        configs = parser.parse(input_path)

        if not configs:
            click.echo("No valid configurations found in input path")
            return

        # Initialize components
        sketch_generator = SketchGenerator()
        pyro_engine = PyroflowEngine()

        # Process each configuration
        for config in configs:
            if not silent:
                click.echo(f"Processing configuration: {config.label}")

            # Generate sketch based on action type
            if action_type == ActionType.VALIDATE:
                # Validation doesn't use sketches
                if not silent:
                    click.echo("Validation action - no sketch generated")
                continue

            sketch = sketch_generator.generate_sketch(config, action_type)

            # Save sketch if output path specified
            if output_path:
                if output_path.is_dir():
                    sketch_filename = f"fc_{config.label.replace(' ', '_')}.json"
                    sketch_file = output_path / sketch_filename
                else:
                    sketch_file = output_path

                if sketch_generator.save_sketch(sketch, sketch_file):
                    if not silent:
                        click.echo(f"Sketch saved to: {sketch_file}")
                else:
                    click.echo(f"Failed to save sketch to: {sketch_file}")

            # Execute sketch through FlowCTRL
            if action_type != ActionType.VALIDATE:
                if not silent:
                    click.echo(f"Executing {action_type.value} sketch...")

                # Confirm destructive actions if not auto-confirmed
                if action_type in [ActionType.SCORCH, ActionType.CONFIGURE] and not auto_confirm:
                    if not _confirm_destructive_action(action_type, config.label):
                        if not silent:
                            click.echo("Action cancelled by user")
                        continue

                success = pyro_engine.execute_sketch(sketch, action_type)

                if not silent:
                    if success:
                        click.echo(f"{action_type.value.capitalize()} action completed successfully")
                    else:
                        click.echo(f"{action_type.value.capitalize()} action failed")

        if not silent:
            click.echo("Action execution completed")

    except Exception as e:
        click.echo(f"Error during {action_type.value} execution: {e}")
        if debug:
            import traceback
            click.echo(traceback.format_exc())


def _confirm_destructive_action(action_type: ActionType, config_label: str) -> bool:
    """
    Confirm destructive actions with user

    Args:
        action_type: Type of action being confirmed
        config_label: Label of the configuration

    Returns:
        True if confirmed, False if cancelled
    """
    import click

    if action_type == ActionType.SCORCH:
        message = f"WARNING: Scorch action will remove system resources not specified in '{config_label}'. Continue?"
    elif action_type == ActionType.CONFIGURE:
        message = f"Configure action will modify system state according to '{config_label}'. Continue?"
    else:
        message = f"Proceed with {action_type.value} action for '{config_label}'?"

    return click.confirm(message)


# Allow running as script
if __name__ == '__main__':
    main()


# CODE DUMP

#   """
#   Pyroform CLI Interface
#   """
#   import click
#   from pathlib import Path
#   from typing import Optional

#   from .src.models import ActionType


#   @click.command()
#   @click.option('-S', '--scorch', is_flag=True, help='Trigger action scorch using input Pyro file(s)')
#   @click.option('-M', '--mount', is_flag=True, help='Trigger action mount using input Pyro file(s)')
#   @click.option('-C', '--configure', is_flag=True, help='Trigger action configure using input Pyro file(s)')
#   @click.option('-V', '--validate', is_flag=True, help='Trigger action validate using input Pyro file(s)')
#   @click.option('-i', '--input', 'input_path', type=click.Path(exists=False),
#               help='Path to Pyro file (JSON|YAML) or directory containing Pyro files')
#   @click.option('-o', '--output', 'output_path', type=click.Path(exists=False),
#               help='Path to FlowCTRL sketch file (JSON) or directory for generated files')
#   @click.option('-c', '--config-file', 'config_file', type=click.Path(exists=False),
#               help='Path to Pyroform config file (JSON|YAML)')
#   @click.option('-l', '--log-file', 'log_file', type=click.Path(exists=False),
#               help='Path to Pyroform and FlowCTRL log file')
#   @click.option('-r', '--dump-report', is_flag=True,
#               help='Flag to generate report file with STDOUT, STDERR plus summary')
#   @click.option('-s', '--silent', is_flag=True, help='Flag to suppress STDOUT')
#   @click.option('-d', '--debug', is_flag=True, help='Flag that makes logging and STDOUT messages more verbose')
#   @click.option('-v', '--version', is_flag=True, help='Action that displays Pyroform version')
#   @click.option('-y', '--yes', is_flag=True,
#               help='Flag to confirm all manual prompts such that manual interaction from user is not required')
#   def main(scorch: bool, mount: bool, configure: bool, validate: bool,
#           input_path: Optional[str], output_path: Optional[str],
#           config_file: Optional[str], log_file: Optional[str],
#           dump_report: bool, silent: bool, debug: bool, version: bool, yes: bool):
#       """
#       Pyroform Linux Configurator

#       A tool that receives input file(s) containing list of users, user groups,
#       block storage device mountpoints, files and directories with owners and permissions,
#       generates on the fly FlowCTRL sketch files based on input pyro file(s),
#       and runs them using the flow_ctrl library.
#       """

#       if version:
#           _display_version()
#           return

#       # Validate action selection
#       actions = [scorch, mount, configure, validate]
#       action_count = sum(actions)

#       if action_count == 0:
#           # No action specified, show help
#           raise click.UsageError("No action specified. Use --scorch, --mount, --configure, or --validate")
#       elif action_count > 1:
#           raise click.UsageError("Exactly one action must be specified: --scorch, --mount, --configure, or --validate")

#       # Validate input path (only required for actions, not for version)
#       if not input_path:
#           raise click.UsageError("Input path must be specified with --input for action execution")

#       # Determine action type
#       action_type = _get_action_type(scorch, mount, configure, validate)

#       # Execute the action
#       _execute_action(
#           action_type=action_type,
#           input_path=Path(input_path) if input_path else None,
#           output_path=Path(output_path) if output_path else None,
#           config_file=Path(config_file) if config_file else None,
#           log_file=Path(log_file) if log_file else None,
#           dump_report=dump_report,
#           silent=silent,
#           debug=debug,
#           auto_confirm=yes
#       )


#   def _display_version():
#       """Display Pyroform version"""
#       try:
#           from pyroform import __version__
#           click.echo(f"Pyroform version {__version__}")
#       except ImportError:
#           click.echo("Pyroform version 0.1.0 (development)")


#   def _get_action_type(scorch: bool, mount: bool, configure: bool, validate: bool) -> ActionType:
#       """Determine action type from CLI flags"""
#       if scorch:
#           return ActionType.SCORCH
#       elif mount:
#           return ActionType.MOUNT
#       elif configure:
#           return ActionType.CONFIGURE
#       elif validate:
#           return ActionType.VALIDATE
#       else:
#           raise ValueError("No action specified")


#   def _execute_action(action_type: ActionType, input_path: Path, output_path: Optional[Path],
#                   config_file: Optional[Path], log_file: Optional[Path],
#                   dump_report: bool, silent: bool, debug: bool, auto_confirm: bool):
#       """
#       Execute the specified action with given parameters

#       Args:
#           action_type: Type of action to perform
#           input_path: Path to input Pyro file(s)
#           output_path: Path for output files (optional)
#           config_file: Path to config file (optional)
#           log_file: Path to log file (optional)
#           dump_report: Whether to generate report
#           silent: Whether to suppress STDOUT
#           debug: Whether to enable debug mode
#           auto_confirm: Whether to auto-confirm prompts
#       """
#       # This will be implemented in later phases
#       click.echo(f"Executing {action_type.value} action with input: {input_path}")

#       if output_path:
#           click.echo(f"Output path: {output_path}")

#       if config_file:
#           click.echo(f"Config file: {config_file}")

#       if debug:
#           click.echo("Debug mode enabled")

#       if auto_confirm:
#           click.echo("Auto-confirm enabled - skipping prompts")

#       # Placeholder for actual implementation
#       click.echo("Action execution will be implemented in Phase 2")


#   # Allow running as script
#   if __name__ == '__main__':
#       main()

# CODE DUMP

#   """
#   Pyroform CLI Interface
#   """
#   import click
#   from pathlib import Path
#   from typing import Optional

#   from .src.models import ActionType


#   @click.command()
#   @click.option('-S', '--scorch', is_flag=True, help='Trigger action scorch using input Pyro file(s)')
#   @click.option('-M', '--mount', is_flag=True, help='Trigger action mount using input Pyro file(s)')
#   @click.option('-C', '--configure', is_flag=True, help='Trigger action configure using input Pyro file(s)')
#   @click.option('-V', '--validate', is_flag=True, help='Trigger action validate using input Pyro file(s)')
#   @click.option('-i', '--input', 'input_path', type=click.Path(exists=False),
#               help='Path to Pyro file (JSON|YAML) or directory containing Pyro files')
#   @click.option('-o', '--output', 'output_path', type=click.Path(exists=False),
#               help='Path to FlowCTRL sketch file (JSON) or directory for generated files')
#   @click.option('-c', '--config-file', 'config_file', type=click.Path(exists=False),
#               help='Path to Pyroform config file (JSON|YAML)')
#   @click.option('-l', '--log-file', 'log_file', type=click.Path(exists=False),
#               help='Path to Pyroform and FlowCTRL log file')
#   @click.option('-r', '--dump-report', is_flag=True,
#               help='Flag to generate report file with STDOUT, STDERR plus summary')
#   @click.option('-s', '--silent', is_flag=True, help='Flag to suppress STDOUT')
#   @click.option('-d', '--debug', is_flag=True, help='Flag that makes logging and STDOUT messages more verbose')
#   @click.option('-v', '--version', is_flag=True, help='Action that displays Pyroform version')
#   @click.option('-y', '--yes', is_flag=True,
#               help='Flag to confirm all manual prompts such that manual interaction from user is not required')
#   def main(scorch: bool, mount: bool, configure: bool, validate: bool,
#           input_path: Optional[str], output_path: Optional[str],
#           config_file: Optional[str], log_file: Optional[str],
#           dump_report: bool, silent: bool, debug: bool, version: bool, yes: bool):
#       """
#       Pyroform Linux Configurator

#       A tool that receives input file(s) containing list of users, user groups,
#       block storage device mountpoints, files and directories with owners and permissions,
#       generates on the fly FlowCTRL sketch files based on input pyro file(s),
#       and runs them using the flow_ctrl library.
#       """

#       if version:
#           _display_version()
#           return

#       # Validate action selection
#       actions = [scorch, mount, configure, validate]
#       if sum(actions) != 1:
#           raise click.UsageError("Exactly one action must be specified: --scorch, --mount, --configure, or --validate")

#       # Validate input path
#       if not input_path:
#           raise click.UsageError("Input path must be specified with --input")

#       # Determine action type
#       action_type = _get_action_type(scorch, mount, configure, validate)

#       # Execute the action
#       _execute_action(
#           action_type=action_type,
#           input_path=Path(input_path) if input_path else None,
#           output_path=Path(output_path) if output_path else None,
#           config_file=Path(config_file) if config_file else None,
#           log_file=Path(log_file) if log_file else None,
#           dump_report=dump_report,
#           silent=silent,
#           debug=debug,
#           auto_confirm=yes
#       )


#   def _display_version():
#       """Display Pyroform version"""
#       try:
#           from pyroform import __version__
#           click.echo(f"Pyroform version {__version__}")
#       except ImportError:
#           click.echo("Pyroform version 0.1.0 (development)")


#   def _get_action_type(scorch: bool, mount: bool, configure: bool, validate: bool) -> ActionType:
#       """Determine action type from CLI flags"""
#       if scorch:
#           return ActionType.SCORCH
#       elif mount:
#           return ActionType.MOUNT
#       elif configure:
#           return ActionType.CONFIGURE
#       elif validate:
#           return ActionType.VALIDATE
#       else:
#           raise ValueError("No action specified")


#   def _execute_action(action_type: ActionType, input_path: Path, output_path: Optional[Path],
#                   config_file: Optional[Path], log_file: Optional[Path],
#                   dump_report: bool, silent: bool, debug: bool, auto_confirm: bool):
#       """
#       Execute the specified action with given parameters

#       Args:
#           action_type: Type of action to perform
#           input_path: Path to input Pyro file(s)
#           output_path: Path for output files (optional)
#           config_file: Path to config file (optional)
#           log_file: Path to log file (optional)
#           dump_report: Whether to generate report
#           silent: Whether to suppress STDOUT
#           debug: Whether to enable debug mode
#           auto_confirm: Whether to auto-confirm prompts
#       """
#       # This will be implemented in later phases
#       click.echo(f"Executing {action_type.value} action with input: {input_path}")

#       if output_path:
#           click.echo(f"Output path: {output_path}")

#       if config_file:
#           click.echo(f"Config file: {config_file}")

#       if debug:
#           click.echo("Debug mode enabled")

#       if auto_confirm:
#           click.echo("Auto-confirm enabled - skipping prompts")

#       # Placeholder for actual implementation
#       click.echo("Action execution will be implemented in Phase 2")


#   # Allow running as script
#   if __name__ == '__main__':
#       main()


# CODE DUMP

#   # pyroform/cli.py
#   import click
#   from pathlib import Path
#   from .src.core import PyroformEngine

#   @click.command()
#   @click.option('-S', '--scorch', is_flag=True, help='Trigger scorch action')
#   @click.option('-M', '--mount', is_flag=True, help='Trigger mount action')
#   # ... other options
#   def main(scorch, mount, configure, validate, input, output, config_file,
#           log_file, dump_report, silent, debug, version, yes):
#       """Pyroform Linux Configurator"""
#       pass
