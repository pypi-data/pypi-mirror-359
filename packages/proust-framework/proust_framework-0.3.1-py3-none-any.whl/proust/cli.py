"""
Command line interface for Proust Framework.
"""

import click
from .core import ProustFramework
from .installer import FrameworkInstaller
from . import __version__


@click.group()
@click.version_option(version=__version__, package_name="proust-framework")
def main() -> None:
    """Proust Framework - AI Memory & Context Archivist"""
    pass


@main.command()
@click.option("--project-root", default=".", help="Project root directory")
@click.option(
    "--location",
    envvar="PROUST_LOCATION",
    help="Base location for .proust and .simone directories (relative to project root)",
)
def install(project_root: str, location: str) -> None:
    """Install Proust framework in the current or specified project."""
    installer = FrameworkInstaller(project_root, location)

    if installer.install_all():
        click.echo("🎉 Proust framework installed successfully!")
        click.echo("📖 See FRAMEWORK_README.md to get started")
        click.echo("🔧 Customize templates in .proust/ for your project")
    else:
        click.echo("❌ Installation failed. See errors above.")
        raise click.Abort()


@main.command()
@click.option("--project-root", default=".", help="Project root directory")
@click.option(
    "--location",
    envvar="PROUST_LOCATION",
    help="Base location for .proust and .simone directories (relative to project root)",
)
def status(project_root: str, location: str) -> None:
    """Check Proust framework status in the project."""
    framework = ProustFramework(project_root, location)

    if framework.is_initialized():
        click.echo("✅ Proust framework is initialized")

        # Show available commands
        commands = framework.get_commands()
        if commands:
            click.echo(f"📋 Available commands: {len(commands)}")
            for command in commands:
                click.echo(f"  - {command}")
        else:
            click.echo("⚠️  No commands found")

        # Show validation issues
        issues = framework.validate_framework()
        total_issues = sum(len(issues[level]) for level in issues)

        if total_issues > 0:
            click.echo(f"⚠️  Found {total_issues} validation issues:")
            for level, issue_list in issues.items():
                if issue_list:
                    click.echo(f"  {level.upper()}:")
                    for issue in issue_list:
                        click.echo(f"    - {issue}")
        else:
            click.echo("✅ Framework validation passed")
    else:
        click.echo("❌ Proust framework is not initialized")
        click.echo("Run 'proust install' to set up the framework")


@main.command()
@click.option("--project-root", default=".", help="Project root directory")
@click.option(
    "--location",
    envvar="PROUST_LOCATION",
    help="Base location for .proust and .simone directories (relative to project root)",
)
def commands(project_root: str, location: str) -> None:
    """List available Simone commands."""
    framework = ProustFramework(project_root, location)

    if not framework.is_initialized():
        click.echo("❌ Proust framework is not initialized")
        click.echo("Run 'proust install' to set up the framework")
        return

    if commands := framework.get_commands():
        click.echo(f"📋 Available Simone commands ({len(commands)}):")
        for command in commands:
            command_path = framework.get_command_path(command)
            if command_path:
                click.echo(f"  - {command}")
            else:
                click.echo(f"  - {command} (missing file)")
    else:
        click.echo("No commands found")


@main.command()
@click.argument("command")
@click.option("--project-root", default=".", help="Project root directory")
@click.option(
    "--location",
    envvar="PROUST_LOCATION",
    help="Base location for .proust and .simone directories (relative to project root)",
)
def show(command: str, project_root: str, location: str) -> None:
    """Show details of a specific Simone command."""
    framework = ProustFramework(project_root, location)

    if not framework.is_initialized():
        click.echo("❌ Proust framework is not initialized")
        return

    command_path = framework.get_command_path(command)
    if not command_path:
        click.echo(f"❌ Command '{command}' not found")
        return

    try:
        with open(command_path, "r") as f:
            content = f.read()
        click.echo(content)
    except Exception as e:
        click.echo(f"❌ Error reading command file: {e}")


@main.command()
@click.option("--project-root", default=".", help="Project root directory")
@click.option(
    "--location",
    envvar="PROUST_LOCATION",
    help="Base location for .proust and .simone directories (relative to project root)",
)
def validate(project_root: str, location: str) -> None:
    """Validate Proust framework integrity."""
    framework = ProustFramework(project_root, location)

    if not framework.is_initialized():
        click.echo("❌ Proust framework is not initialized")
        return

    issues = framework.validate_framework()
    total_issues = sum(len(issues[level]) for level in issues)

    if total_issues == 0:
        click.echo("✅ Framework validation passed")
        return

    click.echo(f"Found {total_issues} validation issues:")

    for level, issue_list in issues.items():
        if issue_list:
            click.echo(f"\n{level.upper()} ({len(issue_list)} issues):")
            for issue in issue_list:
                click.echo(f"  - {issue}")


if __name__ == "__main__":
    main()
