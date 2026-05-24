# MinerU MCP 接入架构

## 目标

把 MinerU 接成 **Codex 可直接调用的工具层**，而不是把整个计组知识库工作流绑死在 MinerU 自带生态里。

当前项目的原则是：

- `MinerU` 负责文档解析
- `MCP` 负责把解析能力暴露给 Codex
- `comporg-kb-builder` 负责准入审核、分层写回和治理
- `comporg-doctor` 负责入库后的巡检和修复

## 最终分层

### 1. 原始资料层

位置：

- `资料/课件/*.pdf`

职责：

- 保留原始课件
- 不直接改写

### 2. 解析工具层

组件：

- `mineru` MCP

职责：

- 把课件 PDF 送入 MinerU 精准解析 API
- 返回 Markdown、图片等解析结果

这里的 `MCP` 只是工具层，不负责知识裁决。

### 3. 审核与分流层

组件：

- `comporg-kb-builder`
- Codex 主模型
- 必要时 `vision` 子 agent

职责：

- 判断抽取结果是否可入库
- 识别乱码、结构错乱、图像承载关键内容的页面
- 复杂图像单独解释

### 4. 证据层

位置：

- `知识库/资料整理稿/课件/`
- `知识库/图像解读/课件/`

职责：

- 保存通过审核的课件整理稿
- 保存复杂图像解释稿

### 5. 规范层与索引层

位置：

- `知识库/知识点/`
- `知识库/专题/`
- `知识库/题型/`
- `知识库/反向题型索引/`

职责：

- 只接收已经稳定、可复用、通过二次沉淀的内容

## 运行关系

推荐顺序：

1. `comporg-kb-builder` 判断当前批次是课件入库
2. 调用 `mineru` MCP 做 PDF 解析
   - 默认参数口径：`model_version=vlm`、`language=ch`、`enable_formula=true`、`enable_table=true`
   - `is_ocr` 按资料分流：普通可编辑 PDF 为 `false`，扫描 / 手写 / 图片型 PDF 为 `true`
3. 先形成 `raw_extract`
4. 主模型审核
5. 必要时复杂图像走子 agent
6. 合格内容写入证据层
7. 后续再按需沉淀到知识点、题型、专题

## 为什么用 MCP，而不是直接上 RAG 框架

因为当前阶段的核心问题是：

- 文档抽取质量
- 证据层清洗
- 分层入库
- 可追溯治理

不是“快速搭一个问答应用”。

所以当前最合适的是：

- `MinerU 精准解析 API / SDK` 作为解析后端
- `MCP` 作为 Codex 工具接入层

而不是一开始就把重点转到 RAG 应用框架上。

## 当前全局配置策略

当前全局 MCP 采用远程 HTTP 形态：

- 全局注册 `mineru`
- 服务器地址：`https://mcp.mineru.net/mcp`
- 认证变量：`MINERU_API_TOKEN`

也就是说：

- Codex 侧直接连接官方远程 MCP
- Token 由全局环境变量提供
- 项目内的 `comporg-kb-builder` 继续负责决定何时调用、如何审核、如何写回知识库

## 一句话原则

**MinerU 负责“解析”，Codex 负责“判断与入库”，MCP 负责“把解析能力接进 Codex”。**
