# Anki Add-on Builder (AADT)

<a title="License: GNU AGPLv3" href="https://github.com/glutanimate/anki-addon-builder/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-GNU AGPLv3-green.svg"></a>
<a href="https://pypi.org/project/aadt/"><img src="https://img.shields.io/pypi/v/aadt.svg"></a>
<img src="https://img.shields.io/pypi/status/aadt.svg">

**A modern, Qt6-focused build tool for Anki add-ons with complete type safety and modern Python practices.**

English | [中文](README_ZH.md)

## 🚀 Features

- **Modern Python 3.12+** with full type annotations
- **Qt6-only support** for current Anki versions  
- **Fast dependency management** with uv
- **Code quality tools** with ruff and mypy integration
- **Comprehensive CLI** for all build operations
- **Manifest generation** for AnkiWeb and local distributions

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Commands](#commands)
- [Configuration](#configuration)
- [Development](#development)
- [Changelog](#changelog)
- [License](#license)

## 🔧 Installation

### Prerequisites

- **Python 3.12+** (required for modern type annotations)
- **uv** (recommended) or pip for dependency management

### Install from PyPI

```bash
# Basic installation
pip install aadt

# With Qt6 support for UI compilation
pip install aadt[qt6]

# Development installation with all tools
pip install aadt[dev]
```

### Install from source with uv (recommended)

```bash
# Clone and install
git clone https://github.com/glutanimate/anki-addon-builder.git
cd anki-addon-builder
uv sync

# With Qt6 support
uv sync --extra qt6

# Development setup
uv sync --extra dev
```

## ⚡ Quick Start

### 1. Initialize your add-on project

Use the `init` command to create a new project:

```bash
# Interactive setup (recommended)
aadt init my-awesome-addon

# Quick setup with defaults
aadt init my-awesome-addon -y

# Initialize in current directory
aadt init
```

This creates an `addon.json` configuration file and project structure:

```json
{
  "display_name": "My Awesome Add-on",
  "module_name": "my_addon", 
  "repo_name": "my-awesome-addon",
  "ankiweb_id": "123456789",
  "author": "Your Name",
  "conflicts": [],
  "targets": ["qt6"]
}
```

### 2. Project structure

```
my-addon/
├── addon.json          # Configuration
├── src/                # Source code
│   └── my_addon/       # Main module
├── ui/                 # UI-related files
│   ├── designer/       # Qt Designer .ui files
│   └── resources/      # UI resources (icons, styles)
└── docs/               # Documentation (optional)
```

### 3. Build your add-on

```bash
# Build for local testing
aadt build

# Build for AnkiWeb submission  
aadt build -d ankiweb

# Just compile UI files
aadt ui

# Generate manifest only
aadt manifest
```

## 📁 Project Structure

AADT follows a standardized project layout:

```
your-addon/
├── addon.json                 # Main configuration
├── src/                      # Source code directory
│   └── your_module/         # Python package
│       ├── __init__.py
│       ├── main.py
│       ├── gui/            # Generated UI files (auto-created)
│       │   ├── forms/      # Compiled .py forms
│       │   │   └── qt6/   # Qt6 compiled forms
│       │   └── __init__.py
│       └── resources/      # Auto-copied UI resources
│           ├── icons/
│           └── styles/
├── ui/                       # UI-related files
│   ├── designer/            # Qt Designer .ui files
│   │   ├── dialog.ui
│   │   └── settings.ui
│   └── resources/           # UI resources (source)
│       ├── icons/
│       │   └── optional/   # Additional icons
│       └── styles/         # Style files (optional)
├── docs/                    # Documentation (optional)
└── build/                  # Build output (auto-created)
    └── dist/              # Distribution files
```

## 🔨 Commands

### Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize new add-on project | `aadt init my-addon` |
| `build` | Full build and package | `aadt build -d local` |
| `ui` | Compile Qt Designer files | `aadt ui` |
| `manifest` | Generate manifest.json | `aadt manifest` |
| `clean` | Clean build artifacts | `aadt clean` |

### Advanced Commands

| Command | Description | Use Case |
|---------|-------------|----------|
| `create_dist` | Prepare source tree | CI/CD pipelines |
| `build_dist` | Build prepared source | Custom processing |
| `package_dist` | Package built files | Final packaging |

### Build Options

```bash
# Build specific distribution type
aadt build -d local      # Local development
aadt build -d ankiweb    # AnkiWeb submission
aadt build -d all        # Both distributions

# Specify version
aadt build v1.2.0        # Specific tag
aadt build dev           # Working directory  
aadt build current       # Latest commit
aadt build release       # Latest tag (default)

# Logging options
aadt build -v            # Verbose output (debug level)
aadt build -q            # Quiet mode (errors only)
aadt build               # Normal output (default)

# All tools run in uv-managed environment automatically
# Use uv run for consistent environment management
uv run aadt build -d local
uv run aadt ui
```

## ⚙️ Configuration

### addon.json Schema

```json
{
  "display_name": "Human-readable name",
  "module_name": "python_module_name", 
  "repo_name": "repository-name",
  "ankiweb_id": "AnkiWeb add-on ID",
  "author": "Author Name",
  "contact": "email@example.com",
  "homepage": "https://github.com/user/repo",
  "tags": "anki addon productivity",
  "conflicts": ["conflicting_addon_id"],
  "targets": ["qt6"],
  "min_anki_version": "2.1.50",
  "max_anki_version": "2.1.99", 
  "tested_anki_version": "2.1.66",
  "copyright_start": 2023,
  "ankiweb_conflicts_with_local": true,
  "local_conflicts_with_ankiweb": true,
  "build_config": {
    "output_dir": "build",
    "trash_patterns": ["*.pyc", "*.pyo", "__pycache__"],
    "license_paths": [".", "resources"],
    "archive_exclude_patterns": [".git", "__pycache__", "*.pyc", "build", "dist"],
    "ui_config": {
      "ui_dir": "ui",
      "designer_dir": "designer",
      "resources_dir": "resources",
      "forms_package": "forms",
      "exclude_optional_resources": false
    }
  }
}
```

### Required Fields

- `display_name`: Add-on name shown to users
- `module_name`: Python module/package name  
- `repo_name`: Repository/file name
- `ankiweb_id`: AnkiWeb add-on identifier
- `author`: Author name
- `conflicts`: List of conflicting add-on IDs
- `targets`: Must be `["qt6"]` (Qt5 no longer supported)

### Optional Build Configuration

The optional `build_config` section allows customization of the build process:

#### General Build Settings
- `output_dir` (default: `"build"`): Directory where build artifacts are stored
- `trash_patterns` (default: `["*.pyc", "*.pyo", "__pycache__"]`): File patterns to clean during build
- `license_paths` (default: `[".", "resources"]`): Paths to search for LICENSE files
- `archive_exclude_patterns` (default: includes common dev files): File patterns to exclude when archiving in non-Git environments

#### UI Configuration (`ui_config`)
- `ui_dir` (default: `"ui"`): Directory containing UI-related files
- `designer_dir` (default: `"designer"`): Directory containing Qt Designer .ui files
- `resources_dir` (default: `"resources"`): Directory containing UI resources
- `forms_package` (default: `"forms"`): Python package name for compiled forms
- `exclude_optional_resources` (default: `false`): Whether to exclude optional resources from build

Example with custom build settings:
```json
{
  "display_name": "My Add-on",
  "module_name": "my_addon",
  "repo_name": "my-addon",
  "ankiweb_id": "123456789",
  "author": "Your Name",
  "conflicts": [],
  "targets": ["qt6"],
  "build_config": {
    "output_dir": "releases",
    "trash_patterns": ["*.pyc", "*.pyo", "__pycache__", "*.log", "tmp/"],
    "license_paths": [".", "docs", "legal"],
    "archive_exclude_patterns": ["*.log", "temp/", ".idea/", "*.backup"],
    "ui_config": {
      "ui_dir": "interface",
      "designer_dir": "qt_designs",
      "resources_dir": "assets",
      "forms_package": "ui_forms",
      "exclude_optional_resources": true
    }
  }
}
```

## 🎨 UI Development Workflow

### Working with Qt Designer

AADT provides seamless integration with Qt Designer for UI development:

1. **Design your UI**: Create `.ui` files in `ui/designer/`
2. **Add resources**: Place images, icons in `ui/resources/`
3. **Reference resources**: In Qt Designer, reference files from `ui/resources/`
4. **Build UI**: Run `aadt ui` to compile and copy resources automatically

```bash
# Your project structure
my-addon/
├── ui/
│   ├── designer/
│   │   └── dialog.ui          # References ../resources/icon.png
│   └── resources/
│       └── icon.png           # Your resource file
└── src/my_addon/

# After running 'aadt ui'
my-addon/
├── src/my_addon/
│   ├── gui/forms/qt6/
│   │   └── dialog.py          # Compiled UI
│   └── resources/
│       └── icon.png           # Auto-copied resource
```

**Key Benefits:**
- ✅ **Automatic resource copying**: Resources are automatically copied to the final package
- ✅ **Clean references**: No need for complex QRC compilation
- ✅ **Direct file paths**: Use standard file paths in your Python code
- ✅ **Development friendly**: Resources are immediately available for testing

## 🛠️ Development

### Modern Python Features

AADT uses modern Python 3.12+ features:

```python
# Union types with |
def parse_version(version: str | None) -> str:
    return version or "latest"

# Modern list/dict annotations  
config: dict[str, Any] = load_config()
files: list[Path] = find_ui_files()

# Match statements (Python 3.12+)
match build_type:
    case "local":
        return build_local()
    case "ankiweb": 
        return build_ankiweb()
```

### Code Quality

AADT includes modern development tools:

```bash
# Linting with ruff
uv run ruff check aadt/
uv run ruff format aadt/

# Type checking with mypy  
uv run mypy aadt/

# Run all checks
uv run ruff check aadt/ && uv run mypy aadt/
```

### Testing

```bash
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=aadt
```

## 📈 Changelog

### v1.0.0-dev.5 (Current)

**🎯 Major Modernization Release**

#### ✨ New Features
- **Modern Python 3.12+** with full type annotations
- **uv-based dependency management** for faster builds
- **Qt6-only architecture** (Qt5 support removed)
- **Comprehensive type safety** with mypy validation
- **Modern code formatting** with ruff
- **True Git-optional support** with intelligent fallback systems
- **Enhanced CLI** with verbose/quiet modes and unified error handling
- **Configurable UI compilation** with customizable paths and resource handling
- **Flexible archiving** with user-configurable exclude patterns

#### 🗑️ Removed (Breaking Changes)
- **Qt5 support** - Use Qt6 for modern Anki versions
- **QRC resource files** - Use direct file paths instead
- **Poetry dependency** - Migrated to uv
- **Legacy migration code** - Cleaner, simpler codebase
- **Pyenv parameters** - Use uv's automatic environment management

#### 🔧 Technical Improvements
- **Dataclass-based configuration** with type safety and automatic nesting
- **Modern pathlib usage** throughout all modules
- **Unified error handling** with exception chaining and meaningful messages
- **Simplified UI building** without legacy compatibility
- **VersionManager architecture** with automatic Git/filesystem fallback
- **Performance optimizations** in file operations and import handling
- **Generic nested dataclass parsing** for extensible configuration

#### 📝 Migration Guide
For existing projects:
1. Update `targets` to `["qt6"]` only
2. Remove any `.qrc` files (use direct file paths)
3. Update Python requirement to 3.12+
4. Remove `qt_resource_migration_mode` from config
5. Remove `--pyenv` arguments from build scripts (use uv environment management)

## 🎯 Design Philosophy

AADT follows these principles:

1. **Modern Python First**: Uses latest language features (3.12+)
2. **Type Safety**: Complete type annotations and mypy validation
3. **Qt6 Focus**: No legacy Qt5 baggage, designed for current Anki
4. **Fast Builds**: uv-based dependency management
5. **Developer Experience**: Clear CLI, good error messages, helpful validation

## 🔧 Platform Support

- **Linux**: Full support ✅
- **macOS**: Full support ✅  
- **Windows**: Basic support (POSIX-like environment recommended)

## 🚀 Git Integration & Alternatives

AADT is designed to work optimally with Git repositories but **does not require Git**:

### Git Available (Recommended)
- **Version detection**: Uses Git tags and commits for versioning
- **Source archiving**: Uses `git archive` for clean source extraction
- **Modification time**: Uses Git commit timestamps

### Non-Git Environment (Fallback)
- **Version detection**: Reads from `pyproject.toml`, `VERSION` files, or generates timestamp-based versions
- **Source archiving**: Copies current directory with smart exclusions (`.git`, `__pycache__`, etc.)
- **Modification time**: Uses current timestamp

### Usage Examples

```bash
# In Git repository (automatic detection)
aadt build -d local

# In non-Git directory (automatic fallback)
aadt build -d local  # Still works!

# Explicit version specification (works anywhere)
aadt build v1.2.0 -d local
```

The tool automatically detects your environment and chooses the appropriate method.

## 📚 Examples

See the `tests/` directory for example configurations and usage patterns.

## 🤝 Contributing

1. Ensure Python 3.12+ is installed
2. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. Clone and setup: `git clone ... && cd ... && uv sync --extra dev`
4. Make changes and test: `uv run ruff check && uv run mypy aab/`
5. Submit a pull request

## 🔄 Why This Modernized Version?

### Key Advantages

- **Faster builds**: uv is ~10x faster than Poetry
- **Better type safety**: Complete mypy coverage
- **Simplified architecture**: Qt5 baggage removed, Qt6-focused
- **Modern Python**: Uses 3.12+ latest features
- **Cleaner codebase**: No legacy compatibility logic

### Use Cases

- 🎯 **New projects**: Starting fresh Anki add-ons from scratch
- 🔄 **Existing project modernization**: Want to upgrade to modern toolchain
- 📊 **Type safety requirements**: Projects needing complete type checking
- ⚡ **Fast development**: Need rapid build and iteration cycles

## 🚀 Workflow Examples

### Typical Development Flow

```bash
# 1. Initialize new add-on project
uv run aadt init my-anki-addon
cd my-anki-addon

# 2. Customize configuration (optional)
# Edit addon.json to modify settings

# 3. Add your code
# Edit files in src/my_anki_addon/

# 4. Build for testing
uv run aadt build -d local

# 5. Code quality checks
uv run ruff check src/
uv run mypy src/
```

### CI/CD Integration

```yaml
# GitHub Actions example
name: Build Anki Add-on
on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v1
      with:
        version: "latest"
    - run: uv sync --extra dev
    - run: uv run ruff check aadt/
    - run: uv run mypy aadt/
    - run: uv run aadt build -d all
```

## 📄 License

This project is licensed under the GNU AGPLv3. See [LICENSE](LICENSE) for details.

---

**Built with ❤️ for the Anki community**

> This modernized version focuses on providing the best development experience for Anki add-on creators using the latest Python technology stack and best practices.