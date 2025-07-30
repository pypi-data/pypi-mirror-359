"""
Core Proust Framework functionality.
"""

from pathlib import Path
from typing import Dict, List, Optional


class ProustFramework:
    """Main Proust Framework class for managing AI context and project memory."""

    def __init__(self, project_root: str = ".", location: Optional[str] = None):
        """Initialize Proust Framework in the given project root."""
        self.project_root = Path(project_root).resolve()

        if location:
            # Resolve location relative to project root
            base_path = (self.project_root / location).resolve()
            self.proust_dir = base_path / ".proust"
            self.simone_dir = base_path / ".simone"
        else:
            # Default behavior - check for symlinks first
            project_proust = self.project_root / ".proust"
            project_simone = self.project_root / ".simone"

            # Resolve symlinks to actual locations
            self.proust_dir = (
                project_proust.resolve() if project_proust.exists() else project_proust
            )
            self.simone_dir = (
                project_simone.resolve() if project_simone.exists() else project_simone
            )

    def is_using_symlinks(self) -> bool:
        """Check if the framework directories are symlinked."""
        project_proust = self.project_root / ".proust"
        project_simone = self.project_root / ".simone"

        return (project_proust.is_symlink()) or (project_simone.is_symlink())

    def is_initialized(self) -> bool:
        """Check if Proust framework is initialized in the project."""
        return (
            self.proust_dir.exists()
            and self.simone_dir.exists()
            and (self.proust_dir / "ethos.md").exists()
        )

    def get_commands(self) -> List[str]:
        """Get list of available Simone commands."""
        commands_dir = self.proust_dir / "commands" / "simone"
        if not commands_dir.exists():
            return []

        commands = []
        for file in commands_dir.glob("*.md"):
            commands.append(file.stem)
        return sorted(commands)

    def get_command_path(self, command: str) -> Optional[Path]:
        """Get path to a specific command file."""
        command_path = self.proust_dir / "commands" / "simone" / f"{command}.md"
        return command_path if command_path.exists() else None

    def get_project_manifest(self) -> Optional[Path]:
        """Get path to project manifest file."""
        manifest_path = self.simone_dir / "00_PROJECT_MANIFEST.md"
        return manifest_path if manifest_path.exists() else None

    def get_ethos(self) -> Optional[Path]:
        """Get path to ethos file."""
        ethos_path = self.proust_dir / "ethos.md"
        return ethos_path if ethos_path.exists() else None

    def get_universal_claude(self) -> Optional[Path]:
        """Get path to universal Claude configuration."""
        claude_path = self.proust_dir / "universal_claude.md"
        return claude_path if claude_path.exists() else None

    def validate_framework(self) -> Dict[str, List[str]]:
        """Validate framework integrity and return issues."""
        issues: Dict[str, List[str]] = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
        }

        # Check core files exist
        core_files = ["ethos.md", "universal_claude.md", "guardrails.yml", "brand.yml"]

        for file in core_files:
            if not (self.proust_dir / file).exists():
                issues["critical"].append(f"Missing core file: {file}")

        # Check command files exist
        commands_dir = self.proust_dir / "commands" / "simone"
        if not commands_dir.exists():
            issues["critical"].append("Missing commands directory")

        # Check Simone structure
        simone_required = ["README.md", "CLAUDE.MD", "00_PROJECT_MANIFEST.md"]

        for file in simone_required:
            if not (self.simone_dir / file).exists():
                issues["high"].append(f"Missing Simone file: {file}")

        return issues
