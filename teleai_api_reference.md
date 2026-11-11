# 星辰智能体平台 知识库API 参考（agent.teleai.com.cn）

> 来源：平台"知识库API → 接口文档"页截图（2026-11-11）。密钥见 .env（TELEAI_DATASET_KEY），密钥不入 git。
> 全局：Base = https://agent.teleai.com.cn，鉴权头 `Authorization: Bearer <ApiKey>`。

## 端点总表

| 功能 | 方法+路径 | 状态 |
|---|---|---|
| 创建知识库 | POST /v1/api_key/datasets/init | 已知 |
| 上传文件 | POST /v1/api_key/files/upload | 已知（核心） |
| 绑定文档到知识库 | POST /v1/api_key/datasets/{dataset_id}/documents | 已知（核心） |
| 文档列表 | GET /v1/api_key/datasets/{dataset_id}/documents?page=&limit=&keyword= | 已知 |
| **召回检索(RAG)** | POST /v1/api_key/datasets/draft | 已知（核心） |
| 更新/删除知识库、知识库列表、模型查找、删除文档、索引状态 | —— | 路径未截图，用到时再查 |

## 1. 上传文件（单文件，≤20MB）

POST /v1/api_key/files/upload，`Content-Type: multipart/form-data`，form 字段 `file=@...`。
支持：TXT/MARKDOWN/PDF/DOC/DOCX/HTML/XLS/XLSX/CSV/JPG/JPEG/PNG/WPS/WPT。
返回：`{id, name, size, extension, mime_type, created_by, created_at}` —— id 即 file_id。

## 2. 绑定文档到知识库（可批量挂到已有库）

POST /v1/api_key/datasets/{dataset_id}/documents，application/json：

```json
{
  "data_source": {
    "type": "upload_file",
    "info_list": {
      "data_source_type": "upload_file",
      "file_info_list": { "file_ids": ["<file_id>", "...最多500条"] }
    }
  },
  "process_rule": { "rules": {}, "mode": "automatic" },
  "doc_form": "text_model",
  "doc_language": "chinese",
  "retrieval_model": {
    "search_method": "semantic_search",
    "reranking_enable": false,
    "reranking_mode": "weighted_score",
    "reranking_model": { "reranking_provider_name": "", "reranking_model_name": "" },
    "weights": {
      "keyword_setting": { "keyword_weight": 0.3 },
      "vector_setting": { "vector_weight": 0.7, "embedding_model_name": "", "embedding_provider_name": "" }
    },
    "top_k": 3,
    "score_threshold_enabled": true,
    "score_threshold": 0.5
  }
}
```

- `doc_form`: text_model(文本模型)/qa_model(问答模型)；`doc_language`: chinese/English
- `mode`: automatic(自动分段)/custom(自定义规则)
- `search_method`: semantic_search(语义)/keyword_search(关键词)；`reranking_mode`: weighted_score(加权)/reranking_model(模型重排)
- 返回 `documents[]`: id, name, tokens, word_count, hit_count, doc_form, error, enabled, archived,
  display_status(queuing/indexing/done/failed), data_source_detail_dict.upload_file{...}

## 3. 召回检索（RAG 核心）

POST /v1/api_key/datasets/draft，application/json：

```json
{
  "inputs": "用户问题",
  "retry_config": { "max_retries": 2, "retry_interval": 10, "retry_enabled": true },
  "dataset_ids": ["<dataset_id>"],
  "retrieval_mode": "multiple",
  "multiple_retrieval_config": {
    "top_k": 3,
    "score_threshold": 0.13,
    "reranking_enable": true,
    "reranking_mode": "reranking_model",
    "reranking_model": { "provider": "tong_yi", "model": "gte-rerank" },
    "weights": {
      "vector_setting": { "vector_weight": 1.0 },
      "keyword_setting": { "keyword_weight": 0.0 }
    }
  }
}
```

返回：

```json
{
  "data": [{
    "inputs": "查询词",
    "metadata": [{
      "dataset_id": "...", "dataset_name": "...",
      "document_id": "...", "document_name": "300字描述.txt",
      "document_data_source_type": "upload_file",
      "segment_id": "...", "score": 0.608, 
      "segment_hit_count": 35, "segment_word_count": 219,
      "segment_position": 1, "position": 1
    }],
    "title": "片段标题(文档名)",
    "content": "召回的片段正文——直接作为引用出处"
  }]
}
```

→ `title`/`content`/`document_name`/`score` 可直接做"答案引用出处"展示（对应防编造页码要求）。

## 4. 创建知识库（补充字段）

POST /v1/api_key/datasets/init —— `ocr_enable`: "0"快速解析(纯文本)/"1"精准解析(图片型PDF)；
`enhanced_enable`+"enhanced_feature": "2"问题生成 "3"段落总结（可辅助考点抽取）；`embedding_model_provider` 模型供应商。

## 错误码

结构 `{code, message, status}`。400 bad_request(APIKey过期/invalid_action/document_indexing/document_already_finished/invalid_metadata/dataset_not_initialized/high_quality_dataset_only/no_file_uploaded/too_many_files)；
401 unauthorized；403 archived_document_immutable；404 not_found(APIKey/Dataset not found)；
409 dataset_name_duplicate；413 file_too_large；415 unsupported_file_type。

## 备忘

- dataset_ids 示例为数字串（"1213360"），不一定是 UUID，以创建接口返回为准。
- 文档处理是异步的：绑定后 display_status 走 queuing→indexing→done，检索前轮询文档列表确认 done（即"索引状态查询"的替代做法）。

---

# 数据库API 参考（database-... 密钥，同一 Base + 鉴权头）

> 来源：QQ 长截图 ×2 OCR + 目检核对（2026-11-11）。注意：**文档中没有行级增删改查接口**——数据进库靠文件导入（CSV/Excel），表结构可自定义。

| 功能 | 方法+路径 | 关键参数 |
|---|---|---|
| 创建数据库 | POST /v1/api_key/databases/create | name(OCR误识为aweuqp), description(≤200字), type("1"默认) |
| 更新数据库 | POST /v1/api_key/databases/update | db_id, db_name?, description? |
| 删除数据库 | POST /v1/api_key/databases/delete | db_id（级联删全部表，慎用） |
| 数据库列表 | POST /v1/api_key/databases/list | page, size, ids[], keyword → data.dbs[]+total/has_more |
| 上传数据文件 | POST /v1/api_key/databases/files/upload | multipart: db_id + file（≤15MB，仅 xlsx/xls/csv，CSV 须 UTF-8）→ file_id |
| 文件建表 | POST /v1/api_key/databases/table/create | db_id, files[{file_id}], data_permission(0只读/1读写) → table_id |
| **自定义建表** | POST /v1/api_key/databases/table/create_custom_table | db_id, table_name, table_desc, tab_desc(0/1自动表描述), data_permission, columns[{name, description, type, is_necessary}] → table_id |
| 数据表列表 | POST /v1/api_key/databases/table/list | db_id → tables[]（含 status_check/security/import 状态、data_volume"7行3列"、database_info） |
| 删除数据表 | POST /v1/api_key/databases/table/delete | db_id, table_id |
| 表状态查询 | POST /v1/api_key/databases/table/status | db_id, table_id → status_check(0-3)/status_security/status_import（异步导入须轮询到 2） |

## 同步策略（架构定案）

自研 SQLite 为账本（答题记录明细）→ 定期导出 CSV 快照 → files/upload + table/create 导入平台库（教师档案/学生档案）→ 智能体侧读表做个性化问答。**平台库=智能体可见的档案镜像，SQLite=真实账本**。

## 限制与错误码要点

- 每库表数量有上限（错误提示"当前已有%d个表，最多支持%v个表"）；文件≤15MB；一次最多 5 文件；文件名不可重复。
- 错误结构 `{code, message, status}`：database_not_found/table_already_exists/database_already_exists(400)、param_invalid(400)、表不存在/表名已存在/不支持的字段类型(500)等。响应成功固定 `"message": "success"`。
- 创建响应示例中 tenant_id/created_at 可能为 null，正常现象。

## 模型API（生成层）

- Base: https://api-maas.teleai.com.cn/v1，OpenAI 兼容；模型 Xing4.0-29B-A4B / TeleChat3-438B-A24B（256K ctx）。
- Key 申请：console.teleai.com.cn/application（API管理/模型管理），需单独开通模型。
