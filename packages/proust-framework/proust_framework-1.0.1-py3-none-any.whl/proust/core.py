"""
Core Proust Framework functionality.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class ProustFramework:
    """Main Proust Framework class for managing AI context and project memory."""
    
    def __init__(self, project_root: str = "."):
        """Initialize Proust Framework in the given project root."""
        self.project_root = Path(project_root).resolve()
        self.proust_dir = self.project_root / "src" / ".proust"
        self.simone_dir = self.project_root / "src" / ".simone"
        self.examples_dir = self.project_root / ".examples"
    
    def is_initialized(self) -> bool:
        """Check if Proust framework is initialized in the project."""
        return (
            self.proust_dir.exists() and
            self.simone_dir.exists() and
            (self.proust_dir / "ethos.md").exists()
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
        issues = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        # Check core files exist
        core_files = [
            "ethos.md",
            "universal_claude.md",
            "guardrails.yml",
            "brand.yml"
        ]
        
        for file in core_files:
            if not (self.proust_dir / file).exists():
                issues["critical"].append(f"Missing core file: {file}")
        
        # Check command files exist
        commands_dir = self.proust_dir / "commands" / "simone"
        if not commands_dir.exists():
            issues["critical"].append("Missing commands directory")
        
        # Check Simone structure
        simone_required = [
            "README.md",
            "CLAUDE.MD",
            "00_PROJECT_MANIFEST.md"
        ]
        
        for file in simone_required:
            if not (self.simone_dir / file).exists():
                issues["high"].append(f"Missing Simone file: {file}")
        
        return issues