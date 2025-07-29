Here is the English translation of the README.md file:

---

```markdown
# CreateFile with Designated Encoding ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/stv_create_file)](https://pypi.org/project/stv_create_file/)
[![Python Versions](https://img.shields.io/pypi/pyversions/stv_create_file)](https://pypi.org/project/stv_create_file/)

[中文](./README.md)

**CreateFile with Designated Encoding** is a powerful command-line tool for creating files with specified encoding formats, supporting custom metadata tags and multi-language prompts.

> Create files with your specified encoding

## 🌟 Core Features

- **Specify File Encoding** - Create files in UTF-8, GBK, Big5, and other encoding formats
- **Metadata Tags** - Customize metadata format in the first line of files
- **Multi-language Support** - Auto-adapt to Chinese/English interfaces
- **Encoding Verification** - Automatically detect file encoding after creation
- **Exclusive Mode** - Prevent accidental overwriting of existing files
- **Verbose Logging** - Optional verbose output mode
- **User Configuration** - Save preferences to config files
- **Author Information** - Add author attribution in metadata
- **Changelog** - View version update history

## 🚀 Installation

### Install via PyPI

```bash
pip install stv_create_file
```

### Install from GitHub Source

```bash
git clone https://github.com/StarWindv/CreateFile-with-DesignatedEncoding.git
cd CreateFile-with-DesignatedEncoding
pip install .
```

## 🛠 Usage Guide

### Basic Commands

```bash
create [file_path] [options]
nf [file_path] [options]      # Short for newfile
newfile [file_path] [options] # Full command
```

### Command Options

| Option           | Shortcut | Default | Description                        |
|------------------|----------|---------|------------------------------------|
| `--encoding`     | `-e`     | `utf-8` | File encoding format               |
| `--prefix`       | `-p`     | `#`     | First line prefix                  |
| `--left-paren`   | `-l`     | `<\|`   | Left metadata tag                  |
| `--right-paren`  | `-r`     | `\|>`   | Right metadata tag                 |
| `--add-author`   | `-a`     | `''`    | Add author info in metadata        |
| `--monopolize`   | `-m`     | `False` | Exclusive mode (prevent overwrite) |
| `--coding-check` | `-cc`    | `False` | Verify encoding after creation     |
| `--verbose`      | `-v`     | `False` | Verbose output mode                |
| `--version`      | `-V`     | -       | Show version information           |
| `--license`      |          | -       | Show project license               |
| `--whats-new`    |          | -       | Show program changelog             |
| `--set-language` | `-sl`    |         | Set prompt language (zh-cn/en-uk)  |

### Usage Examples

1. **Create Basic File**

   ```bash
   create example.txt
   ```

2. **Specify File Encoding**

   ```bash
   nf data.csv -e gbk
   ```

3. **Custom Metadata Format**

   ```bash
   newfile config.ini -p "// " -l "{{" -r "}}"
   ```

4. **Create in Exclusive Mode**

   ```bash
   create important.log -m
   ```

5. **Create and Verify Encoding**

   ```bash
   nf report.txt -e utf-8-sig -cc -v
   ```

6. **Add Author Information**

   ```bash
   nf poem.txt -a "Li Bai"
   ```

7. **View Changelog**

   ```bash
   newfile --whats-new latest
   ```

8. **Switch to English Interface**

   ```bash
   create -sl english
   ```

### Special Notes

1. **Adding Newlines in Metadata Tags**

   ```bash
   nf test.txt -l "#n<| " -p ""
   ```

## ⚙️ Configuration File

Configuration path: `~/.stv_project/config.json`

**Default Configuration:**

```json
{
    "lang": "zh-cn",
    "verbose": false
}
```

**Configurable Options:**

- `lang`: Interface language (`zh-cn`/`en-uk`)
- `verbose`: Enable verbose output by default

## 📂 Project Structure

```
CreateFile-with-DesignatedEncoding/
├── LICENSE
├── pyproject.toml
├── README.md
├── README.en.md
└── src/
    └── stv_create_file/
        ├── core/
        │   ├── __init__.py
        │   ├── FileCreator.py    # Core file creation logic
        │   └── stv_parse.py      # Command-line argument parsing
        ├── main.py               # Program entry point
        ├── mul_lang/             # Multi-language support
        │   ├── __init__.py
        │   └── change_text.py    
        └── utils/
            ├── __init__.py
            ├── GetConfig.py      # Configuration management
            └── utils.py          # Utility functions
```

## 📦 Dependencies

- `chardet` - File encoding detection library

## 📜 License

This project is licensed under the [MIT License](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding/blob/main/LICENSE)

## 🤝 Contributing

Contributions via Issues or Pull Requests are welcome!  
Project Repository: [GitHub Repository](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding)
```