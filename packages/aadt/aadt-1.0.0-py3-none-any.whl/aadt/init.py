"""
Project initialization module for creating new Anki add-on projects.
"""

import json
import re
from pathlib import Path
from typing import Any

import questionary
from questionary import Choice, Separator

from .config import AddonConfig


class ProjectInitializationError(Exception):
    """Exception raised when project initialization fails"""

    pass


class ProjectInitializer:
    """
    Handles the initialization of new Anki add-on projects.
    Creates project structure, configuration files, and template code.
    """

    def __init__(self, target_dir: Path) -> None:
        self.target_dir = target_dir
        self.config_path = target_dir / "addon.json"

    def init_project(self, interactive: bool = True) -> None:
        """
        Initialize a new add-on project in the target directory.

        Args:
            interactive: Whether to prompt for user input

        Raises:
            ProjectInitializationError: If initialization fails
        """
        # Create target directory if it doesn't exist
        self._ensure_target_directory()

        if self.config_path.exists():
            raise ProjectInitializationError(
                f"addon.json already exists in {self.target_dir}. "
                "This directory appears to already contain an add-on project."
            )

        if interactive:
            config_data = self._collect_project_info()
        else:
            config_data = self._get_default_config()

        # Create and validate configuration
        try:
            config = AddonConfig.from_dict(config_data)
        except (KeyError, TypeError, ValueError) as e:
            raise ProjectInitializationError(f"Invalid configuration data: {e}") from e

        # Create project structure
        self._create_project_structure(config)

        # Write configuration file
        self._write_config_file(config_data)

        # Create template files
        self._create_template_files(config)

        print("\n✅ Add-on project initialized successfully!")
        print(f"📁 Project directory: {self.target_dir}")
        print(f"🔧 Edit {self.config_path} to customize your configuration")
        print("🚀 Run 'uv run aab build' to build your add-on")

    def _collect_project_info(self) -> dict[str, Any]:
        """Collect project information through interactive prompts."""
        print("🚀 Initializing new Anki add-on project...\n")

        # Get basic project info
        answers = questionary.form(
            display_name=questionary.text(
                "Display name (shown to users):", default=self._suggest_display_name()
            ),
            author=questionary.text("Author name:"),
        ).ask()

        if not answers:
            raise ProjectInitializationError("Initialization cancelled.")

        display_name = answers["display_name"]

        more_answers = questionary.form(
            module_name=questionary.text(
                "Module name (Python package name):",
                default=self._suggest_module_name(display_name),
                validate=lambda text: re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", text)
                is not None,
            ),
            repo_name=questionary.text(
                "Repository name (for files/GitHub):",
                default=self._suggest_repo_name(display_name),
            ),
        ).ask()

        if not more_answers:
            raise ProjectInitializationError("Initialization cancelled.")

        answers.update(more_answers)

        # Optional fields
        optional_answers = questionary.form(
            ankiweb_id=questionary.text("AnkiWeb ID (optional, for existing add-ons):"),
            contact=questionary.text("Contact email (optional):"),
            homepage=questionary.text("Homepage URL (optional):"),
            tags=questionary.text("Tags (space-separated, optional):"),
        ).ask()

        if not optional_answers:
            raise ProjectInitializationError("Initialization cancelled.")

        # Build configuration
        config_data = {
            "display_name": answers["display_name"],
            "module_name": answers["module_name"],
            "repo_name": answers["repo_name"],
            "author": answers["author"],
            "conflicts": [],
            "targets": ["qt6"],
        }

        # Add optional fields if provided
        for key, value in optional_answers.items():
            if value:
                config_data[key] = value

        return config_data

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration for non-interactive mode."""
        dir_name = self.target_dir.name
        return {
            "display_name": self._suggest_display_name(),
            "module_name": self._suggest_module_name(dir_name),
            "repo_name": self._suggest_repo_name(dir_name),
            "author": "TODO: Set author name",
            "conflicts": [],
            "targets": ["qt6"],
        }

    def _prompt(self, question: str, default: str, required: bool = True) -> str:
        """Prompt user for input with default value."""
        if default:
            prompt = f"{question} [{default}]: "
        else:
            prompt = f"{question}: "

        while True:
            response = input(prompt).strip()
            if response:
                return response
            elif default:
                return default
            elif not required:
                return ""
            else:
                print("This field is required. Please enter a value.")

    def _suggest_display_name(self) -> str:
        """Suggest a display name based on directory name."""
        dir_name = self.target_dir.name
        # Convert kebab-case or snake_case to Title Case
        words = re.sub(r"[-_]", " ", dir_name).split()
        return " ".join(word.capitalize() for word in words)

    def _suggest_module_name(self, display_name: str) -> str:
        """Suggest a Python module name based on display name."""
        # Convert to lowercase, replace spaces/hyphens with underscores
        name = re.sub(r"[^a-zA-Z0-9_]", "_", display_name.lower())
        # Remove multiple underscores and leading/trailing underscores
        name = re.sub(r"_+", "_", name).strip("_")
        # Ensure it starts with a letter
        if name and name[0].isdigit():
            name = f"addon_{name}"
        return name or "my_addon"

    def _suggest_repo_name(self, display_name: str) -> str:
        """Suggest a repository name based on display name."""
        # Convert to lowercase, replace spaces with hyphens
        name = re.sub(r"[^a-zA-Z0-9\-]", "-", display_name.lower())
        # Remove multiple hyphens and leading/trailing hyphens
        name = re.sub(r"-+", "-", name).strip("-")
        return name or "my-addon"

    def _create_project_structure(self, config: AddonConfig) -> None:
        """Create the standard project directory structure."""
        directories = [
            self.target_dir / "src" / config.module_name,
            self.target_dir / "ui" / "designer",
            self.target_dir / "ui" / "resources" / "icons" / "optional",
            self.target_dir / "docs",  # 可选文档目录
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _write_config_file(self, config_data: dict[str, Any]) -> None:
        """Write the addon.json configuration file."""
        with self.config_path.open("w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def _create_template_files(self, config: AddonConfig) -> None:
        """Create template Python files for the add-on."""
        src_dir = self.target_dir / "src" / config.module_name

        # Create __init__.py
        init_content = f'''"""
{config.display_name} - Anki Add-on

{config.author}
"""

from . import main

# Entry point for Anki
def init() -> None:
    """Initialize the add-on."""
    main.setup_addon()
'''

        (src_dir / "__init__.py").write_text(init_content, encoding="utf-8")

        # Create main.py
        main_content = f'''"""
Main module for {config.display_name}
"""

from aqt import mw
from aqt.utils import showInfo


def setup_addon() -> None:
    """Set up the add-on functionality."""
    # Add menu item
    action = mw.form.menuTools.addAction("{config.display_name}")
    action.triggered.connect(show_about)


def show_about() -> None:
    """Show information about the add-on."""
    showInfo(
        f"<h3>{config.display_name}</h3>"
        f"<p>Author: {config.author}</p>"
        f"<p>This is a template add-on created with AAB.</p>"
        f"<p>Edit the code in src/{config.module_name}/ "
        f"to customize functionality.</p>",
        title="{config.display_name}"
    )
'''

        (src_dir / "main.py").write_text(main_content, encoding="utf-8")

        # Create .gitignore
        gitignore_content = """# Build output
build/
dist/
*.ankiaddon

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
.env

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# AAB specific
.aab/
"""

        (self.target_dir / ".gitignore").write_text(gitignore_content, encoding="utf-8")

        # Create README.md
        readme_content = f"""# {config.display_name}

An Anki add-on created with [Anki Add-on Builder (AAB)](https://github.com/glutanimate/anki-addon-builder).

## Description

TODO: Add description of your add-on here.

## Installation

### From AnkiWeb

TODO: Add AnkiWeb installation instructions when published.

### Manual Installation

1. Download the latest release from GitHub
2. In Anki, go to Tools → Add-ons → Install from file
3. Select the downloaded .ankiaddon file

## Development

This project uses AAB for building and development.

### Setup

```bash
# Install dependencies (requires uv)
uv sync --extra qt6

# Build for local testing
uv run aab build -d local

# Build for AnkiWeb
uv run aab build -d ankiweb
```

### Project Structure

- `src/{config.module_name}/` - Main Python package
- `ui/designer/` - Qt Designer .ui files
- `ui/resources/` - UI resources (icons, styles, etc.)
- `docs/` - Documentation (optional)
- `addon.json` - Add-on configuration

## License

TODO: Add license information.

## Author

{config.author}
"""

        (self.target_dir / "README.md").write_text(readme_content, encoding="utf-8")

    def _ensure_target_directory(self) -> None:
        """Create target directory if it doesn't exist."""
        if not self.target_dir.exists():
            try:
                self.target_dir.mkdir(parents=True)
                print(f"Created directory: {self.target_dir}")
            except OSError as e:
                raise ProjectInitializationError(
                    f"Could not create directory '{self.target_dir}': {e}"
                ) from e
