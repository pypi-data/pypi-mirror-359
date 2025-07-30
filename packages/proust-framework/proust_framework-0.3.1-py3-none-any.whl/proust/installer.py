"""
Proust Framework installer for setting up projects.
"""

import urllib.request
from pathlib import Path
from typing import List, Optional


class FrameworkInstaller:
    """Installer for Proust Framework files."""

    BASE_URL = "https://raw.githubusercontent.com/renkasiyas/proust/main"

    def __init__(self, project_root: str = ".", location: Optional[str] = None):
        """Initialize installer for given project root."""
        self.project_root = Path(project_root).resolve()
        self.location = location

        if location:
            # Resolve location relative to project root
            base_path = (self.project_root / location).resolve()
            self.proust_dir = base_path / ".proust"
            self.simone_dir = base_path / ".simone"
            self.is_external_location = not self._is_location_inside_project(base_path)
        else:
            # Default behavior
            self.proust_dir = self.project_root / ".proust"
            self.simone_dir = self.project_root / ".simone"
            self.is_external_location = False

    def _is_location_inside_project(self, base_path: Path) -> bool:
        """Check if the base path is inside the project root."""
        try:
            base_path.resolve().relative_to(self.project_root.resolve())
            return True
        except ValueError:
            return False

    def _create_symlinks(self) -> None:
        """Create symlinks in project root pointing to external directories."""
        if not self.is_external_location:
            return

        self._create_symlink_safely(".proust", self.proust_dir)
        self._create_symlink_safely(".simone", self.simone_dir)

    def _create_symlink_safely(self, link_name: str, target_dir: Path) -> None:
        """Safely create a symlink with proper error handling."""
        project_link = self.project_root / link_name

        # Check if link already exists
        if project_link.exists():
            if project_link.is_symlink():
                existing_target = project_link.resolve()
                if existing_target == target_dir.resolve():
                    print(f"Symlink {link_name} already points to correct location")
                    return
                else:
                    print(
                        f"Warning: {link_name} symlink exists but points to {existing_target}"
                    )
                    print(f"Expected: {target_dir}")
                    return
            else:
                print(
                    f"Warning: {link_name} exists as a regular directory/file, cannot create symlink"
                )
                return

        # Create the symlink
        try:
            project_link.symlink_to(target_dir)
            print(f"✅ Created symlink: {project_link} -> {target_dir}")
        except OSError as e:
            if "Operation not permitted" in str(e):
                print(
                    f"❌ Permission denied creating {link_name} symlink. Try running with admin privileges."
                )
            elif "File exists" in str(e):
                print(f"❌ {link_name} already exists, cannot create symlink")
            else:
                print(f"❌ Could not create {link_name} symlink: {e}")
        except Exception as e:
            print(f"❌ Unexpected error creating {link_name} symlink: {e}")

    def create_directories(self) -> None:
        """Create necessary directory structure."""
        directories = [
            self.proust_dir / "commands" / "simone",
            self.proust_dir / "manifesto",
            self.simone_dir / "01_PROJECT_DOCS",
            self.simone_dir / "02_REQUIREMENTS",
            self.simone_dir / "03_SPRINTS",
            self.simone_dir / "04_GENERAL_TASKS",
            self.simone_dir / "05_ARCHITECTURAL_DECISIONS",
            self.simone_dir / "99_TEMPLATES",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def download_file(self, relative_path: str, local_path: Path) -> bool:
        """Download a file from the repository."""
        url = f"{self.BASE_URL}/{relative_path}"
        try:
            urllib.request.urlretrieve(url, local_path)
            return True
        except Exception as e:
            print(f"Failed to download {relative_path}: {e}")
            return False

    def install_core_files(self) -> List[str]:
        """Install core Proust framework files."""
        core_files = [
            ("src/.proust/ethos.md", self.proust_dir / "ethos.md"),
            (
                "src/.proust/universal_claude.md",
                self.proust_dir / "universal_claude.md",
            ),
            ("src/.proust/guardrails.yml", self.proust_dir / "guardrails.yml"),
            ("src/.proust/brand.yml", self.proust_dir / "brand.yml"),
            ("src/.proust/external_docs.yml", self.proust_dir / "external_docs.yml"),
            (
                "src/.proust/manifesto/manifesto.yml",
                self.proust_dir / "manifesto" / "manifesto.yml",
            ),
        ]

        failed = []
        for remote_path, local_path in core_files:
            if not self.download_file(remote_path, local_path):
                failed.append(remote_path)

        return failed

    def install_commands(self) -> List[str]:
        """Install Simone command files."""
        commands = [
            "analyze_codebase",
            "brainstorm",
            "code_review",
            "commit",
            "consistency_audit",
            "context_management",
            "create_general_task",
            "create_sprint_tasks",
            "create_sprints_from_milestone",
            "discuss_review",
            "do_task",
            "gh_do_issues",
            "initialize",
            "initialize_new_project",
            "prime",
            "project_review",
            "reflect_on_solution",
            "test",
            "testing_review",
            "yolo",
        ]

        failed = []
        for command in commands:
            remote_path = f"src/.proust/commands/simone/{command}.md"
            local_path = self.proust_dir / "commands" / "simone" / f"{command}.md"
            if not self.download_file(remote_path, local_path):
                failed.append(remote_path)

        return failed

    def install_simone_structure(self) -> List[str]:
        """Install Simone project structure files."""
        simone_files = [
            ("src/.simone/README.md", self.simone_dir / "README.md"),
            ("src/.simone/CLAUDE.MD", self.simone_dir / "CLAUDE.MD"),
            (
                "src/.simone/00_PROJECT_MANIFEST.md",
                self.simone_dir / "00_PROJECT_MANIFEST.md",
            ),
        ]

        failed = []
        for remote_path, local_path in simone_files:
            if not self.download_file(remote_path, local_path):
                failed.append(remote_path)

        return failed

    def install_templates(self) -> List[str]:
        """Install template files."""
        templates = [
            "adr_template.md",
            "milestone_meta_template.md",
            "project_manifest_template.md",
            "sprint_meta_template.md",
            "task_template.md",
        ]

        failed = []
        for template in templates:
            remote_path = f"src/.simone/99_TEMPLATES/{template}"
            local_path = self.simone_dir / "99_TEMPLATES" / template
            if not self.download_file(remote_path, local_path):
                failed.append(remote_path)

        return failed

    def install_all(self) -> bool:
        """Install complete Proust framework."""
        print("Creating directory structure...")
        self.create_directories()

        failed_files = []

        print("Installing core files...")
        failed_files.extend(self.install_core_files())

        print("Installing commands...")
        failed_files.extend(self.install_commands())

        print("Installing Simone structure...")
        failed_files.extend(self.install_simone_structure())

        print("Installing templates...")
        failed_files.extend(self.install_templates())

        # Create symlinks if location is external
        if self.is_external_location:
            print("Creating symlinks for external location...")
            self._create_symlinks()

        if failed_files:
            print(f"Failed to install {len(failed_files)} files:")
            for file in failed_files:
                print(f"  - {file}")
            return False

        print("✅ Proust framework installed successfully!")
        return True
