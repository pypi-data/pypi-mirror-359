"""
Proust Framework installer for setting up projects.
"""

import os
import shutil
import urllib.request
from pathlib import Path
from typing import List, Optional


class FrameworkInstaller:
    """Installer for Proust Framework files."""
    
    BASE_URL = "https://raw.githubusercontent.com/renkasiyas/proust/main"
    
    def __init__(self, project_root: str = "."):
        """Initialize installer for given project root."""
        self.project_root = Path(project_root).resolve()
        self.proust_dir = self.project_root / "src" / ".proust"
        self.simone_dir = self.project_root / "src" / ".simone"
        self.examples_dir = self.project_root / ".examples"
    
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
            self.examples_dir
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
            ("src/.proust/universal_claude.md", self.proust_dir / "universal_claude.md"),
            ("src/.proust/guardrails.yml", self.proust_dir / "guardrails.yml"),
            ("src/.proust/brand.yml", self.proust_dir / "brand.yml"),
            ("src/.proust/external_docs.yml", self.proust_dir / "external_docs.yml"),
            ("src/.proust/manifesto/manifesto.yml", self.proust_dir / "manifesto" / "manifesto.yml"),
        ]
        
        failed = []
        for remote_path, local_path in core_files:
            if not self.download_file(remote_path, local_path):
                failed.append(remote_path)
        
        return failed
    
    def install_commands(self) -> List[str]:
        """Install Simone command files."""
        commands = [
            "analyze_codebase", "brainstorm", "code_review", "commit",
            "consistency_audit", "context_management", "create_general_task",
            "create_sprint_tasks", "create_sprints_from_milestone",
            "discuss_review", "do_task", "gh_do_issues", "initialize",
            "initialize_new_project", "prime", "project_review",
            "reflect_on_solution", "test", "testing_review", "yolo"
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
            ("src/.simone/00_PROJECT_MANIFEST.md", self.simone_dir / "00_PROJECT_MANIFEST.md"),
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
            "task_template.md"
        ]
        
        failed = []
        for template in templates:
            remote_path = f"src/.simone/99_TEMPLATES/{template}"
            local_path = self.simone_dir / "99_TEMPLATES" / template
            if not self.download_file(remote_path, local_path):
                failed.append(remote_path)
        
        return failed
    
    def install_examples(self) -> List[str]:
        """Install example files."""
        examples = [
            "README.md",
            "brand_example.yml",
            "ethos_example.md",
            "guardrails_example.yml",
            "manifesto_example.yml",
            "universal_claude_example.md"
        ]
        
        failed = []
        for example in examples:
            remote_path = f".examples/{example}"
            local_path = self.examples_dir / example
            if not self.download_file(remote_path, local_path):
                failed.append(remote_path)
        
        return failed
    
    def install_documentation(self) -> List[str]:
        """Install root documentation files."""
        docs = [
            ("README.md", self.project_root / "README.md"),
            ("FRAMEWORK_README.md", self.project_root / "FRAMEWORK_README.md"),
            ("TEMPLATE_GUIDE.md", self.project_root / "TEMPLATE_GUIDE.md"),
            ("AUDIT_SUPER_PROMPT.md", self.project_root / "AUDIT_SUPER_PROMPT.md"),
        ]
        
        failed = []
        for remote_path, local_path in docs:
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
        
        print("Installing examples...")
        failed_files.extend(self.install_examples())
        
        print("Installing documentation...")
        failed_files.extend(self.install_documentation())
        
        if failed_files:
            print(f"Failed to install {len(failed_files)} files:")
            for file in failed_files:
                print(f"  - {file}")
            return False
        
        print("✅ Proust framework installed successfully!")
        return True