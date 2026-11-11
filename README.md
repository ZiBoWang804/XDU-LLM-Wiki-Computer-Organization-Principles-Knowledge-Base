# TeleAgent 编译原理考点地图智能体

> 校园学习赋能 TeleAgent 智能体大赛 · 揭榜命题6「课程复习考点地图智能体」参赛作品
> 以 Obsidian 风格的知识库为底座，RAG + LLM Wiki 双层检索驱动的课程复习智能体，覆盖 **知识库构建 → 考点地图 → 薄弱诊断 → 个性化复习 → 变式训练** 全流程。

## 功能总览

### 学生端
- **考点地图**：章节 → 知识点 → 考点三级结构 + 考试权重，ECharts 力导向图谱可视化
- **薄弱点诊断**：错因四分类（概念混淆 / 步骤遗漏 / 计算失误 / 规则记错），能力雷达 + 学习路径
- **个性化复习计划**：规则引擎 30 秒内生成，按薄弱优先级排程
- **变式训练**：模板生成 + 规则校验，答案 100% 正确；支持指定原题/章节生成变式
- **自测刷题**：保留专用答题 UI（选择 / 填空），作答记录回流学情
- **智能问答**：RAG + 知识库笔记双层检索回答，可引用选中原文提问、`@文档名` 切换关联文档

### 教师端
- **学情看板**：班级正确率热力图、知识点掌握分布、个体画像
- **命题与作业**：agent 自主查库 + 结合学情出全新题（答案解析默认折叠）、一键布置作业
- **知识库管理**：导入资料、提取知识点、生成图谱、知识库体检、页面勘误（只读模式自动转勘误单）

### TeleAgent 助教（Claudian 式交互）
- `/` 命令面板调用 skill、`@文档名` 引用、Effort 思考等级、YOLO 写权限开关
- Zen Mode（折叠面板专注输入）、多会话 Sessions、选中文字 Inline Edit（diff 预览）
- `/collab` 双智能体协作（教师审阅 ⇄ 学生作答多轮对话）
- 模型思考过程（reasoning）实时展示

### 平台能力
- **RAG + LLM Wiki 双层检索**：TeleAgent 知识库 API（原始资料层）+ 精编 Markdown 笔记（权威层）
- **语义检索**：本地 fastembed（bge-small-zh）向量 + 关键词混合；不可用时自动降级 bigram
- **Smart Lookup（⌘K）/ Smart Connections**：快速跳转、文档语义关联图
- **多课程可插拔**：换课程 = 在 `app/data/courses.json` 注册新知识库目录，零代码改动
- **PDF / LaTeX**：PDF 附件内嵌预览，KaTeX 公式渲染

## 架构

```
┌────────────────────────────────────────────────────┐
│  前端（Obsidian 三栏布局 · ECharts · marked · KaTeX）  │
│    学生端 index.html    教师端 teacher.html           │
├────────────────────────────────────────────────────┤
│  FastAPI + SQLite（会话鉴权 · 多课程 contextvar）      │
│    skills.py：11 个 Skill（提示词+工具+规则封装）      │
├──────────────────────┬─────────────────────────────┤
│  LLM Wiki 层（权威）   │  RAG 层（素材）               │
│  编译原理知识库/*.md   │  TeleAgent 知识库 API        │
│  wiki_adapter 混合检索 │  dataset_adapter 原始资料     │
├──────────────────────┴─────────────────────────────┤
│  DeepSeek（OpenAI 兼容 API）· fastembed 本地向量       │
└────────────────────────────────────────────────────┘
```

## 目录结构

```
app/
  backend/
    main.py            # FastAPI 路由（auth / wiki / rag / skills / teacher / profile…）
    skills.py          # Skill 框架 + 11 个智能体技能
    config.py          # 环境变量 + 多课程注册表
    adapters/          # llm / wiki / embed / dataset / database 适配器
  static/              # 双端前端（html / css / js）
  data/                # 课程注册、考点图谱、题库、评测集、学情种子数据
编译原理知识库/          # LLM Wiki 权威笔记（35 篇核心 + 期末复习专题 + 原始资料）
```

## 快速开始

```bash
pip install -r requirements.txt

# 配置 .env（不入库，见 .env.example）
LLM_API_KEY=sk-xxxx            # OpenAI 兼容端点密钥
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-v4-flash
TELEAI_DATASET_KEY=dataset-xxx  # TeleAgent 知识库（可选，RAG 层）
TELEAI_DATABASE_KEY=database-xxx

python -m uvicorn app.backend.main:app --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000 ，默认账号：

| 角色 | 账号 | 密码 |
|------|------|------|
| 教师 | teacher | teacher123 |
| 学生 | student | student123 |

> fastembed 首次运行会自动下载向量模型（走 hf-mirror 镜像）；下载失败自动降级为 bigram 检索，功能不受影响。

## Agent Skills

所有教学动作都封装为 Skill（提示词 + 工具 + 规则），执行结果经检查后写入知识库 `智能体记录/` 形成文档留痕：

| Skill | 角色 | 说明 |
|-------|------|------|
| ✏️ 出题 | 教师 | 自主查库 + 学情 → 发散命制全新题，答案解析默认折叠 |
| 📝 勘误 | 教师 | 页面错误提交勘误单，教师核对后入库 |
| 📋 布置作业 | 教师 | 按章节/知识点组卷发布 |
| 📥 导入资料 | 教师 | 原始资料入 RAG 素材层 |
| 🔍 提取知识点 | 教师 | 从资料抽取知识点候选 |
| 🕸 生成图谱 | 教师 | 重建考点图谱（章节→知识点→考点+权重） |
| ✅ 知识库体检 | 教师 | 覆盖率 / 死链 / 缺重检测 |
| 📝 自测 | 学生 | 保留专用答题 UI，作答回流学情 |
| 🎯 薄弱训练 | 学生 | 针对薄弱知识点定向练习 |
| 📅 复习计划 | 学生 | 规则引擎个性化排程 |
| 🔁 变式训练 | 学生 | 模板生成变式题，答案规则校验 100% 正确 |

## 质量保障设计

- **变式题 100% 正确率**：模板生成 + 规则逐题校验，不依赖模型自由发挥
- **不编造**：知识库检索不到时明确告知，不虚构页码与出处
- **命令幂等**：所有 skill 产出先检查后入库，只读模式（YOLO 关）下自动改写为勘误单
- **评测集**：`app/data/evals/` 内置考点覆盖评测题，可回归验证

## 多课程复用

在 `app/data/courses.json` 注册即可挂载新的 Obsidian 知识库：

```json
{ "id": "compiler", "name": "编译原理", "description": "…", "kb_dir": "path/to/kb" }
```

前端通过 `X-Course-Id` 头切换课程，图谱 / 题库 / 记录按课程隔离。
