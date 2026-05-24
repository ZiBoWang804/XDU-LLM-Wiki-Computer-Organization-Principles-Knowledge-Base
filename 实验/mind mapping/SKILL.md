---
name: "mind-mapping"
description: "Generate interactive knowledge relationship network graphs, mind maps, and knowledge checklists from courseware/PPT content. Use when the user needs to: (1) analyze course materials and extract key points, (2) create interactive SVG-based knowledge relationship graphs with animations, (3) create collapsible mind maps or Mermaid-based mind maps, (4) generate knowledge checklists with importance ratings. Triggers on requests involving \"思维导图\", \"知识关系图\", \"知识清单\", \"mind map\", \"knowledge graph\", \"study guide\", or \"复习\"."
---

# Mind Mapping Skill

Generate interactive knowledge relationship graphs, mind maps, and knowledge checklists from courseware content.

## When to Use

- Analyzing courseware/PPT to extract key points, difficult points, and exam topics
- Creating interactive SVG-based knowledge relationship network graphs
- Creating collapsible HTML mind maps or Mermaid mind maps
- Generating knowledge checklists with importance/difficulty/exam-frequency ratings

## Workflow

### Phase 1: Content Analysis

1. Read all provided courseware files (PPT, PDF, etc.)
2. Extract key concepts, formulas, protocols, and relationships per chapter
3. Classify each knowledge point:
   - Importance: ★ (low) → ★★★ (high)
   - Difficulty: ▲ (easy) → ▲▲▲ (hard)
   - Exam frequency: ⚡ (rare) → ⚡⚡⚡ (very common)
4. Record PPT page references for each topic

### Phase 2: Knowledge Checklist

Generate a markdown checklist file (`课程名_复习知识清单.md`):

- Organize by chapter, then by topic
- Each entry includes: concept name, key formula/facts, importance rating, PPT page
- Add a formula quick-reference table at the end
- Add top 10-15 high-frequency exam points section

### Phase 3: Mind Map

Generate TWO mind map files:

**Interactive HTML Mind Map** (`课程名_思维导图.html`):
- Collapsible card-based layout with dark gradient theme
- Chapter branches with color-coded headers (expand/collapse)
- Grid layout topics with bullet points
- Use CDN mermaid.js as fallback: `https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js`

**Mermaid Mind Map** (`课程名_思维导图.mermaid`):
- Pure Mermaid mindmap syntax for portability
- Star-marked important nodes: `★★★`
- Bold key concepts with `**...**`

### Phase 4: Knowledge Relationship Network Graph

Generate an interactive SVG-based knowledge relationship graph (`课程名_知识关系网络图.html`).

## Design System

### Color Palette

| Chapter | Normal | Bright (highlight) | Background |
|---------|--------|-------------------|------------|
| Ch1 | `#4ade80` | `#86efac` | `rgba(74,222,128,.08)` |
| Ch2 | `#60a5fa` | `#93c5fd` | `rgba(96,165,250,.08)` |
| Ch3 | `#fb923c` | `#fdba74` | `rgba(251,146,60,.08)` |
| Ch4 | `#c084fc` | `#d8b4fe` | `rgba(192,132,252,.08)` |

For 5+ chapters, extend with: `#f472b6` (pink), `#fbbf24` (yellow), `#34d399` (teal), `#f87171` (red).

### Dark Theme

- Background: `linear-gradient(135deg, #0f0c29, #302b63, #24243e)`
- Card background: `rgba(20,18,50,.88)` or `rgba(30,27,60,.92)`
- Text: `#eee` primary, `#aaa` secondary, `#888` tertiary
- Border: `rgba(255,255,255,.1)` subtle, `rgba(255,255,255,.06)` very subtle

### Network Graph Architecture

```
┌──────────┬────────────────────────────────────┐
│ Sidebar  │  SVG Canvas                        │
│ 280px    │  (pan/zoom)                        │
│          │                                    │
│ Search   │  [Ch1]  [Ch2]  [Ch3]  [Ch4]       │
│ Filter   │   ●─────●      ●─────●            │
│ Legend    │   │     │      │     │            │
│ Tips      │   ●─────●──────●     ●            │
│          │              ┌──────────────┐      │
│          │              │ Detail Card  │      │
│          │              │ (floating)   │      │
│          │              └──────────────┘      │
└──────────┴────────────────────────────────────┘
```

**Layout constants:**
- SVG viewBox: width=2400, height=max(1600, nodeCount * 150)
- PAD=80, column spacing=520px
- Node card: 200×72px, border-radius 12px
- Vertical spacing between nodes: 150px (prevents overlap on highlight)
- Important nodes offset left by 0px, normal nodes offset by +20px

### Animation Specifications

**Edge pulse (heartbeat effect):**
```css
.edge.highlight{stroke-width:3;opacity:1;filter:url(#edgeGlow)}
.edge.pulse{animation:edgePulse 1.5s ease-in-out infinite}
@keyframes edgePulse{
  0%,100%{stroke-width:3;opacity:.85;filter:url(#edgeGlow)}
  50%{stroke-width:6;opacity:1;filter:url(#edgeGlowStrong)}
}
```

**Node bounce on select:**
```css
.node.highlight{transform:scale(1.08)}
@keyframes nodeBounce{
  0%{transform:scale(1)}
  40%{transform:scale(1.14)}
  100%{transform:scale(1.08)}
}
```

**SVG glow filters:**
```javascript
// Subtle glow for edges
'<filter id="edgeGlow"><feGaussianBlur stdDeviation="2.5" result="blur"/>
  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
// Strong glow at pulse peak
'<filter id="edgeGlowStrong"><feGaussianBlur stdDeviation="4" result="blur"/>
  <feComposite in="SourceGraphic" in2="blur" operator="over"/>
  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
// Node glow
'<filter id="glow"><feGaussianBlur stdDeviation="4" result="blur"/>
  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
```

### Edge Drawing Rules

- **Same-chapter edges**: Quadratic bezier `Q` with small offset
- **Cross-chapter edges**: Cubic bezier `C` with control points at 40%/60%
- **Normal state**: `rgba(255,255,255,.08)`, stroke-width 1.5
- **Highlighted state**: Bright chapter color, stroke-width 3→6 (pulse), arrow marker
- **Dimmed state**: opacity 0.04
- Arrow markers: normal `markerWidth=8`, bright `markerWidth=10`

### Interaction Model

1. **Node click**: Highlight node + connected edges + neighbor nodes. Dim everything else. Show detail card.
2. **Detail card**: Position at `svgRect.width*0.58, svgRect.height*0.15`. Contains chapter, title, PPT page, description, exam tip.
3. **Wheel zoom**: `scale *= 0.92 or 1.08`, range [0.3, 3]
4. **Drag pan**: Track delta mouse movement
5. **Chapter filter**: Toggle visibility by chapter
6. **Search**: Match node label/subtitle, auto-select + show detail
7. **Click empty space**: Close detail, reset highlights

### Sidebar Content

- **Search box**: Real-time filter by label/subtitle
- **Chapter buttons**: Active state with chapter color border/background
- **Legend**: Color dots per chapter + red dot for important nodes
- **Learning tips**: 10-15 curated exam tips, color-coded by chapter

## Data Structure

```javascript
const nodes = [
  {
    id: 'unique_id',        // snake_case identifier
    label: '概念名称',       // Display name (Chinese)
    sub: '副标题/公式',      // Subtitle or key formula
    ch: 1,                  // Chapter number
    p: 'PPT136',            // Page reference
    important: true,         // High-frequency exam point
    desc: '详细描述...',     // Shown in detail card
    tip: '考试建议...'       // Exam tip shown in detail card
  }
];

const edges = [
  {
    from: 'node_id_1',
    to: 'node_id_2',
    label: '关系描述',       // Shown on hover/highlight
    cross: true              // true = cross-chapter edge (uses bezier)
  }
];
```

## Output

Save all generated files to the user's workspace folder. Provide `computer://` links for each file. Generate these files:

1. `课程名_复习知识清单.md` — Knowledge checklist
2. `课程名_思维导图.html` — Interactive collapsible mind map
3. `课程名_思维导图.mermaid` — Portable Mermaid mind map
4. `课程名_知识关系网络图.html` — Interactive SVG relationship graph

