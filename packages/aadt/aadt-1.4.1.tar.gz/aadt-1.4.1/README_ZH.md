# Anki Add-on Dev ToolKit (AADT)

<a title="协议: GNU AGPLv3" href="https://github.com/glutanimate/anki-addon-builder/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-GNU AGPLv3-green.svg"></a>
<a href="https://pypi.org/project/aadt/"><img src="https://img.shields.io/pypi/v/aadt.svg"></a>
<img src="https://img.shields.io/pypi/status/aadt.svg">

**现代化的、专注于 Anki 新版本（2025.06+）的插件开发和构建工具包，具备完整类型安全和现代 Python 实践。**

[English](README.md) | 中文

## 🚀 特性

- **Python 3.13** 与 Anki 2025.06+ 保持一致
- **Qt6 专用支持** 适配 Anki 2025.06+ 版本  
- **优雅依赖管理** 完全基于 uv 管理环境和依赖
- **代码质量工具** 集成 ruff 和 mypy 提升代码质量
- **全面的 CLI 命令** 覆盖从初始化到发布的全流程
- **便捷构建和分发** 支持 AnkiWeb 和本地分发

## 📋 目录

- [前置要求](#前置要求)
- [快速开始](#快速开始)
- [命令详解](#命令详解)
- [CI/CD支持](#CI/CD支持)
- [UI开发](#UI开发)
- [代码质量](#代码质量)
- [单元测试](#单元测试)
- [Git 集成](#Git集成)
- [更新日志](#更新日志)
- [协议](#协议)

## 🔧 前置要求

通过 `curl -LsSf https://astral.sh/uv/install.sh | sh` 在本地安装 uv。

## ⚡ 快速开始

### 1. 初始化插件项目

使用 `uvx` 方式使用最新版本运行 `init` 命令快速初始化项目：

```bash
# 创建目录
mkdir my-awesome-addon
cd my-awesome-addon

# 交互式设置
uvx aadt init
```

默认的初始化会创建一个基础但完整的插件项目，包括：

- 通过交互方式搜集插件信息
- 应用模板文件，生成项目结构
- 通过 uv 配置开发环境并安装依赖
- 创建 git 仓库并初始化

初始化完成之后，项目的目录结构如下：

```
my-awesome-addon/
├── addon.json          # Addon 配置文件
├── src/                # 源代码
│   └── my_addon/       # 主模块
├── ui/                 # UI 设计
│   ├── designer/       # Qt Designer .ui 文件
│   └── resources/      # UI 资源（图标、样式）
├── README.md           # 项目说明
├── README_ZH.md        # 中文版说明
├── LICENSE             # 许可证
├── .git/               # Git仓库
├── .gitignore          # 忽略文件
├── .python-version     # 指定Python版本
├── pyproject.toml      # 项目配置
└── uv.lock             # uv 锁定文件

```

### 2. 开发

本项目使用 uv 管理 Python 环境，并使用 uv 的锁定文件 `uv.lock` 来管理依赖。

项目中自动配置了 `ruff` 和 `mypy` 的检查和格式化，并配置了 `pytest` 的测试框架。

TODO： 待补充

### 3. 测试

为了方便开发环境下的测试，AADT 提供了 `test` 命令，用于在 Anki 中进行插件的测试。

```bash
uv run aadt test
```

运行 `test` 命令会先将 `src/` 目录下的项目文件夹软链接到 Anki 的插件目录，然后自动启动 Anki 并加载插件。

同时，AADT 还提供了 `link` 命令，用于管理项目源代码文件夹软链接到 Anki 插件目录的操作。

```bash
# 创建软链接
uv run aadt link

# 删除软链接
uv run aadt link --unlink
```

### 4. 构建

AADT 提供了 `build` 命令，用于构建插件。

```bash
uv run aadt build
```

构建命令依赖于 git 仓库，默认会查找最新的 git tag 并构建对应的 commit 版本，便于将测试版本和正式版本区分。

生成的插件包会存储在 `dist` 目录下，可以用于直接安装或者上传到 AnkiWeb 进行分发。

## 🔧 命令详解

### `init` - 初始化插件项目
```bash
# 在当前目录初始化（交互式）
uv run aadt init

# 在指定目录初始化
uv run aadt init my-addon

# 使用默认值（非交互式）
uv run aadt init -y
```

**功能：**
- 交互式收集插件信息（名称、作者、描述等）
- 生成完整的项目结构和模板文件
- 配置 Python 环境和依赖管理
- 初始化 Git 仓库

### `ui` - 编译用户界面
```bash
# 编译所有 UI 文件
uv run aadt ui
```

**功能：**
- 编译 `ui/designer/` 中的 `.ui` 文件到 `src/模块名/gui/forms/qt6/`
- 自动复制 `ui/resources/` 中的资源文件到 `src/模块名/resources/`
- 支持图标、样式表等各种资源文件

### `test` - 启动测试
```bash
# 链接插件并启动 Anki 测试
uv run aadt test
```

**功能：**
- 自动执行 `aadt link` 创建软链接
- 启动 Anki 程序加载插件
- 一键测试工作流

### `link` - 开发环境链接
```bash
# 创建软链接到 Anki 插件目录
uv run aadt link

# 删除软链接
uv run aadt link --unlink
```

**功能：**
- 将 `src/` 下的插件文件夹软链接到 Anki 插件目录
- 方便开发期间实时测试
- 支持一键取消链接


### `build` - 构建和打包插件
```bash
# 构建最新标签版本（默认）
uv run aadt build

# 构建特定版本
uv run aadt build v1.2.0        # 特定 git 标签
uv run aadt build dev           # 工作目录（包含未提交更改）
uv run aadt build current       # 最新提交
uv run aadt build release       # 最新标签（默认）

# 指定分发类型
uv run aadt build -d local      # 本地开发版本
uv run aadt build -d ankiweb    # AnkiWeb 提交版本
uv run aadt build -d all        # 同时构建两种类型

# 组合使用
uv run aadt build v1.2.0 -d local
```

**分发类型说明：**
- `local`: 适用于本地开发，保留调试信息
- `ankiweb`: 适用于 AnkiWeb 提交，优化文件大小
- `all`: 同时生成两种版本

**功能：**
- 根据 `addon.json` 配置生成 AnkiWeb 所需的 `manifest.json`
- 包含插件元数据、依赖关系等信息

### `manifest` - 生成清单文件
```bash
# 生成 manifest.json
uv run aadt manifest
```

### `clean` - 清理构建文件
```bash
# 清理所有构建产物
uv run aadt clean
```

**功能：**
- 删除 `dist/` 目录及其内容
- 清理临时文件和缓存

## 🚀 CI/CD 支持

这些命令提供更精细的构建控制，适用于自动化构建流水线：

### `create_dist` - 准备源代码树
```bash
uv run aadt create_dist [version]
```

**功能：**
- 准备源代码树到 `dist/build` 目录
- 处理版本控制和文件归档
- 为后续构建步骤做准备

#### `build_dist` - 构建源代码
```bash
aadt build_dist
```

**功能：**
- 处理 `dist/build` 中的源代码
- 编译 UI 文件，生成清单文件
- 执行所有必要的代码后处理

#### `package_dist` - 打包分发
```bash
aadt package_dist
```

**功能：**
- 将构建好的文件打包成 `.ankiaddon` 格式
- 生成最终的分发包

## 🎨 UI 开发

### 使用 Qt Designer

AADT 为 Qt Designer UI开发提供无缝集成：

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

## 代码质量

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

## 单元测试

```bash
# 运行测试
uv run pytest

# 包含覆盖率
uv run pytest --cov=aadt
```

## 🚀 Git 集成

AADT 设计为在 Git 仓库中工作最佳，但**不需要 Git**：

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
aadt build -d local

# 在非 Git 目录中（自动降级）
aadt build -d local  # 仍然可以工作！

# 显式版本指定（任何地方都可以工作）
aadt build v1.2.0 -d local
```

工具会自动检测你的环境并选择适当的方法。

## 📚 示例

查看 `tests/` 目录获取示例配置和使用模式。


## 📄 协议

本项目基于GNU AGPLv3协议。详见[LICENSE](LICENSE)文件。

---

**为Anki社区用❤️构建**

> 这个现代化版本专注于为Anki插件开发者提供最佳的开发体验，采用最新的Python技术栈和最佳实践。
