# 工具配置说明

## 文档定位

这份文档只负责说明：

- 当前知识库基座依赖哪些工具
- 它们各自负责什么
- 应该如何做安装与自检
- 哪些工具是主路线，哪些只是参考或兜底

它**不是**知识库入库规则本身。

真正的规则优先级是：

1. `D:\wzb\计算机组成原理\AGENTS.md`
2. `D:\wzb\计算机组成原理\CODEX.md`
3. 当前 skill 说明
4. 本工具文档

也就是说，工具是否装好，不等于可以绕过知识库规则直接入库。

## 当前核心工具链

### 主线工具

- `Markdown`
  - 唯一主知识库格式
- `PyYAML`
  - frontmatter、结构元数据、规则辅助
- `mineru` MCP
  - Codex 侧 PDF 主调用入口
  - 通过全局 `MINERU_API_TOKEN` 连接官方远程 MCP
- `markitdown`
  - Word / PPT / Office 文档转 Markdown
- `mineru-open-sdk`
  - 仓库级 API / SDK 自检与参考接入
  - 不是当前 skill 的默认调用入口

### 界面层工具

- `Obsidian`
  - 人用界面层
  - 负责浏览、链接、回溯、人工修订
  - 不是知识库本体

### 可选重工具

- `magic-pdf`
  - 更重的 PDF 结构化提取工具
  - 只在 `MinerU` 不足、且确有必要时考虑

### 非主线或兜底工具

- `paddleocr`
  - 不作为当前默认主链
  - 仅保留为极少数场景兜底能力

## 新版知识库工作流中的工具分工

当前 `comporg-kb-builder` 对应的主路线是：

1. 先读 `AGENTS.md` 和 `CODEX.md`
2. 判断资料类型
3. 走类型主路线
   - PDF：全局 `mineru` MCP
   - Word / PPT / Office：`markitdown`
   - Markdown / TXT / 笔记：直接规范化
4. 先形成 `raw_extract`
5. 主模型做准入审核
6. 若存在复杂图像、复杂表格、图像型 PDF，再触发 Codex 子 agent
7. 形成 `reviewed_draft`
8. 审核通过后先写入证据层
9. 必要时再沉淀到知识点、题型、专题
10. 发现冲突、污染、分层问题时，挂钩 `comporg-doctor`

当前推荐的 MinerU 默认口径是：

- `MINERU_MODEL=vlm`
- `MINERU_LANGUAGE=ch`
- `MINERU_ENABLE_FORMULA=true`
- `MINERU_ENABLE_TABLE=true`

另外，提取结果在入证据层前必须过质量闸门：

- 不能有明显乱码
- 不能只有模板头或标题页
- 不能出现“图片很多但正文极少”的空抽取
- 可疑结果先重试，不能直接当成功入库

## 主路线与非主路线

### PDF 主路线

- 默认：全局 `mineru` MCP
- 原因：它是当前项目认可的 Codex 侧 PDF 主调用方案
- 推荐模型口径：`vlm`
- 推荐语言口径：`ch`
- 公式识别：开启
- 表格识别：开启

### Office 主路线

- 默认：`markitdown`
- 负责把 PPT / Word 转成后续可审的 Markdown

### 复杂图像处理

复杂图像、复杂表格、低清扫描页、手写页，不应假装普通 OCR 文本已经足够。

此时的正确路线是：

- 先让主模型检查抽取稿
- 若发现语义不通、乱码、结构缺失或图像信息承载关键内容
- 再触发 Codex 视觉子 agent 做定向解释
- 图像解释结果写入 `知识库/图像解读/`
- 资料整理稿中只保留干净正文和精确图像锚点

### OCR 的定位

- `OCR` 不是当前默认主线
- `paddleocr` 只保留为个别失败场景的兜底选择
- 不能把“我跑了一次 OCR”当作“已经高质量入库”

### `is_ocr` 分流约定

不要全局把 `is_ocr` 固定成同一个值，而是按资料类型分流：

- 普通可编辑 PDF：`is_ocr=false`
- 扫描 PDF / 手写页 / 图片型 PDF：`is_ocr=true`

也就是说，当前项目推荐的是：

- 可编辑正文优先保结构
- 图像型内容优先保可读性

## 旧脚本的当前地位

下列内容可以参考，但不要机械套用为固定主流程：

- `D:\wzb\计算机组成原理\scripts\ingest_materials.py`
- `D:\wzb\计算机组成原理\scripts\ingest_textbooks.py`
- `D:\wzb\计算机组成原理\scripts\mineru_api_doctor.py`

它们现在的角色是：

- 参考片段
- 旧路线样例
- 可改写、可拆用的函数来源

它们不再是：

- 新版知识库的标准入口
- 可以绕过主模型审核的执行通道
- 强制遵守、不可改动的流程准则

## 一键安装

在仓库根目录运行：

```powershell
.\scripts\setup_tooling.ps1
```

如果要顺带安装重工具：

```powershell
.\scripts\setup_tooling.ps1 -IncludeHeavy
```

## 自检

基础自检：

```powershell
.\.venv\Scripts\python.exe .\scripts\tooling_doctor.py
```

MinerU API 专项自检：

```powershell
.\.venv\Scripts\python.exe .\scripts\mineru_api_doctor.py
```

自检会输出：

- Python / `.venv` 状态
- 核心包是否可导入
- MinerU SDK 是否可导入
- `MINERU_TOKEN` 是否已配置
- `magic-pdf` / `paddleocr` 是否可用
- `Obsidian.exe` 是否在常见路径中找到
- 仓库关键规则文件是否存在

注意：

- “工具可导入”只说明环境就绪
- 不代表抽取结果已经通过审核
- 也不代表材料已经允许进入正式知识库

## MinerU 接入配置

当前分两层：

1. Codex 主调用入口：全局 `mineru` MCP
2. 仓库内 API / SDK 自检入口：`.env` + `mineru-open-sdk`

### 1. 全局 MCP 配置

当前全局配置应满足：

- MCP 名称：`mineru`
- 服务器地址：`https://mcp.mineru.net/mcp`
- 认证环境变量：`MINERU_API_TOKEN`

可用下面的命令检查：

```powershell
codex mcp get mineru
```

### 2. 仓库级 API / SDK 自检配置

如果你要跑仓库内的 `mineru_api_doctor.py`，再配置根目录 `.env`：

```env
MINERU_TOKEN=你的 Token
MINERU_MODEL=vlm
MINERU_LANGUAGE=ch
MINERU_ENABLE_FORMULA=true
MINERU_ENABLE_TABLE=true
```

然后运行：

```powershell
.\.venv\Scripts\python.exe .\scripts\mineru_api_doctor.py
```

如果 `mineru_token_present` 为 `true`，说明仓库级 API / SDK 自检配置已就绪。

## 当前建议

- 日常 PDF 主路线：全局 `mineru` MCP
- 默认解析模型口径：`vlm`
- 默认语言口径：`ch`
- 日常 Office 文档主路线：`markitdown`
- 复杂图像处理：优先交给 Codex 视觉子 agent，不要把错误 OCR 结果直接混进正文
- `magic-pdf`：仅在需要更重 PDF 提取时再装或再用
- `paddleocr`：不要当默认主链
- Obsidian：建议单独装客户端，不必进 Python 环境

## MinerU MCP

当前项目已经把 MinerU 接成全局 `MCP`，让 Codex 能把它当工具层调用。

推荐分工是：

- `mineru` MCP：负责 Codex 侧调用入口
- `MinerU API / SDK`：负责仓库级自检或参考接入
- `comporg-kb-builder`：负责审核、分层入库、写回证据层

接入架构说明见：

- [MINERU_MCP_ARCHITECTURE.md](./MINERU_MCP_ARCHITECTURE.md)

## 一句话原则

**工具只是支撑层。真正决定能否入库的，不是“命令跑没跑”，而是是否遵守 Markdown-first、主模型准入审核、复杂图像分流、证据层先行这套规则。**
