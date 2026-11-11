// ================= 基础 =================
let SID = 0;

// ---------- 鉴权 ----------
const TOKEN = localStorage.getItem('ta_token') || '';
if (!TOKEN) location.href = '/static/login.html';
const MYNAME = localStorage.getItem('ta_name') || '张三';

const COURSE_ID = localStorage.getItem('ta_course') || 'compiler';

async function api(path, opts = {}) {
  opts.headers = { 'X-Token': TOKEN, 'X-Course-Id': COURSE_ID, ...(opts.headers || {}) };
  const r = await fetch(path, opts);
  if (r.status === 401) { location.href = '/static/login.html'; throw new Error('未登录'); }
  const data = await r.json();
  if (!r.ok) throw new Error(data.detail || '请求失败');
  return data;
}
const post = (path, body) => api(path, {
  method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
});

function logout() {
  fetch('/api/auth/logout', { method: 'POST', headers: { 'X-Token': TOKEN } });
  localStorage.clear();
  location.href = '/static/login.html';
}

// ================= 视图切换（左栏 TOOLS） =================
function openView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + name).classList.add('active');
  document.getElementById('mainScroll').scrollTop = 0;
  if (name === 'graph' && !graphDrawn) drawGraph();
  if (name === 'plan') loadHomework();
  if (name === 'variant') loadVariantList();
  setTimeout(resizeAllCharts, 60);   // 视图显示后图表重排
}

// ================= 知识库阅读 + 双链跳转 =================
let vaultPages = [], currentFile = '', histStack = [], histIdx = -1, treeCollapsed = {};

async function loadVault() {
  vaultPages = await api('/api/wiki/pages');
  renderTree(vaultPages);
  openPage('编译原理知识库.md', true);
}

function renderTree(pages) {
  const order = ['知识点页', '专题页', '题库页', '题解页', '试卷页', '智能体记录', '索引页'];
  const groups = {};
  pages.forEach(p => { (groups[p.type || '其他'] = groups[p.type || '其他'] || []).push(p); });
  document.getElementById('fileTree').innerHTML = order.filter(t => groups[t]).map(t => {
    const open = !treeCollapsed[t];
    return `<div class="tree-group">
      <div class="tree-folder" onclick="toggleFolder('${t}')">
        <span class="caret">${open ? '▾' : '▸'}</span> ${t} <span class="muted">(${groups[t].length})</span>
      </div>
      <div class="tree-files" style="display:${open ? 'block' : 'none'}">
        ${groups[t].map(p => `<div class="tree-file" data-file="${p.file}"
             onclick="openPage('${p.file}')" title="${p.file}">${p.file.replace(/\.md$/, '')}</div>`).join('')}
      </div>
    </div>`;
  }).join('');
}
function toggleFolder(t) { treeCollapsed[t] = !treeCollapsed[t]; renderTree(vaultPages); }

// 双链目标解析：精确匹配 → 别名 → 关键词搜文件 → 失败标红
function resolveWikiTarget(raw) {
  let target = raw.trim().replace(/\.md$/, '');
  let anchor = '';
  const hashIdx = target.indexOf('#');
  if (hashIdx >= 0) { anchor = target.slice(hashIdx + 1).trim(); target = target.slice(0, hashIdx).trim(); }
  const names = vaultPages.map(p => p.file.replace(/\.md$/, ''));
  let hit = names.find(n => n === target)
    || names.find(n => n === target.replace(/^(专题|题型)\d+[：:]\s*/, ''))
    || names.find(n => n.includes(target) || target.includes(n));
  if (!hit) {
    // 按知识点名模糊定位到包含该知识点的页
    const p = vaultPages.find(p =>
      (p.knowledge_points || []).some(k => target.includes(k) || k.includes(target)));
    if (p) hit = p.file.replace(/\.md$/, '');
  }
  return hit ? { file: hit + '.md', anchor } : null;
}

async function openPage(file, pushHist = true) {
  // 缓存里找不到（如刚生成的记录）→ 直接按路径尝试打开；404 才搜索兜底
  let resolved = resolveWikiTarget(file.replace(/\.md$/, ''));
  if (!resolved) {
    const direct = (file.endsWith('.md') || /\.pdf$/i.test(file)) ? file : file + '.md';
    try {
      await api('/api/wiki/page?name=' + encodeURIComponent(direct));
      resolved = { file: direct, anchor: '' };
    } catch (e) {
      smartLookupFallback(file);
      return;
    }
  }
  const { file: fname, anchor } = resolved;
  currentFile = fname;
  if (pushHist) {
    histStack = histStack.slice(0, histIdx + 1);
    histStack.push({ file: fname, anchor });
    histIdx = histStack.length - 1;
  }
  document.querySelectorAll('.tree-file').forEach(el =>
    el.classList.toggle('active', el.dataset.file === fname));
  openView('read');
  document.getElementById('crumb').textContent = fname.replace(/\.md$/, '');
  updateLinkedChip();
  // 浏览埋点（教师端热力图数据源）
  post('/api/view/record', { file: fname, user_name: MYNAME }).catch(() => { });
  const view = document.getElementById('mdView');
  // PDF/附件 → 内嵌预览（浏览器原生 PDF 渲染）
  if (/\.pdf$/i.test(fname)) {
    view.innerHTML = '<iframe src="/api/wiki/file?name=' + encodeURIComponent(fname) +
      '" style="width:100%;height:78vh;border:none;border-radius:12px;background:#525659"></iframe>';
    document.getElementById('mainScroll').scrollTop = 0;
    loadRelated(fname);
    return;
  }
  view.innerHTML = '<p class="muted">加载中…</p>';
  const page = await api('/api/wiki/page?name=' + encodeURIComponent(fname));
  renderMarkdown(page, anchor);
  loadRelated(fname);
  // 助教上下文默认附加当前文档
  document.getElementById('ctxChip').dataset.file = fname;
  document.getElementById('ctxChip').textContent = '📄 附加 ' + fname.replace(/\.md$/, '') + ' ×';
}

function goBack() {
  if (histIdx > 0) {
    histIdx--;
    const h = histStack[histIdx];
    openPage(h.file, false);
    if (h.anchor) setTimeout(() => scrollToHeading(h.anchor), 300);
  }
}

function renderMarkdown(page, anchor = '') {
  let body = page.body.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (m, target, alias) => {
    const t = target.trim().replace(/\.md$/, '');
    const label = (alias || target).trim();
    return `<a class="wikilink" onclick="openPage('${t.replace(/'/g, '')}')" title="${t}">${label}</a>`;
  });
  const view = document.getElementById('mdView');
  view.innerHTML = marked.parse(body);
  view.querySelectorAll('blockquote').forEach(bq => {
    const first = bq.querySelector('p');
    if (first && /\[!.*?\]/.test(first.textContent)) {
      first.innerHTML = first.textContent.replace(/\[!(.*?)\]/, '<b>💡 $1</b><br>');
    }
  });
  try {
    renderMathInElement(view, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false },
      ],
      throwOnError: false,
    });
  } catch (e) { }
  // 大纲 id
  view.querySelectorAll('h1, h2, h3').forEach((h, i) => h.id = 'hd-' + i);
  if (anchor) setTimeout(() => scrollToHeading(anchor), 120);
  else document.getElementById('mainScroll').scrollTop = 0;
}

function scrollToHeading(anchor) {
  const view = document.getElementById('mdView');
  const hs = [...view.querySelectorAll('h1, h2, h3, strong, b')];
  const target = hs.find(h => h.textContent.replace(/[#\s.]/g, '').includes(anchor.replace(/[#\s.]/g, '')));
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    target.style.background = '#ffe8a3';
    setTimeout(() => target.style.background = '', 1800);
  }
}

function updateLinkedChip() {
  const chip = document.getElementById('linkedChip');
  if (chip) chip.textContent = '🔗 Linked content: ' + (currentFile.replace(/\.md$/, '') || '知识库');
}

// ================= Smart Lookup（快速搜+定位） =================
let lookupTimer = null;
function smartLookup(q) {
  clearTimeout(lookupTimer);
  if (!q.trim()) { document.getElementById('lookupResults').innerHTML = ''; return; }
  lookupTimer = setTimeout(async () => {
    const hits = await api('/api/wiki/search?q=' + encodeURIComponent(q));
    document.getElementById('lookupResults').innerHTML = hits.map(h => `
      <div class="lookup-item" onclick="lookupJump('${h.file}','${q.replace(/'/g, '')}','${(h.anchor||'').replace(/'/g, '')}')">
        <div class="lk-file">${h.file.replace(/\.md$/, '')} <span class="muted">${h.chapter}</span></div>
        <div class="lk-ex">${h.excerpt.replace(new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'), m => '<mark>' + m + '</mark>')}</div>
      </div>`).join('') || '<p class="muted">无匹配</p>';
  }, 220);
}

async function lookupJump(file, q, anchor) {
  await openPage(file);
  await new Promise(r => setTimeout(r, 350));
  const view = document.getElementById('mdView');
  // 高亮目标：优先原查询；语义命中时用锚点短语（保证在原文中存在）
  const targets = [q, anchor].filter(x => x && x.length >= 2);
  let marked = false;
  for (const t of targets) {
    const walker = document.createTreeWalker(view, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      const i = node.textContent.indexOf(t);
      if (i >= 0) {
        const range = document.createRange();
        range.setStart(node, i); range.setEnd(node, i + t.length);
        const mk = document.createElement('mark');
        mk.className = 'hl-active';
        try {
          range.surroundContents(mk);
          mk.scrollIntoView({ behavior: 'smooth', block: 'center' });
          setTimeout(() => { mk.className = 'hl'; }, 1500);
          marked = true;
        } catch (e) { }
        break;
      }
    }
    if (marked) break;
  }
  toast(marked ? '已定位到相关内容' : '已打开「' + file.split('/').pop().replace(/\.md$/, '') + '」');
}

function smartLookupFallback(raw) {
  document.getElementById('lookupInput').value = raw;
  smartLookup(raw);
  toast(`未找到 [[${raw}]]，已用 Smart Lookup 搜索相关内容`);
}

function toast(msg) {
  const t = document.createElement('div');
  t.textContent = msg;
  t.style.cssText = 'position:fixed;bottom:70px;left:50%;transform:translateX(-50%);background:#232936;color:#fff;padding:10px 18px;border-radius:10px;font-size:13px;z-index:99';
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2600);
}

// ================= Smart Connections（关联度：散点地图 + 分数列表） =================
async function loadRelated(file) {
  let list = [];
  try {
    list = await api('/api/wiki/related?name=' + encodeURIComponent(file) + '&k=8');
  } catch (e) { }
  renderConnMap(file, list);
  document.getElementById('relatedList').innerHTML = list.length ? list.map(r => `
    <div class="related-item" onclick="openPage('${r.file}')">
      <div><span class="r-score">${(r.score ?? 0).toFixed(2)}</span>
        <span class="r-file">${r.file.replace(/\.md$/, '').split('/').pop()}</span></div>
      <div class="r-meta">${r.chapter}${(r.kp_overlap || []).length ? ' · 共同: ' + r.kp_overlap.join('/') : ''}</div>
      <div class="r-bar"><i style="width:${Math.min((r.score ?? 0) * 100, 100).toFixed(0)}%"></i></div>
    </div>`).join('') : '<p class="muted">暂无关联</p>';
}

function renderConnMap(file, list) {
  const el = document.getElementById('connMap');
  if (!el) return;
  const chart = echarts.getInstanceByDom(el) || echarts.init(el);
  const me = file.replace(/\.md$/, '').split('/').pop();
  const shortName = s => s.length > 10 ? s.slice(0, 9) + '…' : s;
  const nodes = [{
    name: me, x: 0, y: 0, symbolSize: 36,
    itemStyle: { color: '#22c55e', borderColor: '#fff', borderWidth: 3,
                 shadowBlur: 16, shadowColor: 'rgba(34,197,94,.45)' },
    label: { show: true, position: 'top', fontSize: 10.5, fontWeight: 'bold',
             color: '#15803d', formatter: shortName(me) },
  }];
  const links = [];
  const n = Math.max(list.length, 1);
  list.forEach((r, i) => {
    const score = r.score ?? 0;
    const angle = (i / n) * Math.PI * 2 + 0.45;
    const dist = (1 - score) * 205 + 92;
    const short = r.file.replace(/\.md$/, '').split('/').pop();
    nodes.push({
      name: short,
      x: Math.cos(angle) * dist, y: Math.sin(angle) * dist,
      symbolSize: 13 + score * 17,
      itemStyle: {
        color: 'rgba(124,92,255,' + (0.5 + score * 0.5).toFixed(2) + ')',
        borderColor: '#fff', borderWidth: 2.5,
        shadowBlur: 10, shadowColor: 'rgba(124,92,255,.32)',
      },
      label: { show: true, position: 'bottom', fontSize: 9, color: '#5b6178',
               formatter: shortName(short) + '\n' + score.toFixed(2) },
      file: r.file,
    });
    links.push({
      source: me, target: short,
      lineStyle: { width: 1 + score * 2.4, opacity: 0.14 + score * 0.3,
                   curveness: 0.14, color: '#8b7cf6' },
    });
  });
  chart.setOption({
    tooltip: { formatter: p => p.data.file ? '关联度 ' + ((p.data.value ?? 0).toFixed?.(2) || '') + '<br/>' + p.name + '<br/>点击打开' : '当前文档：' + me },
    xAxis: { show: false, min: -335, max: 335 },
    yAxis: { show: false, min: -335, max: 335 },
    grid: { left: 4, right: 4, top: 16, bottom: 4 },
    series: [{
      type: 'graph', layout: 'none', roam: true, draggable: true,
      data: nodes, links: links,
      lineStyle: { color: '#8b7cf6' },
      emphasis: { focus: 'adjacency', lineStyle: { opacity: 0.65 } },
      labelLayout: { hideOverlap: true },
    }],
  }, true);
  chart.resize();
  setTimeout(() => chart.resize(), 80);
  chart.off('click');
  chart.on('click', p => { if (p.data.file) openPage(p.data.file); });
}

// ================= TeleAgent 助教（Claudian 式） =================
let hintFirst = true;

function pushMsg(cls, html) {
  const log = document.getElementById('chatLog');
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  div.innerHTML = html;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

// / 命令与技能由下方 Skill 区的命令面板统一处理

// 五功能：左栏 TOOLS 与助教 chips 共用 —— 中栏执行 + 助教汇报
async function runTool(name) {
  openView(name);
  const log = document.getElementById('chatLog');
  const greet = log.querySelector('.greet');
  if (greet) greet.remove();
  const label = { graph: '🗺 考点地图', quiz: '✏️ 自测', diag: '🎯 薄弱诊断', plan: '📅 复习计划', variant: '🔁 变式训练' }[name];
  if (name === 'quiz') {
    await startQuiz();
    pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>已为你开始一轮自测（中栏作答）。做完我帮你归因错题、更新薄弱诊断。`);
  } else if (name === 'diag') {
    const list = await api('/api/quiz/weakness?student_id=' + SID);
    loadWeakness();
    const top = list.slice(0, 3).map(w => `<div class="card-mini">🔴 <b>${w.kp}</b> — 正确率 ${(w.accuracy * 100).toFixed(0)}%</div>`).join('')
      || '<div class="card-mini">暂无答题记录，先做一轮自测吧</div>';
    pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>薄弱诊断已更新，当前最需要补的：<div>${top}</div>`);
  } else if (name === 'plan') {
    pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>在中栏选好考试日期，点「生成计划」；或直接回复 <b>/plan 2026-12-10</b> 我来生成。`);
  } else if (name === 'variant') {
    loadVariantList();
    pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>变式题库已打开（中栏）。出新题输 <b>/variant</b>，可粘贴原型题或章节内容。`);
  } else if (name === 'graph') {
    pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>考点地图已打开（中栏）。第2章权重最高（32%），第5章其次（23%）——建议优先这两章。`);
  }
  toast('已打开：' + label);
}

async function ask() {
  const input = document.getElementById('chatQ');
  let q = input.value.trim();
  if (!q && !quotedText) return;
  // 选中引用作为上下文随问题一起输入模型
  if (quotedText) {
    q = (q ? q + '\n\n' : '') + '【我选中的资料片段】\n' + quotedText;
    clearQuote();
  }
  if (!q) return;
  // /技能 要求 → skill 调用（agent 调 skill → 模型思考 → 受约束回答）
  if (q.startsWith('/')) {
    const m = q.match(/^\/(\S+)\s*([\s\S]*)$/);
    const hit = m && skillCatalog.find(s => s.name === m[1]);
    if (hit) {
      input.value = '';
      runSkill(hit.name, { req: (m[2] || '').trim() });
      return;
    }
  }
  // /plan YYYY-MM-DD 快捷
  const planMatch = q.match(/^\/plan\s+(\d{4}-\d{2}-\d{2})/);
  if (planMatch) {
    input.value = '';
    runSkill('plan', { req: planMatch[1], exam_date: planMatch[1] });
    return;
  }
  input.value = '';
  const log = document.getElementById('chatLog');
  const greet = log.querySelector('.greet');
  if (greet) greet.remove();
  const ctxFile = document.getElementById('ctxChip').dataset.file || '';
  pushMsg('user', q);
  const thinking = pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>检索知识库中…`);
  try {
    const r = await post('/api/ask', {
      question: q, student_id: SID, context_file: ctxFile,
      hint_first: document.getElementById('hintFirst').checked,
    });
    const srcs = (r.sources || []).map(s =>
      `${s.file || s.document_name || ''}${s.chapter ? '（' + s.chapter + '）' : ''}`).join('；');
    thinking.innerHTML = `<span class="ta-tag">TeleAgent</span><br><div class="md-out">${marked.parse(r.answer || '')}</div>
      ${srcs ? `<span class="src">📎 资料出处：${srcs}</span>` : ''}`;
  } catch (e) {
    thinking.innerHTML = `<span class="ta-tag">TeleAgent</span><br>出错了：${e.message}`;
  }
  log.scrollTop = log.scrollHeight;
}

// ================= 注册 =================
function registerStudent() {
  const name = document.getElementById('studentName').value || MYNAME;
  SID = Math.abs(hashCode(name)) % 100000 || 1;
  document.getElementById('sidBadge').textContent = name + ' #' + SID;
}
function hashCode(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) { h = (h << 5) - h + s.charCodeAt(i); h |= 0; }
  return h;
}
registerStudent();

// ================= 考点图谱 =================
let graphDrawn = false;
const LEVEL_COLOR = { '必考': '#e8590c', '常考': '#3b5bdb', '了解': '#868e96' };

async function drawGraph() {
  const graphData = await api('/api/graph');
  const chart = echarts.init(document.getElementById('graphChart'));
  const trunc = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s;

  // 标签分级规则：一级(章节)/二级(知识点)常显，三级(考点)放大后才显示
  let zoomLevel = 1;
  let showEp = false;
  const buildNodes = (showExam) => graphData.nodes.map(n => {
    if (n.type === 'chapter') {
      return { ...n, symbolSize: 46, category: 0,
        label: { show: true, fontSize: 12, fontWeight: 'bold', formatter: p => trunc(p.name, 14) } };
    }
    if (n.type === 'knowledge_point') {
      return { ...n, symbolSize: 22 + (n.weight || 3) * 1.2, category: 1,
        label: { show: true, fontSize: 9.5, color: '#444', formatter: p => trunc(p.name, 10) } };
    }
    return { ...n, symbolSize: 10 + (n.weight || 1) * 1.6, category: 2,
      itemStyle: { color: LEVEL_COLOR[n.level] || '#aaa' },
      label: { show: showExam, fontSize: 8.5, color: '#666', formatter: p => trunc(p.name, 8) } };
  });

  chart.setOption({
    tooltip: {
      formatter: p => {
        const d = p.data;
        if (d.type === 'chapter') return d.name;
        if (d.type === 'knowledge_point') return `知识点：${d.name}<br/>权重：${d.weight}`;
        return `考点：${d.name}<br/>级别：${d.level} · 权重：${d.weight}<br/>题型：${d.qtype || '-'}`;
      },
    },
    legend: { data: ['章节', '知识点', '考点'], bottom: 0 },
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true,
      force: { repulsion: 120, edgeLength: [40, 130], gravity: 0.12 },
      categories: [{ name: '章节' }, { name: '知识点' }, { name: '考点' }],
      nodes: buildNodes(false), links: graphData.links,
      lineStyle: { color: '#cdd3e1', curveness: 0.08 },
      emphasis: { focus: 'adjacency', lineStyle: { width: 2 } },
      labelLayout: { hideOverlap: true },
    }],
  });

  // 滚轮/手势放大到阈值 → 显示三级考点标签；缩回 → 隐藏
  chart.on('georoam', params => {
    if (params.zoom) {
      zoomLevel = Math.max(0.3, zoomLevel * params.zoom);
      const want = zoomLevel >= 1.5;
      if (want !== showEp) {
        showEp = want;
        chart.setOption({ series: [{ nodes: buildNodes(showEp) }] });
      }
    }
  });
  chart.on('click', p => {
    const d = p.data;
    const el = document.getElementById('graphInfo');
    if (d.type === 'chapter') {
      el.innerHTML = `<h3>${d.name}</h3><p class="muted">点击知识点/考点查看详情</p>`;
    } else if (d.type === 'knowledge_point') {
      const src = (d.sources || [])[0];
      el.innerHTML = `<h3>${d.name}</h3>
        <p><span class="tag">知识点</span><span class="tag">${d.chapter}</span></p>
        <p>综合权重：<b>${d.weight}</b></p>
        <p class="muted">资料：${(d.sources || []).join('、')}</p>
        ${src ? `<button class="ghost" onclick="openPage('${src}')">📖 打开知识库文档 →</button>` : ''}`;
    } else {
      el.innerHTML = `<h3>${d.name}</h3>
        <p><span class="tag ${d.level === '必考' ? 'must' : ''}">${d.level}</span><span class="tag">${d.qtype || ''}</span></p>
        <p>权重：<b>${d.weight}</b> · ${d.kp}（${d.chapter}）</p>
        <button class="primary" onclick="quickVariant('${(d.kp || '').replace(/'/g, '')}')">针对此考点练变式</button>`;
    }
  });
  graphDrawn = true;
  graphDataCache = graphData;
  const byCh = {}, srcByCh = {};
  graphData.nodes.filter(n => n.type === 'exam_point').forEach(n => {
    byCh[n.chapter] = (byCh[n.chapter] || 0) + (n.weight || 0);
  });
  graphData.nodes.filter(n => n.type === 'knowledge_point').forEach(n => {
    if (!srcByCh[n.chapter] && (n.sources || []).length) srcByCh[n.chapter] = n.sources[0];
  });
  chapterSrcByCh = srcByCh;
  const max = Math.max(...Object.values(byCh), 1);
  document.getElementById('chapterBars').innerHTML = Object.entries(byCh).map(([ch, w]) => `
    <div class="card chapter-card" title="点击打开该章知识库" onclick="openChapterDoc('${ch.replace(/'/g, '')}')">
      <h3>${ch}</h3><div class="num">${w.toFixed(1)}</div>
      <div class="bar"><i style="width:${(w / max * 100).toFixed(0)}%"></i></div>
      <p class="muted">考点权重占比 · 点击阅读 →</p></div>`).join('');
}

let graphDataCache = null, chapterSrcByCh = {};

function openChapterDoc(ch) {
  const go = (file) => {
    openPage(file);
    // 图谱视图里顺带高亮该章节点
    const chart = echarts.getInstanceByDom(document.getElementById('graphChart'));
    if (chart) {
      chart.dispatchAction({ type: 'highlight', seriesIndex: 0, name: ch });
      setTimeout(() => chart.dispatchAction({ type: 'downplay', seriesIndex: 0, name: ch }), 1600);
    }
  };
  const file = chapterSrcByCh[ch]
    || vaultPages.find(p => p.chapter === ch && p.type === '知识点页')?.file
    || vaultPages.find(p => p.chapter === ch)?.file;
  if (file) go(file);
  else toast('未找到该章文档');
}

// ================= 选中文字 → 引用进对话（作为上下文） =================
let quotedText = '';

function setQuote(text) {
  quotedText = text.trim();
  const chip = document.getElementById('quoteChip');
  if (!chip) return;
  if (quotedText) {
    document.getElementById('quoteText').textContent = '📎 引用：' + quotedText;
    chip.style.display = 'flex';
    document.getElementById('chatQ').focus();
    toast('已引用选中文字，将作为上下文随问题发给模型');
  } else chip.style.display = 'none';
}

function clearQuote() {
  quotedText = '';
  const chip = document.getElementById('quoteChip');
  if (chip) chip.style.display = 'none';
}

// 阅读区选中 → 浮现"引用"按钮
document.addEventListener('mouseup', e => {
  const view = document.getElementById('mdView');
  const float = document.getElementById('quoteFloat');
  if (view.contains(e.target)) {
    const sel = window.getSelection().toString();
    if (sel.length >= 4) {
      if (!float) {
        const b = document.createElement('button');
        b.id = 'quoteFloat';
        b.className = 'quote-float';
        b.textContent = '💬 引用到对话';
        b.onmousedown = ev => {
          ev.preventDefault();
          setQuote(window.getSelection().toString());
          window.getSelection().removeAllRanges();
          b.remove();
        };
        document.body.appendChild(b);
      }
      const f = document.getElementById('quoteFloat');
      f.style.left = Math.min(e.pageX + 10, window.innerWidth - 140) + 'px';
      f.style.top = (e.pageY + 16) + 'px';
      f.style.display = 'block';
      return;
    }
  }
  if (float) float.remove();
});

// ================= Skill 技能（助教调用 → 思考 → 检查 → 入库记录） =================
let skillCatalog = [];

async function loadSkillChips() {
  try {
    skillCatalog = await api('/api/skills');
    document.getElementById('assistChips').innerHTML = skillCatalog.map(s =>
      `<button class="chip-btn" title="${s.desc}" onclick="pickSkill('${s.name}')">${s.label}</button>`).join('');
  } catch (e) { }
}

// ---------- / 命令面板 + @ 文档选择器（Claudian 式） ----------
function onChatInput(val) {
  const menu = document.getElementById('cmdMenu');
  if (val.startsWith('/')) {
    const q = val.slice(1).toLowerCase().split(' ')[0];
    const hits = skillCatalog.filter(s =>
      s.name.includes(q) || s.label.toLowerCase().includes(q) || s.desc.includes(q));
    menu.innerHTML = hits.map((s, i) => `
      <div class="cmd-item ${i === 0 ? 'sel' : ''}" onclick="pickSkill('${s.name}')">
        <div class="cmd-name"><span class="cmd-tag">/${s.name}</span>${s.label}</div>
        <div class="cmd-desc">${s.desc}</div>
        <div class="cmd-use">▸ 示例：${s.usage}</div>
        <div class="cmd-rules">规则：${s.rules.join(' · ')}</div>
      </div>`).join('') ||
      `<div class="cmd-item"><div class="cmd-desc">无匹配技能。可用：${skillCatalog.map(s => '/' + s.name).join('  ')}</div></div>`;
    menu.classList.add('show');
    return;
  }
  if (val.startsWith('@')) {
    const q = val.slice(1).trim().toLowerCase();
    const hits = vaultPages.filter(p =>
      p.file.replace(/\.md$/, '').toLowerCase().includes(q)).slice(0, 8);
    menu.innerHTML = hits.map((p, i) => `
      <div class="cmd-item ${i === 0 ? 'sel' : ''}" onclick="pickDoc('${p.file}')">
        <div class="cmd-name"><span class="cmd-tag">@</span>${p.file.replace(/\.md$/, '').split('/').pop()}</div>
        <div class="cmd-desc">${p.chapter || p.type || ''}</div>
      </div>`).join('') || '<div class="cmd-item"><div class="cmd-desc">无匹配文档</div></div>';
    menu.classList.add('show');
    return;
  }
  menu.classList.remove('show');
}

function pickDoc(file) {
  document.getElementById('ctxChip').dataset.file = file;
  document.getElementById('ctxChip').textContent = '📄 附加 ' + file.replace(/\.md$/, '').split('/').pop() + ' ×';
  document.getElementById('chatQ').value = '';
  document.getElementById('cmdMenu').classList.remove('show');
  document.getElementById('chatQ').focus();
  toast('已切换关联文档：' + file.replace(/\.md$/, '').split('/').pop());
}

function pickSkill(name) {
  const input = document.getElementById('chatQ');
  input.value = '/' + name + ' ';
  input.focus();
  document.getElementById('cmdMenu').classList.remove('show');
}

function onChatKey(e) {
  // IME 组合中的回车：先让输入法确认候选词，确认后自动发送
  if (e.isComposing || e.keyCode === 229 || __imeComposing) {
    if (e.key === 'Enter' && !e.shiftKey) __imePendingSend = true;
    return;
  }
  const menu = document.getElementById('cmdMenu');
  const input = document.getElementById('chatQ');
  if (menu.classList.contains('show')) {
    const items = [...menu.querySelectorAll('.cmd-item')];
    const cur = items.findIndex(x => x.classList.contains('sel'));
    if (e.key === 'ArrowDown') { e.preventDefault(); if (items[cur + 1]) { items[cur].classList.remove('sel'); items[cur + 1].classList.add('sel'); } return; }
    if (e.key === 'ArrowUp') { e.preventDefault(); if (items[cur - 1]) { items[cur].classList.remove('sel'); items[cur - 1].classList.add('sel'); } return; }
    if (e.key === 'Escape') { menu.classList.remove('show'); return; }
    if (e.key === 'Enter') {
      e.preventDefault();
      const sel = items[cur];
      if (sel) sel.click();   // 通用：/ 技能项和 @ 文档项都直接点选中项
      return;
    }
    return;
  }
  if (e.key === 'Enter') {
    if (e.shiftKey) return;   // Shift+Enter 换行（textarea 默认行为）
    e.preventDefault();
    ask();
  }
}

async function runSkill(name, params = {}) {
  const log = document.getElementById('chatLog');
  const greet = log.querySelector('.greet');
  if (greet) greet.remove();
  const s = skillCatalog.find(x => x.name === name);
  const label = s ? s.label : name;
  // ① 用户：技能 + 要求
  pushMsg('user', `▶ <b>${label}</b>${params.req ? '<br>' + params.req : ''}`);
  // ② 模型思考（受约束）
  const thinking = pushMsg('bot',
    `<span class="ta-tag">TeleAgent · ${label}</span><br>🧠 模型思考中…<br>
     <span class="src">约束规则：${(s ? s.rules : []).join(' ✓ ')}</span>`);
  try {
    if (['quiz', 'diagnosis', 'plan', 'variant'].includes(name) && !params.student_id) {
      params.student_id = SID;
    }
    const r = await post('/api/skills/run', {
      skill: name, params,
      effort: (document.getElementById('effortSel') || {}).value || 'high',
      kb_write: (document.getElementById('kbWrite') || {}).checked !== false,
    });
    thinking.innerHTML = `<span class="ta-tag">TeleAgent · ${r.label || ''}</span><br>
      <div class="md-out">${marked.parse(r.output || '')}</div>
      ${r.record_file ? `<div class="card-mini">📄 <a class="wikilink" onclick="openPage('${r.record_file}')">打开知识库记录 →</a></div>` : ''}
      <span class="src">✅ 规则检查通过：${(r.rules || []).join(' ✓ ')}</span>`;
    if (r.record_file) refreshTree();
    updateCtxStats();
  } catch (e) {
    thinking.innerHTML = `<span class="ta-tag">TeleAgent</span><br>❌ ${e.message}`;
  }
  log.scrollTop = log.scrollHeight;
}

// ================= 自测 =================
let quizList = [], quizIdx = 0, quizRight = 0;

async function startQuiz() {
  quizList = await api('/api/quiz/questions?limit=10');
  quizIdx = 0; quizRight = 0;
  renderQuiz();
}

function renderQuiz() {
  const area = document.getElementById('quizArea');
  if (quizIdx >= quizList.length) {
    area.innerHTML = `<div class="quiz-q"><h3>本轮完成 ✅</h3>
      <p>正确 ${quizRight} / ${quizList.length}</p>
      <button class="primary" onclick="runTool('diag')">看薄弱诊断 →</button></div>`;
    return;
  }
  const q = quizList[quizIdx];
  area.innerHTML = `
    <div class="quiz-q">
      <p><span class="tag">${q.type}</span>
        <span class="tag ${q.qtype.includes('题型') ? 'must' : ''}">${q.qtype}</span>
        <span class="tag">${q.kp}</span>
        <span class="muted">${quizIdx + 1} / ${quizList.length}</span></p>
      <p style="font-size:15px;line-height:1.8">${q.q}</p>
      <div id="opts">${q.options.map((o, i) =>
        `<button class="opt" onclick="answer(${i})">${'ABCD'[i]}. ${o}</button>`).join('')}</div>
      <div id="fb"></div>
    </div>`;
}

async function answer(i) {
  const q = quizList[quizIdx];
  const std = await api('/api/quiz/answer?question_id=' + q.id);
  const ok = i === std.answer;
  if (ok) quizRight++;
  document.querySelectorAll('#opts .opt').forEach((b, j) => {
    b.onclick = null;
    if (j === std.answer) b.classList.add('right');
    if (j === i && !ok) b.classList.add('wrong');
  });
  const nextBtn = `<button class="primary" onclick="renderQuiz()">下一题 →</button>`;
  if (!ok) {
    const r = await post('/api/quiz/submit', {
      student_id: SID, question_id: q.id, kp: q.kp, qtype: q.qtype,
      correct: false, question_text: q.q,
      student_answer: q.options[i], right_answer: q.options[std.answer],
    });
    document.getElementById('fb').innerHTML =
      `<p class="muted">已入错题本 · 错因归类：<b>${r.error_cause}</b> · 出处：${std.source}</p>${nextBtn}`;
  } else {
    post('/api/quiz/submit', {
      student_id: SID, question_id: q.id, kp: q.kp, qtype: q.qtype, correct: true,
    });
    document.getElementById('fb').innerHTML =
      `<p class="muted" style="color:var(--ok)">回答正确 · 出处：${std.source}</p>${nextBtn}`;
  }
  quizIdx++;
}

// ================= 诊断 =================
async function loadWeakness() {
  const list = await api('/api/quiz/weakness?student_id=' + SID);
  const el = document.getElementById('weakList');
  if (!list.length) {
    el.innerHTML = '<p class="muted">还没有答题记录——先去「自测刷题」做一轮。</p>';
    return;
  }
  el.innerHTML = list.map((w, i) => `
    <div class="weak-item">
      <div class="row space">
        <div><b>#${i + 1} ${w.kp}</b><p class="muted">已练 ${w.total} 题</p></div>
        <div style="text-align:right">
          <div class="acc" style="color:${w.accuracy < 0.6 ? 'var(--bad)' : 'var(--ok)'}">${(w.accuracy * 100).toFixed(0)}%</div>
          <p class="muted">正确率</p></div>
      </div>
      <div>${Object.entries(w.error_causes).map(([c, n]) => `<span class="cause-chip">${c} × ${n}</span>`).join('')}</div>
      <button class="ghost" style="margin-top:8px" onclick="quickVariant('${w.kp.replace(/'/g, '')}')">练变式题 →</button>
    </div>`).join('');
}

// ================= 计划 =================
document.getElementById('examDate').value =
  new Date(Date.now() + 21 * 864e5).toISOString().slice(0, 10);

async function genPlan() {
  const exam_date = document.getElementById('examDate').value;
  const r = await post('/api/plan/generate', { student_id: SID, exam_date });
  genPlanTo(document.getElementById('planArea'), r);
}

// 教师布置的作业（计划页展示）
async function loadHomework() {
  try {
    const list = await api('/api/teacher/homework');
    const el = document.getElementById('hwArea');
    if (!el) return;
    el.innerHTML = list.length ? list.map(h => `
      <div class="card">
        <h3>📋 ${h.title}</h3>
        <p><span class="tag">${h.kp || '综合'}</span>
           <span class="muted">截止 ${h.due_date || '未定'} · ${h.teacher || ''}</span></p>
        <p class="muted">${(h.detail || '').slice(0, 80)}</p>
      </div>`).join('') : '<p class="muted">暂无作业</p>';
  } catch (e) { }
}

function genPlanTo(el, r) {
  el.innerHTML = r.plan.map(d => `
    <div class="card"><h3>Day ${d.day} · ${d.date}</h3>
    ${d.tasks.map(t => `<p style="margin:6px 0"><b>${t.kp}</b><br>
      <span class="muted">${t.action}｜目标：${t.goal}</span></p>`).join('')}</div>`).join('') +
    `<div class="card"><h3>⏱ 生成耗时</h3><div class="num">${r.elapsed_s}s</div>
     <p class="muted">${r.days} 天计划 · 倒计时精确到考试日</p></div>`;
}

// ================= 变式（页内纯展示，生成走 skill） =================
let kpList = [];

function goVariantSkill() {
  pickSkill('variant');
  document.getElementById('chatQ').focus();
  toast('在助教输入要求（可粘贴原型题/章节内容），回车生成');
}

async function loadVariantList() {
  const list = await api('/api/variants?student_id=' + SID);
  const el = document.getElementById('variantArea');
  if (!list.length) {
    el.innerHTML = '<p class="muted">还没有变式题——点右上角「生成新变式题」，或在助教里输入 /variant。</p>';
    return;
  }
  el.innerHTML = list.map((r, i) => {
    const v = r.variant || {};
    const ans = typeof v.answer === 'object'
      ? Object.entries(v.answer).map(([k, a]) => `<p><b>${k}</b>：${a}</p>`).join('')
      : `<p>${v.answer || ''}</p>`;
    return `
    <div class="variant-box">
      <p><span class="tag must">变式题</span><span class="tag">${r.kp}</span>
        <span class="muted">#${list.length - i}</span></p>
      <p style="white-space:pre-wrap;font-size:15px;line-height:1.9">${(v.question || '').replace(/\n/g, '<br>')}</p>
      <button class="ghost" onclick="this.nextElementSibling.style.display='block'">💡 先看提示</button>
      <div style="display:none;margin-top:10px" class="answer-box"><b>提示：</b>${v.hint || ''}</div>
      <button class="ghost" style="margin-top:10px" onclick="this.nextElementSibling.style.display='block'">📖 再看解答</button>
      <div style="display:none;margin-top:10px" class="answer-box">${ans}
        <ol class="steps">${(v.steps || []).map(s => `<li>${s}</li>`).join('')}</ol></div>
    </div>`;
  }).join('');
}

function quickVariant(kp) {
  openView('variant');
  loadVariantList();
  pickSkill('variant');
  const input = document.getElementById('chatQ');
  input.value = '/variant 针对「' + kp + '」出一道同源变式题';
  input.focus();
  toast('已填好要求，回车即可生成');
}

// ================= 启动 =================
document.getElementById('ctxChip').onclick = () => {
  const chip = document.getElementById('ctxChip');
  chip.dataset.file = '';
  chip.textContent = '📄 不附加文档 ×';
};
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    document.getElementById('lookupInput').focus();
  }
});

// 图表动态自适应（逐容器观察：视图切换/侧栏拖拽/窗口缩放都触发）
function resizeAllCharts() {
  document.querySelectorAll('.chart, .conn-map').forEach(el => {
    const inst = echarts.getInstanceByDom(el);
    if (inst) inst.resize();
  });
}
window.addEventListener('resize', resizeAllCharts);
function observeCharts() {
  document.querySelectorAll('.chart, .conn-map').forEach(el => {
    if (el.__obs) return;
    el.__obs = true;
    new ResizeObserver(() => {
      const inst = echarts.getInstanceByDom(el);
      if (inst) inst.resize();
    }).observe(el);
  });
}
const __chartObs = new ResizeObserver(() => { resizeAllCharts(); observeCharts(); });
__chartObs.observe(document.getElementById('mainScroll'));
observeCharts();

// 模型芯片显示实际配置
api('/api/config/status').then(c => {
  const chip = document.getElementById('modelChip');
  if (chip) chip.textContent = c.llm_model + (c.llm_configured ? '' : '（未配Key）');
}).catch(() => { });

loadVault();
loadSkillChips();


// ================= 课程切换（多知识库可复用） =================
async function switchCourse(cid) {
  localStorage.setItem('ta_course', cid);
  await post('/api/courses/switch', { course_id: cid }).catch(() => { });
  location.reload();
}

async function loadCourseBar() {
  try {
    const courses = await api('/api/courses');
    let bar = document.getElementById('courseBar');
    if (!bar) return;
    bar.innerHTML = courses.map(c =>
      `<option value="${c.id}" ${c.id === COURSE_ID ? 'selected' : ''}>${c.name}</option>`).join('');
  } catch (e) { }
}
loadCourseBar();


// ================= 快速搜索弹窗（Obsidian 式 Quick Search） =================
let srIdx = 0, srHits = [];

function openSearch() {
  const m = document.getElementById('searchModal');
  m.classList.add('show');
  const inp = document.getElementById('searchInput');
  inp.value = '';
  inp.focus();
  document.getElementById('searchResults').innerHTML =
    '<div class="search-empty">输入关键词或问题开始搜索</div>';
}

function closeSearch() {
  document.getElementById('searchModal').classList.remove('show');
}

function doSearch(q) {
  clearTimeout(window.__srTimer);
  if (!q.trim()) {
    document.getElementById('searchResults').innerHTML =
      '<div class="search-empty">输入关键词或问题开始搜索</div>';
    return;
  }
  window.__srTimer = setTimeout(async () => {
    const hits = await api('/api/wiki/search?q=' + encodeURIComponent(q) + '&k=8');
    srHits = hits; srIdx = 0;
    renderSearchResults(q);
  }, 200);
}

function renderSearchResults(q) {
  const box = document.getElementById('searchResults');
  if (!srHits.length) {
    box.innerHTML = '<div class="search-empty">未找到相关内容</div>';
    return;
  }
  box.innerHTML = srHits.map((h, i) => {
    const snips = (h.snippets || [h.excerpt || '']).slice(0, 3).map(s => {
      const esc = s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
      const hl = esc.replace(new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi'),
        m => '<mark>' + m + '</mark>');
      return '<div class="sr-snip">- ' + hl + '</div>';
    }).join('');
    return `<div class="sr-item ${i === 0 ? 'sel' : ''}" data-i="${i}" onclick="pickSearch(${i})">
      <div class="sr-head">
        <span class="sr-name">${h.file.replace(/\.md$/, '').split('/').pop()}</span>
        <span class="sr-count">${h.match_count || 1} matches · ${h.chapter || ''}</span>
      </div>
      <div class="sr-snips">${snips}</div>
    </div>`;
  }).join('');
}

function moveSearchSel(d) {
  const items = document.querySelectorAll('.sr-item');
  if (!items.length) return;
  items[srIdx]?.classList.remove('sel');
  srIdx = (srIdx + d + items.length) % items.length;
  items[srIdx].classList.add('sel');
  items[srIdx].scrollIntoView({ block: 'nearest' });
}

function pickSearch(i) {
  const h = srHits[i];
  if (!h) return;
  closeSearch();
  const q = document.getElementById('searchInput').value.trim();
  lookupJump(h.file, q, h.anchor);
}

// 搜索框点击/⌘K 唤起弹窗
document.addEventListener('DOMContentLoaded', () => {});
setTimeout(() => {
  const li = document.getElementById('lookupInput');
  if (li) li.addEventListener('focus', openSearch);
}, 100);

document.addEventListener('keydown', e => {
  const m = document.getElementById('searchModal');
  if (!m || !m.classList.contains('show')) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      openSearch();
    }
    return;
  }
  // 弹窗内键盘导航
  if (e.key === 'Escape') { e.preventDefault(); closeSearch(); }
  else if (e.key === 'ArrowDown') { e.preventDefault(); moveSearchSel(1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); moveSearchSel(-1); }
  else if (e.key === 'Enter') { e.preventDefault(); pickSearch(srIdx); }
});


// 上下文统计条（Claudian 式：词数/字符数实时显示）
function updateCtxStats() {
  const el = document.getElementById('ctxStats');
  if (!el) return;
  const chip = document.getElementById('ctxChip');
  const file = (chip && chip.dataset.file) || '';
  const quote = typeof quotedText !== 'undefined' ? quotedText : '';
  const q = (document.getElementById('chatQ') || {}).value || '';
  const chars = quote.length + q.length;
  const words = (quote + ' ' + q).split(/\s+/).filter(Boolean).length + (file ? 2 : 0);
  const fname = file ? file.replace(/\.md$/, '').split('/').pop() + ' · ' : '';
  el.textContent = fname + words + ' 词 ' + chars + ' 字符';
}


// ================= 插件系统（Obsidian 式：ribbon + 标签页 + 单面板） =================
const PLUGIN_META = {
  assist: { icon: '🤖', name: 'TeleAgent 助教' },
  smartconn: { icon: '🔗', name: 'Smart Connections' },
};
let openPlugins = ['assist'];
let activePlugin = 'assist';

function renderPluginUI() {
  const tabs = document.getElementById('pluginTabs');
  if (tabs) {
    tabs.innerHTML = openPlugins.map(p => `
      <div class="ptab ${p === activePlugin ? 'active' : ''}" onclick="switchPlugin('${p}')">
        <span>${PLUGIN_META[p].icon}</span>
        <span>${PLUGIN_META[p].name}</span>
        <span class="ptab-x" onclick="event.stopPropagation(); closePlugin('${p}')">×</span>
      </div>`).join('');
  }
  document.querySelectorAll('.plugin-panel').forEach(el => {
    el.classList.toggle('active', el.dataset.plugin === activePlugin);
  });
  document.querySelectorAll('.rail-icon').forEach(el => {
    el.classList.toggle('active', el.dataset.plugin === activePlugin);
  });
  if (typeof resizeAllCharts === 'function') setTimeout(resizeAllCharts, 90);
}

function openPlugin(name) {
  if (!PLUGIN_META[name]) return;
  if (!openPlugins.includes(name)) openPlugins.push(name);
  activePlugin = name;
  renderPluginUI();
}

function switchPlugin(name) {
  activePlugin = name;
  renderPluginUI();
}

function closePlugin(name) {
  openPlugins = openPlugins.filter(p => p !== name);
  if (activePlugin === name) activePlugin = openPlugins[openPlugins.length - 1] || null;
  renderPluginUI();
}

renderPluginUI();


// ================= Zen Mode =================
function toggleZen(on) {
  const bar = document.getElementById('zenBar');
  const want = on === undefined ? !bar.classList.contains('show') : on;
  bar.classList.toggle('show', want);
  const right = document.getElementById('sidebarRight');
  if (want) {
    if (right && !right.classList.contains('collapsed')) toggleSidebar('right');
  } else {
    if (right && right.classList.contains('collapsed')) toggleSidebar('right');
    document.getElementById('chatQ') && document.getElementById('chatQ').focus();
  }
  if (want) document.getElementById('zenInput').focus();
}

function zenUpdate(text) {
  const el = document.getElementById('zenActivity');
  if (el && text) el.textContent = 'TeleAgent 助教 · ' + text;
}

// Zen 输入回车 → 转发给主对话
setTimeout(() => {
  const zi = document.getElementById('zenInput');
  if (zi) zi.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const v = zi.value.trim();
    if (!v) return;
    zi.value = '';
    const chatQ = document.getElementById('chatQ');
    if (chatQ) { chatQ.value = v; ask(); }
  });
}, 120);

// ================= Sessions（多会话管理） =================
const SESS_KEY = 'ta_sessions_' + (typeof COURSE_ID !== 'undefined' ? COURSE_ID : 'compiler');
let sessions = [];
let curSess = 0;

function loadSessions() {
  try { sessions = JSON.parse(localStorage.getItem(SESS_KEY) || '[]'); } catch (e) { sessions = []; }
  if (!sessions.length) newSession(true);
}
function saveSessions() {
  try { localStorage.setItem(SESS_KEY, JSON.stringify(sessions.slice(-20))); } catch (e) { }
}
function newSession(silent) {
  sessions.push({ id: Date.now(), title: '新会话', time: new Date().toLocaleString('zh-CN', { hour12: false }), msgs: [] });
  curSess = sessions.length - 1;
  saveSessions();
  if (!silent) {
    const log = document.getElementById('chatLog');
    if (log) log.innerHTML = '<div class="greet"><div class="greet-title">TeleAgent</div><div class="greet-sub">Good day</div><div class="linked-chip" id="linkedChip">🔗 Linked content: 知识库</div></div>';
    renderSessions();
    zenUpdate('新会话已创建');
  }
}
function switchSession(i) {
  curSess = i;
  renderSessions();
  const log = document.getElementById('chatLog');
  const s = sessions[i];
  if (!log || !s) return;
  log.innerHTML = s.msgs.map(m => '<div class="msg ' + m.cls + '">' + m.html + '</div>').join('')
    || '<div class="greet"><div class="greet-title">TeleAgent</div><div class="greet-sub">Good day</div><div class="linked-chip" id="linkedChip">🔗 Linked content: 知识库</div></div>';
  document.querySelectorAll('.sess-item').forEach((el, j) => el.classList.toggle('sel', j === i));
}
function renderSessions() {
  const pop = document.getElementById('sessionsPop');
  if (!pop) return;
  pop.innerHTML = '<button class="sess-new" onclick="newSession()">＋ 新会话</button>' +
    sessions.map((s, i) => `<div class="sess-item ${i === curSess ? 'sel' : ''}" onclick="switchSession(${i})">
      <span class="t">${s.title}</span><span class="d">${s.time}</span></div>`).join('');
}
function toggleSessions() {
  const pop = document.getElementById('sessionsPop');
  if (pop) pop.classList.toggle('show');
}

// 助手：记录消息进当前会话（pushMsg 增强）
function sessRecord(cls, html) {
  if (!sessions.length) loadSessions();
  const s = sessions[curSess];
  if (!s) return;
  s.msgs.push({ cls, html });
  if (s.title === '新会话' && cls === 'user') {
    s.title = html.replace(/<[^>]+>/g, '').slice(0, 18) || s.title;
  }
  s.time = new Date().toLocaleString('zh-CN', { hour12: false });
  saveSessions();
}

// ================= Inline Edit（选中改写） =================
let rewriteBefore = '';

function openRewrite() {
  const sel = window.getSelection().toString();
  if (sel.length < 4) return;
  rewriteBefore = sel;
  const pop = document.getElementById('rewritePop');
  // 定位到选区附近
  const sel0 = window.getSelection().getRangeAt(0).getBoundingClientRect();
  pop.style.left = Math.min(sel0.left, window.innerWidth - 460) + 'px';
  pop.style.top = Math.min(sel0.bottom + 10, window.innerHeight - 380) + 'px';
  pop.classList.add('show');
  document.getElementById('rewriteDiff').innerHTML = '<p class="muted">原文：' + sel.slice(0, 120) + (sel.length > 120 ? '…' : '') + '</p>';
  document.getElementById('rewriteInstr').focus();
}
function closeRewrite() {
  const pop = document.getElementById('rewritePop');
  if (pop) pop.classList.remove('show');
  rewriteBefore = '';
}

async function doRewrite() {
  const instr = document.getElementById('rewriteInstr').value.trim() || '润色';
  const box = document.getElementById('rewriteDiff');
  box.innerHTML = '<p class="muted">改写中…</p>';
  try {
    const r = await post('/api/rewrite', { text: rewriteBefore, instruction: instr });
    window.__rewriteAfter = r.after;
    // 简易 diff：前后段落对比（词级标色留给"应用"后展示）
    box.innerHTML = `<div><b>原文</b><br><span class="diff-del">${rewriteBefore.replace(/\n/g, '<br>')}</span></div>
      <div style="margin-top:8px"><b>改写后</b><br><span class="diff-add">${r.after.replace(/\n/g, '<br>')}</span></div>`;
  } catch (e) {
    box.innerHTML = '<p style="color:var(--bad)">改写失败：' + e.message + '</p>';
  }
}

async function applyRewrite() {
  const after = window.__rewriteAfter;
  if (!after) { toast('请先生成改写'); return; }
  try {
    const r = await post('/api/rewrite/apply', {
      file: (typeof currentFile !== 'undefined' ? currentFile : '') || document.getElementById('ctxChip').dataset.file || '',
      before: rewriteBefore, after, note: 'Inline Edit：' + (document.getElementById('rewriteInstr').value || '润色'),
    });
    if (r.applied) {
      toast('✅ 已应用到知识库');
      if (typeof openPage === 'function') openPage(currentFile, false);
    } else {
      toast('⚠ 只读模式：已记录为勘误单');
    }
    closeRewrite();
  } catch (e) {
    toast('应用失败：' + e.message);
  }
}

// 选中文字 → 浮现按钮组（引用 + 改写）
document.addEventListener('mouseup', e => {
  if (e.target.closest && e.target.closest('.rewrite-pop')) return;
  const view = document.getElementById('mdView');
  const old = document.getElementById('quoteFloat');
  if (view && view.contains(e.target)) {
    const sel = window.getSelection().toString();
    if (sel.length >= 4) {
      if (!old) {
        const b = document.createElement('div');
        b.id = 'quoteFloat';
        b.style.cssText = 'position:absolute;z-index:60;display:flex;gap:6px;';
        b.innerHTML = `
          <button class="quote-float" onclick="setQuote(window.getSelection().toString()); window.getSelection().removeAllRanges(); document.getElementById('quoteFloat').remove();">💬 引用到对话</button>
          <button class="quote-float" style="background:#1677ff" onclick="openRewrite()">✏️ 改写</button>`;
        document.body.appendChild(b);
      }
      const f = document.getElementById('quoteFloat');
      f.style.left = Math.min(e.pageX, window.innerWidth - 320) + 'px';
      f.style.top = (e.pageY + 14) + 'px';
      f.style.display = 'flex';
      return;
    }
  }
  if (old) old.remove();
});

// ================= Cross-Session（/collab 双智能体） =================
async function runCollab(task) {
  const log = document.getElementById('chatLog');
  const greet = log.querySelector('.greet');
  if (greet) greet.remove();
  pushMsg('user', '🤝 多智能体协作：' + task);
  const thinking = pushMsg('bot', '<span class="ta-tag">TeleAgent</span><br>双智能体协作中（教师审阅 ⇄ 学生作答）…');
  try {
    const r = await post('/api/collab', { task, rounds: 2 });
    const lines = r.dialogue.map(d => `
      <div class="collab-line">
        <div class="collab-av ${d.role}">${d.role === 'teacher' ? '👩‍🏫' : '🧑‍🎓'}</div>
        <div style="flex:1">
          <div class="collab-name">${d.agent}</div>
          <div class="collab-bubble">${(d.text || '').replace(/\n/g, '<br>')}</div>
        </div>
      </div>`).join('');
    thinking.innerHTML = `<span class="ta-tag">TeleAgent · 多智能体协作</span><br>
      <div class="collab-wrap">${lines}</div>
      <span class="src">✅ 协作完成 ${r.rounds} 轮 · 终稿见教师智能体意见</span>`;
    zenUpdate('协作完成：' + task.slice(0, 20));
  } catch (e) {
    thinking.innerHTML = '<span class="ta-tag">TeleAgent</span><br>协作失败：' + e.message;
  }
  const logEl = document.getElementById('chatLog');
  logEl.scrollTop = logEl.scrollHeight;
}

// /collab 命令拦截（在 ask() 之前）
const _origAsk = typeof ask === 'function' ? ask : null;
document.addEventListener('keydown', e => {
  if (e.key === 'Enter' && document.activeElement && document.activeElement.id === 'chatQ') {
    const v = document.activeElement.value.trim();
    if (v.startsWith('/collab ') || v.startsWith('/协作 ')) {
      e.preventDefault();
      document.activeElement.value = '';
      runCollab(v.replace(/^\/(collab|协作)\s*/, ''));
    }
  }
}, true);

// 会话按钮注入助教头部
setTimeout(() => {
  const head = document.querySelector('.assist-head');
  if (head && !document.getElementById('sessionsBtn')) {
    const btn = document.createElement('button');
    btn.id = 'sessionsBtn';
    btn.className = 'ghost';
    btn.style.cssText = 'padding:5px 10px;font-size:11.5px';
    btn.textContent = '🗂 会话';
    btn.onclick = toggleSessions;
    head.style.position = 'relative';
    head.appendChild(btn);
    const pop = document.createElement('div');
    pop.id = 'sessionsPop';
    pop.className = 'sessions-pop';
    head.appendChild(pop);
    loadSessions();
    renderSessions();
  }
}, 150);


// ================= IME 回车修复（中文输入法：组合期回车=确认+发送） =================
let __imeComposing = false;
let __imePendingSend = false;

function bindImeEnter(input, handler) {
  if (!input) return;
  input.addEventListener('compositionstart', () => { __imeComposing = true; });
  input.addEventListener('compositionend', () => {
    __imeComposing = false;
    if (__imePendingSend) { __imePendingSend = false; setTimeout(handler, 30); }
  });
}

bindImeEnter(document.getElementById('chatQ'), () => ask());
bindImeEnter(document.getElementById('zenInput'), () => {
  const zi = document.getElementById('zenInput');
  if (zi && zi.value.trim()) { const v = zi.value.trim(); zi.value = ''; const q = document.getElementById('chatQ'); if (q) { q.value = v; ask(); } }
});
bindImeEnter(document.getElementById('searchInput'), () => pickSearch(srIdx));


// Shift+Enter 换行；Enter 发送；自动增高
function autoGrow(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 160) + 'px';
}
