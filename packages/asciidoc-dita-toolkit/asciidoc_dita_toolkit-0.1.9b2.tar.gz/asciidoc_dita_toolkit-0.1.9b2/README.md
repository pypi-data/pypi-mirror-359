# AsciiDoc DITA Toolkit

[![PyPI version](https://badge.fury.io/py/asciidoc-dita-toolkit.svg)](https://badge.fury.io/py/asciidoc-dita-toolkit)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Command-line toolkit for technical writers to review and fix AsciiDoc content for DITA-based publishing workflows.

## 🚀 Quick Start

**PyPI installation:**
```sh
pip install asciidoc-dita-toolkit
adt --help                    # CLI interface
```

**Container usage:**
```sh
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest --help
```

## 📖 What does it do?

- **Fix common issues** in `.adoc` files before publishing
- **Apply automated checks** and transformations via plugins
- **Ensure consistency** across large documentation projects
- **Integrate** with existing documentation workflows

## 📦 Installation

### Option 1: Container (No Python Required)

```sh
# Standard container image (includes dev tools)
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit:latest --help

# Test the container
docker run --rm rolfedh/asciidoc-dita-toolkit:latest --version
```

**Benefits of container approach:**

- No need to install Python or manage dependencies
- Consistent environment across different systems
- Easy to use in CI/CD pipelines
- Automatic cleanup after each run

### Option 2: PyPI

Install the toolkit using pip:

```sh
python3 -m pip install asciidoc-dita-toolkit

# Test the installation
adt --help¹
```

### Upgrading

**Container:**

```sh
# Production image (recommended for most users)
docker pull rolfedh/asciidoc-dita-toolkit-prod:latest

# Development image (includes dev tools)
docker pull rolfedh/asciidoc-dita-toolkit:latest
```

**PyPI:**

```sh
python3 -m pip install --upgrade asciidoc-dita-toolkit
```

### Requirements

- Python 3.7 or newer
- No external dependencies (uses only Python standard library)

## 🔧 Usage

### Command Line Interface

For automation, scripting, or advanced usage:

### List available plugins

```sh
adt --list-plugins¹
```

### Run a plugin

```sh
adt <plugin> [file_or_dir] [options]¹
```

- `<plugin>`: Name of the plugin to run (e.g., `EntityReference`, `ContentType`)
- `[file_or_dir]`: File or directory to process (auto-detected)
- `[options]`: Plugin-specific options (e.g., `-nr` to disable recursive processing)

### Common Options

All plugins support these options:

- **Auto-detection**: Automatically detects files vs directories - no flags needed
- `-nr` or `--no-recursive`: Process directory non-recursively (single level only)
- **Recursive by default**: Directory paths are processed recursively by default

### 📝 Examples

#### Fix HTML entity references in a single file

```sh
adt EntityReference path/to/file.adoc¹
```

#### Add content type labels (processes current directory recursively by default)

```sh
adt ContentType .¹
```

#### Process all .adoc files in a specific directory (recursive by default)

```sh
adt EntityReference docs/¹
```

#### Process directory non-recursively (single level only)

```sh
adt ContentType docs/ -nr¹
```

### Container Usage

```sh
# List plugins
docker run --rm rolfedh/asciidoc-dita-toolkit-prod:latest --list-plugins

# Fix entity references in current directory
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest EntityReference .

# Add content type labels to a specific file
docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest ContentType docs/myfile.adoc
```

**Tip:** Create a shell alias to simplify container usage:

```sh
alias adt='docker run --rm -v $(pwd):/workspace rolfedh/asciidoc-dita-toolkit-prod:latest'
```

Then use it exactly like the PyPI version:

```sh
adt --list-plugins
adt EntityReference .
```

## 🔌 Available Plugins

| Plugin | Description | Example Usage |
|--------|-------------|---------------|
| `EntityReference` | Replace unsupported HTML character entity references with AsciiDoc attribute references | `adt EntityReference file.adoc`¹ |
| `ContentType` | Add `:_mod-docs-content-type:` labels with smart analysis, interactive prompts, deprecated attribute conversion, and filename-based auto-detection | `adt ContentType docs/`¹ |

> **📋 Technical Details**: For plugin internals and supported entity mappings, see [docs/asciidoc-dita-toolkit.md](docs/asciidoc-dita-toolkit.md).

## 🔍 Troubleshooting

- **Python Version**: Make sure you are using Python 3.7 or newer
- **Installation Issues**: Try upgrading pip: `python3 -m pip install --upgrade pip`
- **Development Setup**: If you need to use a local clone, see the [contributor guide](docs/CONTRIBUTING.md)

## 📚 Resources

- [PyPI: asciidoc-dita-toolkit](https://pypi.org/project/asciidoc-dita-toolkit/)
- [GitHub repository](https://github.com/rolfedh/asciidoc-dita-toolkit)
- [Documentation](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/)
- [Contributing Guide](https://github.com/rolfedh/asciidoc-dita-toolkit/blob/main/docs/CONTRIBUTING.md)
- [asciidoctor-dita-vale](https://github.com/jhradilek/asciidoctor-dita-vale): Vale style rules and test fixtures

## 🤝 Contributing

Want to add new plugins or help improve the toolkit?

- Read our [Contributing Guide](docs/CONTRIBUTING.md)
- Follow the [Plugin Development Pattern](docs/PLUGIN_DEVELOPMENT_PATTERN.md) for new plugins
- Check out [open issues](https://github.com/rolfedh/asciidoc-dita-toolkit/issues)
- See our [Security Policy](SECURITY.md) for reporting vulnerabilities

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

¹ The command `adt` is a convenient alias for the full command `asciidoc-dita-toolkit`.