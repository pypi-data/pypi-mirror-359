# BigModel Hub (BMHub)

## 概述

本项目增强从 Hugging Face Hub 与 ModelScope Hub 下载新模型与列出、更新、删除已下载模型的体验。

## 模型存储

默认情况下，BMHub 基于 Hugging Face Hub 或 ModelScope Hub 的缓存机制来存储模型，来获取最大的兼容性与空间利用率。

如果需要更改默认的缓存目录位置，参考 Hugging Face Hub 或 ModelScope Hub 的文档，设置环境变量 `HF_HUB_CACHE` 或 `MODELSCOPE_CACHE` 来修改缓存目录位置。

如果不依赖 Hugging Face Hub 或 ModelScope Hub 的缓存机制，需要手动指定本地模型存储目录，且遵循如下目录结构：

```
|- <Local Models Directory>
   |- <Organization ID>
      |- <Model ID>
      |- ...
   |- ...
```

本地模型存储目录结构示例：

```
|- <Local Models Directory>
   |- Qwen
      |- Qwen2.5-7B-Instruct
         |- config.json
         |- ...
```

## 安装

```bash
pip install bmhub
```

测试 BMHub CLI 可用性。

```bash
bmhub --help
```

如果访问 Hugging Face Hub 受限，设置环境变量 `HF_ENDPOINT` 。

```bash
HF_ENDPOINT=https://hf-mirror.com bmhub --help
```

> 建议在访问 Hugging Face Hub 受限时使用 ModelScope Hub 加速下载。

## CLI 功能

### 列出模型

列出已下载的模型，可以通过模型 ID 的 Glob 模式过滤，并查看模型占用存储空间等信息。

默认在 Hugging Face Hub 或 ModelScope Hub 缓存目录中检索已下载的模型。如果指定参数 `--local-dir`，则在本地模型存储目录中检索已下载的模型。

```bash
bmhub list --help
```

### 下载模型

下载指定 ID 的模型，如果已下载过模型，则会更新该模型。

默认下载到 Hugging Face Hub 或 ModelScope Hub 缓存目录。如果指定参数 `--local-dir`，则下载到本地模型存储目录。

```bash
bmhub download --help
```

### 更新模型

更新已下载的模型，可以通过模型 ID 的 Glob 模式过滤。

默认在 Hugging Face Hub 或 ModelScope Hub 缓存目录中更新已下载的模型。如果指定参数 `--local-dir`，则在本地模型存储目录中更新已下载的模型。

```bash
bmhub update --help
```

### 删除模型

删除已下载的模型，可以通过模型 ID 的 Glob 模式过滤。

默认在 Hugging Face Hub 或 ModelScope Hub 缓存目录中删除已下载的模型。如果指定参数 `--local-dir`，则在本地模型存储目录中删除已下载的模型。

```bash
bmhub remove --help
```
