# XDU: 基于 LLM + Wiki 的《计算机组成原理》知识库

一个面向《计算机组成原理》课程的 `Markdown-first` 知识库仓库。
它不是“套壳问答系统”，而是把教材、课件、试卷、作业、图表解读、知识点、题型、勘误、个人演化内容组织成一套 **LLM 能高效读取、人能直接审阅、错误能被追溯修正** 的课程知识底座。

- GitHub 仓库地址：<https://github.com/ZiBoWang804/XDU-LLM-Wiki-Computer-Organization-Principles-Knowledge-Base>
- 当前方法论关键词：`LLM + Wiki`、`知识点中心`、`四层架构`、`可审计`、`可纠错`、`可增长`
- 完整治理约束见：[AGENTS.md](./AGENTS.md) / [CODEX.md](./CODEX.md)

## 1. 项目定位

这套仓库的核心目标，是持续维护一套高质量、可追溯、可纠错、可增长的《计算机组成原理》知识库，而不是把知识藏进数据库、向量库或黑盒服务。

这里的主资产始终是本地 Markdown：

- 人可以直接阅读、修改、审核
- LLM 可以按索引、链接和层级结构导航
- 错误可以精确定位到知识点页、整理稿、图像解读页和原始资料

## 2. 核心思想

本项目采用的是 **Karpathy 风格的 LLM + Wiki** 路线，而不是“先切 chunk、再做 embedding、最后 top-k 检索”的传统 RAG 默认解法。

核心判断有四条：

1. 对这门课来说，最稳定的最小单元不是题目、方法或 chunk，而是 **知识点**。
2. 对课程型任务来说，模型更适合“像人一样读结构化知识库”，而不是在无结构文本碎片里做概率匹配。
3. 课程答题、批改、出卷这类场景对正确性和出处要求高，必须优先保证可追溯、可解释、可人工修复。
4. Markdown 是跨模型、跨工具、跨平台的长期资产；模型和工具都应该围绕它工作，而不是反过来绑死知识库。

简化地说：

- `RAG` 更擅长海量文档的模糊召回
- `LLM + Wiki` 更适合知识量可控、但要求准确、可审计、可维护的课程知识工程

## 3. 当前知识库规模

以下规模信息来自本仓库的架构展示文档《知识库架构文档》截至 `2026-05` 的统计：

| 资产类型 | 数量 |
| --- | ---: |
| 知识点页 | 173 |
| 题型页 | 30 |
| 反向题型索引 | 78 |
| 课件整理稿 | 24 |
| 图像解读页 | 46 |
| 专题页 | 21 |
| 教材章节 | 10 |
| 勘误 / 分歧 | 5 |

## 4. 四层架构

本仓库最核心的不是某个脚本，而是四层边界。

| 层级 | 作用 | 典型内容 | 规则 |
| --- | --- | --- | --- |
| 原始层 | 保存知识来源 | 教材 PDF、课件 PDF、试卷扫描件 | 原始资料不可偷偷改写 |
| 证据层 | 保存出处、上下文、图像解释 | 资料整理稿、图像解读、勘误、分歧 | 先保留证据，再考虑升格 |
| 规范层 | 保存课程稳定表达 | 知识点页、题型页、标准化答题模板、代表题 | 默认主读取层 |
| 演化层 | 保存个人理解与增量记忆 | 个人理解、类比、替代解法、待确认质疑 | 不直接混入知识点正文 |

默认读取顺序固定为：

`总索引 -> 章节/专题索引 -> 知识点页 -> 必要时回读整理稿片段 -> 复杂图再读图像解读`

这也是本仓库坚持 `md-first` 的核心原因：
模型不应无差别全库乱扫，而应沿着分层索引逐步收缩。

## 5. 目录结构

```text
计算机组成原理/
├─ 知识库/
│  ├─ index.md
│  ├─ 章节/
│  ├─ 专题/
│  ├─ 知识点/
│  ├─ 题型/
│  ├─ 反向题型索引/
│  ├─ 资料整理稿/
│  ├─ 图像解读/
│  ├─ 勘误/
│  ├─ 分歧/
│  └─ 个人演化/
├─ 资料/
├─ docs/
│  ├─ skills/
│  ├─ tooling/
│  └─ superpowers/
├─ AGENTS.md
├─ CODEX.md
└─ README.md
```

几个关键原则：

- 同一个知识点正文只能维护一份
- 页面里只维护正向关系，反向关系通过索引或 backlinks 派生
- `知识点页` 是规范层，`资料整理稿` 是证据层，二者不是替代关系

## 6. 工作流

### 6.1 总体流水线

从原始资料到可复用知识，当前采用如下主流程：

1. 资料进入仓库原始层
2. 按类型选择提取路线
   - `PDF`：MinerU MCP
   - `Word / PPT / Office`：markitdown
   - `Markdown / TXT / 笔记`：直接规范化
3. 先形成 `raw-extract`，不立刻写正式知识库
4. 主模型做准入审核
5. 对复杂图像 / 复杂表格 / 图片型 PDF 触发视觉子代理
6. 审核通过后，先写入证据层
7. 从证据层沉淀知识点、题型、专题和索引
8. 通过治理流程巡检冲突、死链、层违规和覆盖率缺口

### 6.2 复杂 PDF 的两阶段方案

本项目对 PDF 资料不依赖单一路径，而是采用“两阶段提取”：

1. **MinerU 批量提取**
   - 负责大部分普通 PDF
   - 生成 Markdown、图片、公式、表格结构
2. **视觉大模型精修**
   - 只处理高信息密度、OCR 失败或结构极复杂的页面
   - 输出结构化图像解读页
   - 不把乱码或错误识别结果直接混进正式整理稿正文

也就是说，目标从来不是“识别出字就算成功”，而是：

**只有真正读懂、审核通过、可追溯地写回 Markdown，才算进入知识库。**

## 7. 工具与环境

### 7.1 核心环境

- `PowerShell 7`
- `Python + uv`
- `Git`
- `Obsidian`
- `Codex Desktop / Codex CLI`

### 7.2 文档与知识库主资产

- `Markdown`
  - 唯一主知识库格式
- `PyYAML`
  - 用于 frontmatter、结构元数据等辅助处理

### 7.3 文档提取工具

- `MinerU MCP`
  - 当前 PDF 主调用入口
  - 推荐口径：`vlm`、`ch`、公式识别开启、表格识别开启
- `markitdown`
  - Office 文档转 Markdown

### 7.4 模型与智能执行层

- `Codex`
  - 主控制器、审核器、答题/批改/治理/入库执行层
- `Vision 子代理`
  - 复杂图、复杂表、图片型 PDF 的定向解读
- `comporg-doctor`
  - 知识库巡检和结构治理

### 7.5 关键参考文档

- [docs/tooling/SETUP.md](./docs/tooling/SETUP.md)
- [docs/tooling/MINERU_MCP_ARCHITECTURE.md](./docs/tooling/MINERU_MCP_ARCHITECTURE.md)
- [docs/tooling/IMAGE_WORKFLOW.md](./docs/tooling/IMAGE_WORKFLOW.md)

## 8. Skill 体系

这套知识库不是只有“静态资料”，还配套了一组围绕 Markdown 主库工作的专用 skill 文档。
为了方便在 GitHub 中查看，本仓库额外导出了 `docs/skills/` 目录。

| Skill | 作用 | 文档 |
| --- | --- | --- |
| `comporg-kb-builder` | 资料入库、MinerU 审核、图像解读、知识沉淀 | [docs/skills/comporg-kb-builder.md](./docs/skills/comporg-kb-builder.md) |
| `comporg-doctor` | 巡检知识库、修死链、查冲突、做结构治理 | [docs/skills/comporg-doctor.md](./docs/skills/comporg-doctor.md) |
| `comporg-answer` | 概念答疑、作业题解答、混合讲解 + 解题 | [docs/skills/comporg-answer.md](./docs/skills/comporg-answer.md) |
| `comporg-grading` | 学生作业 / 试卷批改、错因分析、弱项记录 | [docs/skills/comporg-grading.md](./docs/skills/comporg-grading.md) |
| `comporg-exam-author` | 基于本地题型和知识点结构进行正式组卷 | [docs/skills/comporg-exam-author.md](./docs/skills/comporg-exam-author.md) |

Skill 设计说明仍保留在：

- [docs/superpowers/specs/2026-05-21-comporg-answer-skill-design.md](./docs/superpowers/specs/2026-05-21-comporg-answer-skill-design.md)
- [docs/superpowers/specs/2026-05-21-comporg-doctor-skill-design.md](./docs/superpowers/specs/2026-05-21-comporg-doctor-skill-design.md)
- [docs/superpowers/specs/2026-05-21-comporg-grading-skill-design.md](./docs/superpowers/specs/2026-05-21-comporg-grading-skill-design.md)
- [docs/superpowers/specs/2026-05-22-comporg-exam-author-skill-design.md](./docs/superpowers/specs/2026-05-22-comporg-exam-author-skill-design.md)
- [docs/superpowers/specs/2026-05-22-comporg-kb-builder-redesign.md](./docs/superpowers/specs/2026-05-22-comporg-kb-builder-redesign.md)

## 9. 优势

这套方案的优势，不只是“能答题”，而是它同时解决了知识组织、知识治理和后续扩展的问题。

### 9.1 可追溯

答案、题型、知识点、整理稿、原始资料之间可逐层回溯，错误定位清晰。

### 9.2 可纠错

资料中的错误不会被静默吸收；可以通过 `勘误` / `分歧` 单独治理。

### 9.3 人类友好

主资产就是 Markdown，可以直接用 Obsidian 查看、编辑、回溯、画图谱。

### 9.4 模型无关

知识库本体不绑定某个单一模型、数据库或 embedding 体系，迁移成本低。

### 9.5 可复用

只要保留四层架构、frontmatter 规范、索引结构和 skill 工作流，这套方法可以迁移到别的课程。

### 9.6 可扩展

知识库一旦立住，上层就能叠加：

- 自动答疑
- 自动批改
- 自动组卷
- 错题与弱项画像
- 学习路径规划

## 10. 未来发展

当前仓库已经不再只是“整理笔记”，后续自然的演进方向包括：

1. **通用课程模板化**
   - 把“四层架构 + frontmatter + 索引规范 + skill 体系”抽象成跨课程模板
2. **知识库驱动的自适应学习 Agent**
   - 在答题、批改、复习推荐、薄弱点诊断之间形成闭环
3. **个人演化层持续生长**
   - 将用户的理解、类比、质疑、替代解法和错题历史持续沉淀，并与知识点稳定挂钩

## 11. 搭建流程

如果你想在本地复现这套工作流，推荐按下面的顺序搭建。

### 第一步：准备环境

安装并确认：

- PowerShell 7
- Git
- Python
- `uv`
- Obsidian
- Codex Desktop 或 Codex CLI

### 第二步：克隆仓库

```powershell
git clone https://github.com/ZiBoWang804/XDU-LLM-Wiki-Computer-Organization-Principles-Knowledge-Base.git
cd XDU-LLM-Wiki-Computer-Organization-Principles-Knowledge-Base
```

### 第三步：安装仓库工具

```powershell
.\scripts\setup_tooling.ps1
```

如果你需要更重的依赖：

```powershell
.\scripts\setup_tooling.ps1 -IncludeHeavy
```

### 第四步：配置 MinerU MCP

本项目当前推荐的 PDF 主路线是全局 `mineru` MCP。
推荐默认口径：

- `MINERU_MODEL=vlm`
- `MINERU_LANGUAGE=ch`
- `MINERU_ENABLE_FORMULA=true`
- `MINERU_ENABLE_TABLE=true`

然后按资料类型分流：

- 普通可编辑 PDF：`is_ocr=false`
- 扫描 / 手写 / 图片型 PDF：`is_ocr=true`

详细说明见：

- [docs/tooling/SETUP.md](./docs/tooling/SETUP.md)
- [docs/tooling/MINERU_MCP_ARCHITECTURE.md](./docs/tooling/MINERU_MCP_ARCHITECTURE.md)

### 第五步：运行环境自检

```powershell
.\.venv\Scripts\python.exe .\scripts\tooling_doctor.py
```

如需检查 MinerU SDK / API 侧配置：

```powershell
.\.venv\Scripts\python.exe .\scripts\mineru_api_doctor.py
```

### 第六步：用 Obsidian 打开仓库

建议直接把仓库根目录或 `知识库/` 作为 Obsidian Vault 打开，用于：

- 浏览知识点
- 看 wikilink / backlinks
- 查看反向题型索引
- 审阅资料整理稿与图像解读页
- 补充个人演化层内容

### 第七步：开始入库

把课程资料放进 `资料/` 后，使用 `comporg-kb-builder` 工作流做：

- 提取
- 审核
- 复杂图像分流
- 写入证据层
- 沉淀知识点 / 题型 / 专题

### 第八步：治理与使用

完成入库后，按需继续：

- 用 `comporg-doctor` 做巡检
- 用 `comporg-answer` 做答疑和作业题解答
- 用 `comporg-grading` 做批改
- 用 `comporg-exam-author` 做正式组卷

## 12. 相关文档

- [AGENTS.md](./AGENTS.md)
- [CODEX.md](./CODEX.md)
- [architecture-overview.md](./architecture-overview.md)
- [docs/tooling/SETUP.md](./docs/tooling/SETUP.md)
- [docs/skills/README.md](./docs/skills/README.md)

## 13. 一句话总结

这不是一个“靠几条 prompt 临时回答问题”的项目，而是一套以知识点 Markdown 页为核心、以原始资料整理稿为证据、以图像解读和治理流程补强、以 skill 体系提供上层能力的 **LLM + Wiki 课程知识工程底座**。
