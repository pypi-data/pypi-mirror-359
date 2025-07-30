"""
Command line interface for Proust Framework.
"""

import click
from pathlib import Path
from .core import ProustFramework
from .installer import FrameworkInstaller


@click.group()
@click.version_option()
def main():
    """Proust Framework - AI Memory & Context Archivist"""
    pass


@main.command()
@click.option("--project-root", default=".", help="Project root directory")
def install(project_root):
    """Install Proust framework in the current or specified project."""
    installer = FrameworkInstaller(project_root)
    
    if installer.install_all():
        click.echo("🎉 Proust framework installed successfully!")
        click.echo("📖 See FRAMEWORK_README.md to get started")
        click.echo("🔧 Customize templates in src/.proust/ for your project")
    else:
        click.echo("❌ Installation failed. See errors above.")
        raise click.Abort()


@main.command()
@click.option("--project-root", default=".", help="Project root directory")
def status(project_root):
    """Check Proust framework status in the project."""
    framework = ProustFramework(project_root)
    
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
def commands(project_root):
    """List available Simone commands."""
    framework = ProustFramework(project_root)
    
    if not framework.is_initialized():
        click.echo("❌ Proust framework is not initialized")
        click.echo("Run 'proust install' to set up the framework")
        return
    
    commands = framework.get_commands()
    if commands:
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
def show(command, project_root):
    """Show details of a specific Simone command."""
    framework = ProustFramework(project_root)
    
    if not framework.is_initialized():
        click.echo("❌ Proust framework is not initialized")
        return
    
    command_path = framework.get_command_path(command)
    if not command_path:
        click.echo(f"❌ Command '{command}' not found")
        return
    
    try:
        with open(command_path, 'r') as f:
            content = f.read()
        click.echo(content)
    except Exception as e:
        click.echo(f"❌ Error reading command file: {e}")


@main.command()
@click.option("--project-root", default=".", help="Project root directory")
def validate(project_root):
    """Validate Proust framework integrity."""
    framework = ProustFramework(project_root)
    
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