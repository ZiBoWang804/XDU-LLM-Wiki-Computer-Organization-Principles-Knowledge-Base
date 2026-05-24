# 图像修复与读图工作流

## 目标

把原 PDF / 已抽取图片稳定转换成：

- 可直接查看的 PNG
- 可供模型读取的切片图
- 可检索的 OCR Markdown
- 可回挂到 `知识库/图像解读/` 的证据层材料

这条链只服务 `md-first` 主库，不进入 `comporg_agents` 或派生产物层。

## 工作流

### 1. 校验图像解读层链接

```powershell
python scripts/validate_image_layer_links.py
```

如果教材图像解读层有坏链：

```powershell
python scripts/repair_textbook_image_links.py --apply
```

### 2. 从原 PDF 渲染页图

示例：渲染课件第 31 页，切成 3 段，并同时输出 OCR Markdown：

```powershell
python scripts/prepare_visual_sources.py "资料/课件/数制表示3--Spring.2025.pdf" --pages 31 --scale 2.0 --vertical-slices 3 --ocr-markdown
```

默认输出目录：

`渲染缓存/<源文件名>/`

输出内容：

- `page-031.png`
- `page-031-s01-of03.png` 等切片图
- `page-031.ocr.md`
- `page-031.ocr.json`
- `manifest.json`
- `index.md`

### 3. 对已抽取原图做切图和 OCR

```powershell
python scripts/prepare_visual_sources.py "知识库/资料整理稿/教材/计算机组成与设计-第2章-29-58/images/6bb3e5b1f3b7129fdeccd8b30a482c085d112988f7719976714033c3717ec352.jpg" --vertical-slices 2
```

### 4. 读图策略

- 纯文字页：优先整页 PNG + OCR Markdown
- 例题页：整页读语境，再对公式块或编码串切图
- 电路图 / 数据通路图 / 时序图 / 复杂表格：直接切图读
- 位串、字段、引脚号、下标、颜色承载语义的内容：必须人工复核

## 建议写回格式

正式写回 `知识库/图像解读/**/*.md` 时，建议沿用现有结构：

- Frontmatter
  - `figure_id`
  - `title`
  - `type: figure_interpretation`
  - `chapter`
  - `source_refs`
  - `image_ref`
  - `related_points`
  - `status`
  - `updated`
- 正文
  - `## 图像类型`
  - `## 教材中的作用` 或 `## 课件中的作用`
  - `## 图中结构 / 读取要点`
  - `## 该图支撑的知识点`
  - `## 检索关键词`
  - `## 相关知识点`
  - `## 出处`

## 当前稳定路线

- PDF 页图：`pypdfium2`
- OCR：`PaddleOCR`
- 图像切片：`prepare_visual_sources.py --vertical-slices`
- 最终图意判断：`vision` 子代理或本地人工复核

不再依赖 Edge 本地 PDF 截图作为主流程。
