# Anki 插件构建工具 (AADT)

<a title="协议: GNU AGPLv3" href="https://github.com/glutanimate/anki-addon-builder/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-GNU AGPLv3-green.svg"></a>
<a href="https://pypi.org/project/aadt/"><img src="https://img.shields.io/pypi/v/aadt.svg"></a>
<img src="https://img.shields.io/pypi/status/aadt.svg">

**现代化的、专注Qt6的Anki插件构建工具，具备完整类型安全和现代Python实践。**

[English](README.md) | 中文

## 🚀 特性

- **现代Python 3.10+** 完整类型注解支持
- **Qt6专用支持** 适配当前Anki版本  
- **快速依赖管理** 基于uv构建
- **代码质量工具** 集成ruff和mypy
- **全面的CLI** 覆盖所有构建操作
- **清单文件生成** 支持AnkiWeb和本地分发

## 📋 目录

- [安装](#安装)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [命令](#命令)
- [配置](#配置)
- [开发](#开发)
- [更新日志](#更新日志)
- [协议](#协议)

## 🔧 安装

### 前置要求

- **Python 3.10+** (现代类型注解必需)
- **uv** (推荐) 或 pip 用于依赖管理

### 从PyPI安装

```bash
# 基础安装
pip install aadt

# 包含Qt6支持的UI编译功能
pip install aadt[qt6]

# 开发安装，包含所有工具
pip install aadt[dev]
```

### 从源码安装（推荐使用uv）

```bash
# 克隆并安装
git clone https://github.com/glutanimate/anki-addon-builder.git
cd anki-addon-builder
uv sync

# 包含Qt6支持
uv sync --extra qt6

# 开发环境设置
uv sync --extra dev
```

## ⚡ 快速开始

### 1. 初始化插件项目

使用 `init` 命令创建新项目：

```bash
# 交互式设置（推荐）
aadt init my-awesome-addon

# 使用默认值快速设置
aadt init my-awesome-addon -y

# 在当前目录初始化
aadt init
```

这会创建 `addon.json` 配置文件和项目结构：

```json
{
  "display_name": "我的超棒插件",
  "module_name": "my_addon", 
  "repo_name": "my-awesome-addon",
  "ankiweb_id": "123456789",
  "author": "你的名字",
  "conflicts": [],
  "targets": ["qt6"]
}
```

### 2. 项目结构

```
my-addon/
├── addon.json          # 配置文件
├── src/                # 源代码
│   └── my_addon/       # 主模块
├── ui/                 # UI相关文件
│   ├── designer/       # Qt Designer .ui 文件
│   └── resources/      # UI资源（图标、样式）
└── docs/               # 文档（可选）
```

### 3. 构建插件

```bash
# 本地测试构建
aadt build

# AnkiWeb提交构建  
aadt build -d ankiweb

# 仅编译UI文件
aadt ui

# 仅生成清单文件
aadt manifest
```

## 📁 项目结构

AADT遵循标准化的项目布局：

```
your-addon/
├── addon.json                 # 主配置文件
├── src/                      # 源代码目录
│   └── your_module/         # Python包
│       ├── __init__.py
│       ├── main.py
│       ├── gui/            # 生成的UI文件（自动创建）
│       │   ├── forms/      # 编译的.py表单
│       │   │   └── qt6/   # Qt6编译表单
│       │   └── __init__.py
│       └── resources/      # 自动复制的UI资源
│           ├── icons/
│           └── styles/
├── ui/                       # UI相关文件
│   ├── designer/            # Qt Designer .ui文件
│   │   ├── dialog.ui
│   │   └── settings.ui
│   └── resources/           # UI资源（源文件）
│       ├── icons/
│       │   └── optional/   # 额外图标
│       └── styles/         # 样式文件（可选）
├── docs/                    # 文档（可选）
└── build/                  # 构建输出（自动创建）
    └── dist/              # 分发文件
```

## 🔨 命令

### 核心命令

| 命令 | 描述 | 示例 |
|---------|-------------|---------|
| `init` | 初始化新插件项目 | `aadt init my-addon` |
| `build` | 完整构建和打包 | `aadt build -d local` |
| `ui` | 编译Qt Designer文件 | `aadt ui` |
| `manifest` | 生成manifest.json | `aadt manifest` |
| `clean` | 清理构建文件 | `aadt clean` |

### 高级命令

| 命令 | 描述 | 用途 |
|---------|-------------|----------|
| `create_dist` | 准备源代码树 | CI/CD流水线 |
| `build_dist` | 构建准备好的源码 | 自定义处理 |
| `package_dist` | 打包构建文件 | 最终打包 |

### 构建选项

```bash
# 构建特定分发类型
aadt build -d local      # 本地开发
aadt build -d ankiweb    # AnkiWeb提交
aadt build -d all        # 两种分发类型

# 指定版本
aadt build v1.2.0        # 特定标签
aadt build dev           # 工作目录  
aadt build current       # 最新提交
aadt build release       # 最新标签（默认）

# uv自动管理环境
uv run aadt build -d local
uv run aadt ui
```

## ⚙️ 配置

### addon.json 模式

```json
{
  "display_name": "用户可读名称",
  "module_name": "python_模块名", 
  "repo_name": "仓库名称",
  "ankiweb_id": "AnkiWeb插件ID",
  "author": "作者姓名",
  "contact": "email@example.com",
  "homepage": "https://github.com/user/repo",
  "tags": "anki addon productivity",
  "conflicts": ["冲突插件ID"],
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
    "license_paths": [".", "resources"]
  }
}
```

### 必需字段

- `display_name`: 显示给用户的插件名称
- `module_name`: Python模块/包名称  
- `repo_name`: 仓库/文件名
- `ankiweb_id`: AnkiWeb插件标识符
- `author`: 作者姓名
- `conflicts`: 冲突插件ID列表
- `targets`: 必须是 `["qt6"]` (不再支持Qt5)

### 可选的构建配置

可选的 `build_config` 部分允许自定义构建过程：

- `output_dir` (默认: `"build"`): 存储构建产物的目录
- `trash_patterns` (默认: `["*.pyc", "*.pyo", "__pycache__"]`): 构建时清理的文件模式
- `license_paths` (默认: `[".", "resources"]`): 搜索许可证文件的路径

自定义构建设置示例：
```json
{
  "display_name": "我的插件",
  "module_name": "my_addon",
  "repo_name": "my-addon",
  "ankiweb_id": "123456789",
  "author": "你的名字",
  "conflicts": [],
  "targets": ["qt6"],
  "build_config": {
    "output_dir": "releases",
    "trash_patterns": ["*.pyc", "*.pyo", "__pycache__", "*.log", "tmp/"],
    "license_paths": [".", "docs", "legal"]
  }
}
```

## 🎨 UI开发工作流程

### 使用Qt Designer

AADT为Qt Designer UI开发提供无缝集成：

1. **设计UI**: 在 `ui/designer/` 中创建 `.ui` 文件
2. **添加资源**: 将图片、图标放在 `ui/resources/` 中
3. **引用资源**: 在Qt Designer中引用 `ui/resources/` 中的文件
4. **构建UI**: 运行 `aadt ui` 自动编译并复制资源

```bash
# 你的项目结构
my-addon/
├── ui/
│   ├── designer/
│   │   └── dialog.ui          # 引用 ../resources/icon.png
│   └── resources/
│       └── icon.png           # 你的资源文件
└── src/my_addon/

# 运行 'aadt ui' 后
my-addon/
├── src/my_addon/
│   ├── gui/forms/qt6/
│   │   └── dialog.py          # 编译后的UI
│   └── resources/
│       └── icon.png           # 自动复制的资源
```

**主要优势：**
- ✅ **自动资源复制**: 资源文件自动复制到最终包中
- ✅ **清洁引用**: 无需复杂的QRC编译
- ✅ **直接文件路径**: 在Python代码中使用标准文件路径
- ✅ **开发友好**: 资源立即可用于测试

## 🛠️ 开发

### 现代Python特性

AADT使用现代Python 3.10+特性：

```python
# 使用 | 的联合类型
def parse_version(version: str | None) -> str:
    return version or "latest"

# 现代list/dict注解  
config: dict[str, Any] = load_config()
files: list[Path] = find_ui_files()

# match语句 (Python 3.10+)
match build_type:
    case "local":
        return build_local()
    case "ankiweb": 
        return build_ankiweb()
```

### 代码质量

AADT包含现代开发工具：

```bash
# 使用ruff进行代码检查
uv run ruff check aadt/
uv run ruff format aadt/

# 使用mypy进行类型检查  
uv run mypy aadt/

# 运行所有检查
uv run ruff check aadt/ && uv run mypy aadt/
```

### 测试

```bash
# 运行测试
uv run pytest

# 包含覆盖率
uv run pytest --cov=aadt
```

## 📈 更新日志

### v1.0.0-dev.5 (当前版本)

**🎯 重大现代化版本**

#### ✨ 新特性
- **现代Python 3.10+** 完整类型注解
- **基于uv的依赖管理** 更快的构建
- **Qt6专用架构** （移除Qt5支持）
- **全面类型安全** mypy验证
- **现代代码格式化** 使用ruff
- **真正的Git可选支持** 智能后备系统
- **增强的CLI** 详细/静默模式和统一错误处理
- **可配置UI编译** 自定义路径和资源处理
- **灵活的归档** 用户可配置的排除模式

#### 🗑️ 移除内容（破坏性更改）
- **Qt5支持** - 现代Anki版本请使用Qt6
- **QRC资源文件** - 使用直接文件路径替代
- **Poetry依赖** - 迁移到uv
- **遗留迁移代码** - 更清洁、简单的代码库
- **Pyenv参数** - 使用uv的自动环境管理

#### 🔧 技术改进
- **基于数据类的配置** 类型安全和自动嵌套
- **现代pathlib使用** 贯穿所有模块
- **统一错误处理** 异常链和有意义的错误信息
- **简化的UI构建** 无遗留兼容性
- **VersionManager架构** 自动Git/文件系统后备
- **性能优化** 文件操作和导入处理
- **通用嵌套数据类解析** 可扩展配置

#### 📝 迁移指南
对于现有项目：
1. 将 `targets` 更新为仅 `["qt6"]`
2. 移除任何 `.qrc` 文件（使用直接文件路径）
3. 将Python要求更新到3.10+
4. 从配置中移除 `qt_resource_migration_mode`
5. 从构建脚本中移除 `--pyenv` 参数（使用uv环境管理）

## 🎯 设计理念

AAB遵循以下原则：

1. **现代Python优先**: 使用最新语言特性 (3.10+)
2. **类型安全**: 完整类型注解和mypy验证
3. **Qt6专注**: 无Qt5历史包袱，为当前Anki设计
4. **快速构建**: 基于uv的依赖管理
5. **开发体验**: 清晰的CLI、良好的错误信息、有用的验证

## 🔧 平台支持

- **Linux**: 完全支持 ✅
- **macOS**: 完全支持 ✅  
- **Windows**: 基础支持（推荐类POSIX环境）

## 🚀 Git 集成与替代方案

AAB 设计为在 Git 仓库中工作最佳，但**不需要 Git**：

### Git 可用时（推荐）
- **版本检测**: 使用 Git 标签和提交进行版本控制
- **源码归档**: 使用 `git archive` 进行干净的源码提取
- **修改时间**: 使用 Git 提交时间戳

### 非Git环境（降级模式）
- **版本检测**: 从 `pyproject.toml`、`VERSION` 文件读取，或生成基于时间戳的版本
- **源码归档**: 复制当前目录并智能排除（`.git`、`__pycache__` 等）
- **修改时间**: 使用当前时间戳

### 使用示例

```bash
# 在 Git 仓库中（自动检测）
aab build -d local

# 在非 Git 目录中（自动降级）
aab build -d local  # 仍然可以工作！

# 显式版本指定（任何地方都可以工作）
aab build v1.2.0 -d local
```

工具会自动检测你的环境并选择适当的方法。

## 📚 示例

查看 `tests/` 目录获取示例配置和使用模式。

## 🤝 贡献

1. 确保安装Python 3.10+
2. 安装uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
3. 克隆并设置: `git clone ... && cd ... && uv sync --extra dev`
4. 进行更改并测试: `uv run ruff check && uv run mypy aab/`
5. 提交pull request

## 🔄 与原版的区别

### 为什么选择这个现代化版本？

- **更快的构建**: uv比Poetry快约10倍
- **更好的类型安全**: 完整的mypy覆盖
- **简化的架构**: 移除Qt5包袱，专注Qt6
- **现代Python**: 使用3.10+的最新特性
- **更清洁的代码**: 无历史遗留逻辑

### 适用场景

- 🎯 **新项目**: 从零开始的Anki插件
- 🔄 **现有项目现代化**: 想要升级到现代工具链
- 📊 **类型安全需求**: 需要完整类型检查的项目
- ⚡ **快速开发**: 需要快速构建和迭代

## 🚀 工作流程示例

### 典型开发流程

```bash
# 1. 初始化新插件项目
uv run aab init my-anki-addon
cd my-anki-addon

# 2. 自定义配置（可选）
# 编辑 addon.json 修改配置

# 3. 添加你的代码
# 编辑 src/my_anki_addon/ 中的文件

# 4. 构建测试
uv run aab build -d local

# 5. 代码质量检查
uv run ruff check src/
uv run mypy src/
```

### CI/CD集成

```yaml
# GitHub Actions示例
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
    - run: uv run ruff check aab/
    - run: uv run mypy aab/
    - run: uv run aab build -d all
```

## 📄 协议

本项目基于GNU AGPLv3协议。详见[LICENSE](LICENSE)文件。

---

**为Anki社区用❤️构建**

> 这个现代化版本专注于为Anki插件开发者提供最佳的开发体验，采用最新的Python技术栈和最佳实践。