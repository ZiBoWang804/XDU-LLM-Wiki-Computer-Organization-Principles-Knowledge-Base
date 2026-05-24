# 计组 Skill 文档索引

本目录保存的是这套《计算机组成原理》知识库在 GitHub 仓库里的 **GitHub 可读版 skill 文档**。

它们对应本地 Codex 环境中的实际 skill，但这里的文档更偏向：

- 设计说明
- 工作流说明
- 约束摘要
- 入口页说明

如果你是在本地运行 Codex，这些 skill 的运行态入口仍然应安装在你的 Codex skill 目录中；本仓库中的版本主要用于：

- 在 GitHub 中展示这套方法论
- 让协作者理解每个 skill 的职责边界
- 让后续迁移到其他课程时有稳定文档可参考

## 文档列表

| Skill | 说明 |
| --- | --- |
| [comporg-kb-builder.md](./comporg-kb-builder.md) | 知识库基座：资料入库、MinerU 审核、图像解读、知识沉淀 |
| [comporg-doctor.md](./comporg-doctor.md) | 知识库治理：巡检、修复、覆盖率检查、冲突治理 |
| [comporg-answer.md](./comporg-answer.md) | 答疑 / 作业题解答：概念解释、题目求解、混合模式 |
| [comporg-grading.md](./comporg-grading.md) | 学生批改：给分、评语、错因与弱项候选 |
| [comporg-exam-author.md](./comporg-exam-author.md) | 组卷：正式试卷生成、参考答案、给分点与覆盖表 |

## 统一前提

所有 skill 都共享这些底层约束：

1. Markdown 是唯一主知识资产
2. 进入仓库后必须先遵守 [AGENTS.md](../../AGENTS.md) 和 [CODEX.md](../../CODEX.md)
3. 默认路线是 `md-first`
4. 不把旧的派生工具链、数据库或缓存当作知识库本体
5. 证据层、规范层、演化层必须严格分离

## 相关设计文档

- [2026-05-21-comporg-answer-skill-design.md](../superpowers/specs/2026-05-21-comporg-answer-skill-design.md)
- [2026-05-21-comporg-doctor-skill-design.md](../superpowers/specs/2026-05-21-comporg-doctor-skill-design.md)
- [2026-05-21-comporg-grading-skill-design.md](../superpowers/specs/2026-05-21-comporg-grading-skill-design.md)
- [2026-05-22-comporg-exam-author-skill-design.md](../superpowers/specs/2026-05-22-comporg-exam-author-skill-design.md)
- [2026-05-22-comporg-kb-builder-redesign.md](../superpowers/specs/2026-05-22-comporg-kb-builder-redesign.md)
