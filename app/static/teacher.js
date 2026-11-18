// ================= 鉴权 =================
const TOKEN = localStorage.getItem('ta_token') || '';
const MYNAME = localStorage.getItem('ta_name') || '教师';
if (!TOKEN || localStorage.getItem('ta_role') !== 'teacher') location.href = '/static/login.html';
document.getElementById('teacherBadge').textContent = MYNAME;

function logout() {
  fetch('/api/auth/logout', { method: 'POST', headers: { 'X-Token': TOKEN } });
  localStorage.clear();
  location.href = '/static/login.html';
}

const COURSE_ID = localStorage.getItem('ta_course') || 'compiler';
let COURSE_NAME = '';

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

function toast(msg) {
  const t = document.createElement('div');
  t.textContent = msg;
  t.style.cssText = 'position:fixed;bottom:70px;left:50%;transform:translateX(-50%);background:#232936;color:#fff;padding:10px 18px;border-radius:10px;font-size:13px;z-index:99';
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 2400);
}

// 死链兜底：转 Smart Lookup 搜索
function smartLookupFallback(raw) {
  const inp = document.getElementById('lookupInput');
  if (inp) inp.value = raw;
  smartLookup(raw);
  toast('未找到「' + raw + '」，已搜索相关内容');
}

// 刷新文件树（skill 产生新记录后即时可见）
async function refreshTree() {
  try {
    vaultPages = await api('/api/wiki/pages');
    renderTree(vaultPages);
  } catch (e) { }
}

// ================= 视图 =================
function openView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + name).classList.add('active');
  document.getElementById('mainScroll').scrollTop = 0;
  if (name === 'graph' && !graphDrawn) drawGraph();
  if (name === 'status') loadStatus();
  if (name === 'heat') loadHeat();
  if (name === 'klass') loadKlass();
  if (name === 'question') loadQuestions();
  if (name === 'homework') loadHomework();
  if (name === 'edit') loadErrata();
  setTimeout(resizeAllCharts, 60);   // 视图显示后图表重排
}

// ================= 知识库阅读（同学生端） =================
let vaultPages = [], currentFile = '', histStack = [], histIdx = -1, treeCollapsed = {};

async function loadVault() {
  vaultPages = await api('/api/wiki/pages');
  renderTree(vaultPages);
  // 默认打开课程首页：索引页 > 根目录 md > 任意 md；空库给出提示（不做搜索兜底）
  const home = vaultPages.find(p => p.type === '索引页' && p.file.endsWith('.md'))
    || vaultPages.find(p => p.file.endsWith('.md') && !p.file.includes('/'))
    || vaultPages.find(p => p.file.endsWith('.md'));
  if (home) {
    openPage(home.file);
  } else {
    document.getElementById('crumb').textContent = (COURSE_NAME || '知识库');
    document.getElementById('mdView').innerHTML =
      '<p class="muted">该课程知识库暂无内容——可用「导入资料 → 提取知识点」构建。</p>';
  }
}

function renderTree(pages) {
  const order = ['知识点页', '专题页', '题库页', '题解页', '试卷页', '智能体记录', '索引页', '文档附件', '其他'];
  const groups = {};
  pages.forEach(p => { (groups[p.type || '其他'] = groups[p.type || '其他'] || []).push(p); });
  const keys = order.filter(t => groups[t]).concat(Object.keys(groups).filter(t => !order.includes(t)));
  document.getElementById('fileTree').innerHTML = keys.map(t => {
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

function resolveWikiTarget(raw) {
  let target = raw.trim().replace(/\.md$/, '');
  const names = vaultPages.map(p => p.file.replace(/\.md$/, ''));
  let hit = names.find(n => n === target)
    || names.find(n => n.includes(target) || target.includes(n));
  if (!hit) {
    const p = vaultPages.find(p =>
      (p.knowledge_points || []).some(k => target.includes(k) || k.includes(target)));
    if (p) hit = p.file.replace(/\.md$/, '');
  }
  return hit ? hit + (/\.pdf$/i.test(hit) ? '' : '.md') : null;
}

async function openPage(file, pushHist = true) {
  // 缓存找不到（如刚生成的记录）→ 直接按路径尝试；404 兜底搜索
  let fname = resolveWikiTarget(file.replace(/\.md$/, ''));
  if (!fname) {
    const direct = (file.endsWith('.md') || /\.pdf$/i.test(file)) ? file : file + '.md';
    try {
      await api('/api/wiki/page?name=' + encodeURIComponent(direct));
      fname = direct;
    } catch (e) {
      smartLookupFallback(file);
      return;
    }
  }
  currentFile = fname;
  if (pushHist) {
    histStack = histStack.slice(0, histIdx + 1);
    histStack.push(fname);
    histIdx = histStack.length - 1;
  }
  document.querySelectorAll('.tree-file').forEach(el =>
    el.classList.toggle('active', el.dataset.file === fname));
  openView('read');
  document.getElementById('crumb').textContent = fname.replace(/\.md$/, '');
  const chip = document.getElementById('ctxChip');
  chip.dataset.file = fname;
  chip.textContent = '📄 附加 ' + fname.replace(/\.md$/, '') + ' ×';
  const lc = document.getElementById('linkedChip');
  if (lc) lc.textContent = '🔗 Linked content: ' + fname.replace(/\.md$/, '');
  // 浏览埋点
  post('/api/view/record', { file: fname, user_name: MYNAME }).catch(() => { });
  const view = document.getElementById('mdView');
  // PDF/附件 → 内嵌预览（浏览器原生 PDF 渲染）
  if (/\.pdf$/i.test(fname)) {
    view.innerHTML = '<iframe src="/api/wiki/file?name=' + encodeURIComponent(fname) +
      '&course=' + encodeURIComponent(COURSE_ID) + '&token=' + encodeURIComponent(TOKEN) +
      '" style="width:100%;height:78vh;border:none;border-radius:12px;background:#525659"></iframe>';
    document.getElementById('mainScroll').scrollTop = 0;
    loadRelated(fname);
    return;
  }
  view.innerHTML = '<p class="muted">加载中…</p>';
  const page = await api('/api/wiki/page?name=' + encodeURIComponent(fname));
  let body = page.body.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (m, target, alias) => {
    const t = target.trim().replace(/\.md$/, '');
    return `<a class="wikilink" onclick="openPage('${t.replace(/'/g, '')}')" title="${t}">${(alias || target).trim()}</a>`;
  });
  view.innerHTML = renderMD(body);
  // 行内代码中的文件路径（如 原始资料/xxx.md）→ 可点击打开
  view.querySelectorAll('code').forEach(c => {
    const t = c.textContent.trim();
    const hit = vaultPages.find(p => p.file === t || p.file === t + '.md');
    if (hit && !c.closest('a')) {
      const a = document.createElement('a');
      a.className = 'wikilink';
      a.title = hit.file;
      a.textContent = t;
      a.onclick = () => openPage(hit.file);
      c.replaceWith(a);
    }
  });
  try {
    renderMathInElement(view, {
      delimiters: [{ left: '$$', right: '$$', display: true }, { left: '$', right: '$', display: false }],
      throwOnError: false,
    });
  } catch (e) { }
  document.getElementById('mainScroll').scrollTop = 0;
  loadRelated(fname);
}

function goBack() {
  if (histIdx > 0) {
    histIdx--;
    openPage(histStack[histIdx], false);
  }
}

// ================= Smart Lookup =================
let lookupTimer = null;
function smartLookup(q) {
  clearTimeout(lookupTimer);
  if (!q.trim()) { document.getElementById('lookupResults').innerHTML = ''; return; }
  lookupTimer = setTimeout(async () => {
    const hits = await api('/api/wiki/search?q=' + encodeURIComponent(q));
    const maxS = Math.max(...hits.map(x => x.score || 0), 1);
    document.getElementById('lookupResults').innerHTML = hits.map(h => {
      const rel = Math.round((h.score || 0) / maxS * 100);
      return `
      <div class="lookup-item" onclick="lookupJump('${h.file}','${q.replace(/'/g, '')}','${(h.anchor||'').replace(/'/g, '')}')">
        <div class="lk-file">${h.file.replace(/\.md$/, '')} <span class="muted">${h.chapter}</span>
          <span class="lk-rel${rel < 45 ? ' low' : ''}" title="关联度">${rel}%</span></div>
        <div class="lk-ex">${h.excerpt}</div>
      </div>`;
    }).join('') || '<p class="muted">无匹配</p>';
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

// ================= 考点图谱（含标签分级：一二常显，放大显三级） =================
let graphDrawn = false, graphDataCache = null, chapterSrcByCh = {};
const LEVEL_COLOR = { '必考': '#e8590c', '常考': '#3b5bdb', '了解': '#868e96' };

async function drawGraph() {
  const graphData = await api('/api/graph');
  graphDataCache = graphData;
  const chart = echarts.init(document.getElementById('graphChart'));
  const trunc = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s;
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
        <p>权重：<b>${d.weight}</b> · ${d.kp}（${d.chapter}）</p>`;
    }
  });
  graphDrawn = true;
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

function openChapterDoc(ch) {
  const file = chapterSrcByCh[ch]
    || vaultPages.find(p => p.chapter === ch && p.type === '知识点页')?.file
    || vaultPages.find(p => p.chapter === ch)?.file;
  if (file) openPage(file);
  else toast('未找到该章文档');
}

// ================= Smart Connections（关联度：散点地图 + 分数列表） =================
let relList = [];

async function loadRelated(file) {
  let list = [];
  try {
    list = await api('/api/wiki/related?name=' + encodeURIComponent(file) + '&k=8');
  } catch (e) { }
  relList = list;
  renderConnMap(file, list);
  document.getElementById('relatedList').innerHTML = list.length ? list.map((r, i) => `
    <div class="related-item" id="rel-${i}">
      <div class="rel-head" onclick="toggleRel(${i})">
        <div><span class="r-score">${(r.score ?? 0).toFixed(2)}</span>
          <span class="r-file">${r.file.replace(/\.md$/, '').split('/').pop()}</span>
          <span class="rel-caret" id="rel-caret-${i}">▸</span></div>
        <div class="r-meta">${r.chapter}${(r.kp_overlap || []).length ? ' · 共同: ' + r.kp_overlap.join('/') : ''}
          <a class="rel-open" onclick="event.stopPropagation();openPage('${r.file}')">打开 →</a></div>
        <div class="r-bar"><i style="width:${Math.min((r.score ?? 0) * 100, 100).toFixed(0)}%"></i></div>
      </div>
      <div class="rel-body" id="rel-body-${i}" style="display:none"></div>
    </div>`).join('') : '<p class="muted">暂无关联</p>';
}

// 展开/收起关联文档内容预览（图谱节点点击 → 强制展开并滚动到该条）
async function toggleRel(i, forceOpen = false) {
  const body = document.getElementById('rel-body-' + i);
  const caret = document.getElementById('rel-caret-' + i);
  if (!body) return;
  const open = forceOpen || body.style.display === 'none';
  if (open && !body.dataset.loaded) {
    body.innerHTML = '<p class="muted">加载中…</p>';
    try {
      const page = await api('/api/wiki/page?name=' + encodeURIComponent(relList[i].file));
      const raw = (page.body || '').slice(0, 1600);
      body.innerHTML = '<div class="rel-content">' + renderMD(raw) +
        ((page.body || '').length > 1600 ? '<p class="muted">…（已截断，点"打开"看全文）</p>' : '') + '</div>';
      body.dataset.loaded = '1';
      renderChatMathSoon();
    } catch (e) {
      body.innerHTML = '<p class="muted">预览失败：' + e.message + '</p>';
    }
  }
  body.style.display = open ? 'block' : 'none';
  if (caret) caret.textContent = open ? '▾' : '▸';
  if (open) body.parentElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
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
    tooltip: { formatter: p => p.data.file ? '关联度 ' + ((p.data.value ?? 0).toFixed?.(2) || '') + '<br/>' + p.name + '<br/>点击展开下方内容' : '当前文档：' + me },
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
  chart.on('click', p => {
    if (typeof p.data.idx === 'number') toggleRel(p.data.idx, true);
    else if (p.data.file) openPage(p.data.file);
  });
}

// ================= 编辑 / 勘误 =================
function editCurrent() {
  openView('edit');
  document.getElementById('editTarget').textContent = currentFile || '未选择';
  api('/api/wiki/page?name=' + encodeURIComponent(currentFile)).then(p => {
    document.getElementById('editorArea').value = p.body;
    document.getElementById('errFile').value = currentFile;
    document.getElementById('errBefore').value = '';
    document.getElementById('errAfter').value = '';
  });
}

async function savePage() {
  await post('/api/teacher/page/save', {
    name: currentFile, body: document.getElementById('editorArea').value,
  });
  toast('已保存：' + currentFile);
  openPage(currentFile, false);
}

function submitErrataAsEdit() { savePage(); }

async function submitErrata() {
  await post('/api/teacher/errata', {
    file: document.getElementById('errFile').value,
    kind: document.getElementById('errKind').value,
    before: document.getElementById('errBefore').value,
    after: document.getElementById('errAfter').value,
    note: document.getElementById('errNote').value,
  });
  toast('勘误单已提交');
  loadErrata();
}

async function loadErrata() {
  const list = await api('/api/teacher/errata');
  document.getElementById('errataList').innerHTML = list.length ? `
    <table class="plain">
      <tr><th>#</th><th>文档</th><th>类型</th><th>说明</th><th>状态</th><th>操作</th></tr>
      ${list.map(e => `<tr>
        <td>${e.id}</td><td>${e.file}</td><td>${e.kind}</td>
        <td>${(e.note || '').slice(0, 40)}</td><td>${e.status}</td>
        <td>${e.status === '待确认' ? `<button class="ghost" onclick="applyErrata(${e.id})">应用</button>` : ''}</td>
      </tr>`).join('')}
    </table>` : '<p class="muted">暂无勘误记录</p>';
}

async function applyErrata(id) {
  await post('/api/teacher/errata/apply?id=' + id);
  toast('已应用到知识库');
  loadErrata();
}

// ================= 知识库状态 =================
async function loadStatus() {
  const s = await api('/api/teacher/kb-status');
  const cov = (s.sources.coverage * 100).toFixed(0);
  document.getElementById('statusArea').innerHTML = `
    <div class="status-cards">
      <div class="status-card">
        <div class="n">Indexed sources</div>
        <div class="v">${s.sources.total}</div>
        <div class="s">知识库文档（含 frontmatter ${s.sources.with_frontmatter}）</div>
        <div class="cov-bar"><i style="width:${cov}%"></i></div>
        <div class="s">${cov}% 元数据覆盖</div>
      </div>
      <div class="status-card">
        <div class="n">Exam points</div>
        <div class="v">${s.graph.exam_points}</div>
        <div class="s">考点 · 图谱节点 ${s.graph.nodes} / 边 ${s.graph.links}</div>
      </div>
      <div class="status-card">
        <div class="n">Levels</div>
        <div class="v" style="font-size:17px;line-height:1.7">
          必考 ${s.graph.levels['必考'] || 0} · 常考 ${s.graph.levels['常考'] || 0} · 了解 ${s.graph.levels['了解'] || 0}
        </div>
        <div class="s">考点分级分布 · 总权重 ${s.graph.total_weight}</div>
      </div>
      <div class="status-card">
        <div class="n">Vector memory</div>
        <div class="v">${s.sources.total_chars.toLocaleString()}</div>
        <div class="s">字符总量 · 本地向量索引（bigram embedding）</div>
      </div>
      <div class="status-card">
        <div class="n">题库 / 作业</div>
        <div class="v">${s.banks.questions} 题</div>
        <div class="s">作业 ${s.banks.homework} · 勘误 ${s.banks.errata} · 浏览 ${s.banks.page_views} 次</div>
      </div>
      <div class="status-card">
        <div class="n">Collections</div>
        <div class="v" style="font-size:15px;line-height:1.8">
          ${Object.entries(s.types).map(([t, n]) => `${t} ${n}`).join(' · ')}
        </div>
        <div class="s">按页型分布</div>
      </div>
    </div>
    <div class="row" style="margin-top:18px">
      <button class="primary" onclick="rebuildGraph()">🔄 更新知识库（重建考点图谱）</button>
      <span class="muted">知识库 md 修改后点击刷新图谱数据</span>
    </div>`;
}

async function rebuildGraph() {
  const r = await post('/api/teacher/kb/rebuild', {});
  toast(r.ok ? '图谱已重建' : '重建失败');
  loadStatus();
}

// ================= 出题 =================
async function loadQuestions() {
  const qs = await api('/api/teacher/questions');
  document.getElementById('qCount').textContent = qs.length;
  document.getElementById('qList').innerHTML = `
    <table class="plain">
      <tr><th>id</th><th>类型</th><th>知识点</th><th>题干</th><th>出处</th></tr>
      ${qs.slice(-15).reverse().map(q => `<tr>
        <td>${q.id}</td><td>${q.type}</td><td>${q.kp}</td>
        <td>${q.q.slice(0, 50)}</td><td>${q.source}</td></tr>`).join('')}
    </table>`;
}

async function submitQuestion() {
  const opts = document.getElementById('qOptions').value.split('\n').map(s => s.trim()).filter(Boolean);
  await post('/api/teacher/question', {
    type: document.getElementById('qType').value,
    kp: document.getElementById('qKp').value,
    qtype: document.getElementById('qQtype').value,
    q: document.getElementById('qText').value,
    options: opts,
    answer: parseInt(document.getElementById('qAnswer').value) || 0,
    source: document.getElementById('qSource').value || '教师出题',
  });
  toast('已入题库，学生端立即可用');
  loadQuestions();
}

// ================= 作业 =================
async function loadHomework() {
  const list = await api('/api/teacher/homework');
  document.getElementById('hwList').innerHTML = list.length ? `
    <table class="plain">
      <tr><th>#</th><th>标题</th><th>知识点</th><th>截止</th><th>发布人</th></tr>
      ${list.map(h => `<tr><td>${h.id}</td><td>${h.title}</td><td>${h.kp}</td>
        <td>${h.due_date}</td><td>${h.teacher}</td></tr>`).join('')}
    </table>` : '<p class="muted">暂无作业</p>';
}

async function submitHomework() {
  await post('/api/teacher/homework', {
    title: document.getElementById('hwTitle').value,
    detail: document.getElementById('hwDetail').value,
    kp: document.getElementById('hwKp').value,
    question_ids: '',
    due_date: document.getElementById('hwDue').value,
  });
  toast('作业已发布，学生端可见');
  loadHomework();
}

// ================= 浏览热力图 =================
async function loadHeat() {
  const h = await api('/api/teacher/view-heatmap');
  const chart = echarts.init(document.getElementById('heatChart'));
  const rows = h.by_file.slice(0, 20);
  if (!rows.length) {
    chart.setOption({ title: { text: '暂无浏览数据（学生端打开文档后产生）', left: 'center', top: 'middle', textStyle: { color: '#999', fontSize: 15 } } });
    document.getElementById('heatCards').innerHTML = '';
    return;
  }
  const max = Math.max(...rows.map(r => r.n), 1);
  chart.setOption({
    tooltip: {},
    grid: { left: 230, right: 50, top: 10, bottom: 30 },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: rows.map(r => r.file.replace(/\.md$/, '')).reverse() },
    series: [{
      type: 'bar', barWidth: 15,
      data: rows.map(r => ({
        value: r.n,
        itemStyle: { color: r.n / max > 0.6 ? '#e8590c' : r.n / max > 0.3 ? '#f59f00' : '#3b5bdb' },
      })).reverse(),
      label: { show: true, position: 'right' },
    }],
  });
  document.getElementById('heatCards').innerHTML = `
    <div class="card"><h3>最热文档</h3><div class="num">${rows[0].n}</div>
      <p class="muted">${rows[0].file.replace(/\.md$/, '')}</p></div>
    <div class="card"><h3>活跃学生</h3><div class="num">${h.by_user.length}</div>
      <p class="muted">${h.by_user.slice(0, 3).map(u => u.user_name).join('、') || '-'}</p></div>
    <div class="card"><h3>总浏览</h3><div class="num">${h.by_file.reduce((s, r) => s + r.n, 0)}</div>
      <p class="muted">页面浏览次数</p></div>`;
}

// ================= 班级学情 =================
async function loadKlass() {
  const heat = await api('/api/teacher/heatmap');
  const chart = echarts.init(document.getElementById('klassChart'));
  const rows = heat.kp_accuracy.slice().sort((a, b) => a.accuracy - b.accuracy);
  if (!rows.length) {
    chart.setOption({ title: { text: '暂无答题数据', left: 'center', top: 'middle', textStyle: { color: '#999', fontSize: 15 } } });
  } else {
    chart.setOption({
      tooltip: { formatter: p => `${p.name}<br/>正确率：${(p.value * 100).toFixed(0)}%` },
      grid: { left: 160, right: 60, top: 20, bottom: 30 },
      xAxis: { type: 'value', min: 0, max: 1, axisLabel: { formatter: v => (v * 100) + '%' } },
      yAxis: { type: 'category', data: rows.map(r => r.kp), axisLabel: { fontSize: 12 } },
      series: [{
        type: 'bar', barWidth: 16,
        data: rows.map(r => ({
          value: r.accuracy,
          itemStyle: { color: r.accuracy < 0.5 ? '#e03131' : r.accuracy < 0.75 ? '#f59f00' : '#2f9e44' },
        })),
        label: { show: true, position: 'right', formatter: p => (p.value * 100).toFixed(0) + '%' },
      }],
    });
  }
  document.getElementById('hotList').innerHTML = heat.hot_wrong.length
    ? heat.hot_wrong.map((h, i) => `
      <div class="card"><h3>#${i + 1} ${h.question_id}</h3>
        <p><span class="tag must">${h.kp}</span></p>
        <div class="num" style="color:${h.wrong_n >= 3 ? 'var(--bad)' : 'var(--must)'}">${h.wrong_n} 人答错</div>
        <p class="muted">建议课堂讲评</p></div>`).join('')
    : '<p class="muted">暂无错题记录。</p>';
  const graph = await api('/api/graph');
  const lvColor = { '必考': '#e8590c', '常考': '#3b5bdb', '了解': '#868e96' };
  const chapters = graph.nodes.filter(n => n.type === 'chapter');
  const kps = graph.nodes.filter(n => n.type === 'knowledge_point');
  const eps = graph.nodes.filter(n => n.type === 'exam_point');
  let html = '';
  chapters.forEach(ch => {
    const chKps = kps.filter(k => k.chapter === ch.name);
    if (!chKps.length) return;
    html += `<div class="weak-item"><b>${ch.name}</b>${chKps.map(k => {
      const kEps = eps.filter(e => e.kp === k.name && e.chapter === ch.name);
      return `<div style="margin:10px 0 0 14px"><b style="font-size:14px">${k.name}</b>
        <span class="muted">（权重 ${k.weight}）</span>
        ${kEps.map(e => `<div style="margin:6px 0 0 14px">
          <span class="cause-chip" style="border-color:${lvColor[e.level]};color:${lvColor[e.level]}">${e.level}</span>
          ${e.name} <span class="muted">· ${e.qtype || ''} · ${e.weight}</span></div>`).join('')}
      </div>`;
    }).join('')}</div>`;
  });
  document.getElementById('weightTable').innerHTML = html;
}

// ================= TeleAgent 助教（教师模式） =================
function pushMsg(cls, html) {
  const log = document.getElementById('chatLog');
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  div.innerHTML = html;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
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

// ---------- / 命令面板（Claudian 式） ----------
function onChatInput(val) {
  updateCtxStats();
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
      const hit = skillCatalog.find(s => items[cur]?.innerHTML.includes('/' + s.name));
      if (hit) pickSkill(hit.name);
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
  pushMsg('user', `▶ <b>${label}</b>${params.req ? '<br>' + params.req : ''}`);
  const thinking = pushMsg('bot',
    `<span class="ta-tag">TeleAgent · ${label}</span><br>🧠 模型思考中…<br>
     <span class="src">约束规则：${(s ? s.rules : []).join(' ✓ ')}</span>`);
  try {
    const r = await post('/api/skills/run', {
      skill: name, params,
      effort: (document.getElementById('effortSel') || {}).value || 'high',
      kb_write: (document.getElementById('kbWrite') || {}).checked !== false,
    });
    thinking.innerHTML = `<span class="ta-tag">TeleAgent · ${r.label || ''}</span><br>
      <div class="md-out">${renderMD(r.output || '')}</div>
      ${r.record_file ? `<div class="card-mini">📄 <a class="wikilink" onclick="openPage('${r.record_file}')">打开知识库记录 →</a></div>` : ''}
      <span class="src">✅ 规则检查通过：${(r.rules || []).join(' ✓ ')}</span>`;
    if (r.record_file) refreshTree();
    updateCtxStats();
  } catch (e) {
    thinking.innerHTML = `<span class="ta-tag">TeleAgent</span><br>❌ ${e.message}`;
  }
  log.scrollTop = log.scrollHeight;
}

// 多轮对话历史（随 /api/agent/chat 一起发模型，跨会话各自维护）
let chatHistory = [];
// 多模态附件（file_id 列表）
let attachments = [];

function onAttach(inp) {
  [...inp.files].forEach(f => uploadAttach(f));
  inp.value = '';
}
async function uploadAttach(file) {
  const fd = new FormData();
  fd.append('file', file);
  try {
    const r = await fetch('/api/upload', {
      method: 'POST',
      headers: { 'X-Token': TOKEN, 'X-Course-Id': COURSE_ID },
      body: fd,
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || '上传失败');
    attachments.push({ id: data.file_id, name: data.name });
    renderAttach();
    toast('📎 已附加 ' + data.name);
  } catch (e) {
    toast('附件上传失败：' + e.message);
  }
}
function renderAttach() {
  const box = document.getElementById('attachChips');
  if (!box) return;
  box.innerHTML = attachments.map((a, i) =>
    `<span class="attach-chip">📎 ${a.name}<button onclick="removeAttach(${i})">×</button></span>`).join('');
}
function removeAttach(i) { attachments.splice(i, 1); renderAttach(); }

// 拖拽 & 粘贴上传（composer 区域）
(function initAttachDnD() {
  const zone = document.querySelector('.assist');
  if (!zone) return;
  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });
  zone.addEventListener('dragleave', e => {
    if (!e.relatedTarget || !zone.contains(e.relatedTarget)) zone.classList.remove('drag-over');
  });
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const fs = [...(e.dataTransfer && e.dataTransfer.files || [])];
    if (fs.length) fs.forEach(uploadAttach);
  });
  document.addEventListener('paste', e => {
    const fs = [...(e.clipboardData && e.clipboardData.files || [])];
    if (fs.length) {
      e.preventDefault();
      fs.forEach(uploadAttach);
    }
  });
})();


async function ask() {
  const input = document.getElementById('chatQ');
  let q = input.value.trim();
  if (q.startsWith('/')) {
    const m = q.match(/^\/(\S+)\s*([\s\S]*)$/);
    const hit = m && skillCatalog.find(s => s.name === m[1]);
    if (hit) {
      input.value = '';
      runSkill(hit.name, { req: (m[2] || '').trim() });
      return;
    }
  }
  if (!q && !quotedText && !attachments.length) return;
  // 选中引用作为上下文随问题一起输入模型
  if (quotedText) {
    q = (q ? q + '\n\n' : '') + '【我选中的资料片段】\n' + quotedText;
    clearQuote();
  }
  if (!q) q = '📎 ' + attachments.map(a => a.name).join('、');
  input.value = '';
  const greet = document.querySelector('.greet');
  if (greet) greet.remove();
  const sendHistory = chatHistory.slice(-10);
  pushMsg('user', q);
  chatHistory.push({ role: 'user', content: q.slice(0, 600) });
  const thinking = pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>🧠 模型思考中…（检索知识库）`);
  try {
    const r = await post('/api/agent/chat', {
      message: q, student_id: 0,
      history: sendHistory,
      attachments: attachments.map(a => a.id),
    });
    attachments = [];
    renderAttach();
    chatHistory.push({ role: 'assistant', content: (r.answer || '').replace(/<[^>]+>/g, ' ').slice(0, 600) });
    updateCtxStats();
    const srcs = (r.sources || []).map(s =>
      `${s.file || s.document_name || ''}${s.chapter ? '（' + s.chapter + '）' : ''}`).join('；');
    const traceHtml = (r.trace && r.trace.length)
      ? `<details class="trace-box"><summary>🔧 执行轨迹（${r.trace.length} 次工具调用）</summary>${
          r.trace.map(t => `<div class="trace-line">${t.ok ? '✅' : '❌'} <b>${t.tool}</b> <span class="muted">${
            String(JSON.stringify(t.args || {})).slice(0, 90)}</span></div>`).join('')}</details>`
      : '';
    thinking.innerHTML = `<span class="ta-tag">TeleAgent</span><br><div class="md-out">${renderMD(r.answer || '')}</div>
      ${traceHtml}
      ${srcs ? `<span class="src">📎 资料出处：${srcs}</span>` : ''}`;
  } catch (e) {
    thinking.innerHTML = `<span class="ta-tag">TeleAgent</span><br>出错了：${e.message}`;
  }
}

function runTool(name) {
  openView(name);
  const greet = document.querySelector('.greet');
  if (greet) greet.remove();
  const tips = {
    edit: '已打开编辑/勘误。也可以直接对我说「/errata」由我自动处理。',
    status: '知识库状态面板已刷新。改完知识库记得点「更新知识库」重建考点图谱。',
    question: '出题面板已就绪。也可以直接输入 /question 出 3 道 LL(1) 的题。',
    homework: '作业面板已就绪。也可以直接输入 /homework 布置作业。',
    heat: '浏览热力图已加载。看看哪些资料学生最常翻。',
  };
  pushMsg('bot', `<span class="ta-tag">TeleAgent</span><br>${tips[name] || ''}`);
}

// ================= 启动 =================
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

loadCourseBar().finally(() => loadVault());
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
    COURSE_NAME = (courses.find(c => c.id === COURSE_ID) || {}).name || '';
    applyCourseLabels();
  } catch (e) { }
}

// 课程名相关界面文案（切课后不残留旧课程名）
function applyCourseLabels() {
  const n = COURSE_NAME || '知识库';
  const kb = document.getElementById('kbTitle');
  if (kb) kb.textContent = n + '知识库';
  const h1 = document.getElementById('pageTitle');
  if (h1) h1.textContent = '教师端 · ' + n + '考点地图';
  document.title = n + '考点地图 · 教师端';
  const oh = document.querySelector('.onboard-hi');
  if (oh) oh.textContent = 'TELEAGENT · ' + n + '考点地图';
}


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
    const hits = await api('/api/wiki/search?q=' + encodeURIComponent(q) + '&k=12');
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
    const maxS = Math.max(...srHits.map(x => x.score || 0), 1);
    const rel = Math.round((h.score || 0) / maxS * 100);
    return `<div class="sr-item ${i === 0 ? 'sel' : ''}" data-i="${i}" onclick="pickSearch(${i})">
      <div class="sr-head">
        <span class="sr-name">${h.file.replace(/\.md$/, '').split('/').pop()}</span>
        <span class="sr-rel${rel < 45 ? ' low' : ''}" title="关联度">${rel}%</span>
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


// ===== 上下文占用（Claudian 式：环形 + tokens + 明细弹层） =====
function ctxBreakdown() {
  const chip = document.getElementById('ctxChip');
  const file = (chip && chip.dataset.file) || '';
  let quote = '';
  try { quote = quotedText || ''; } catch (e) { }
  const q = (document.getElementById('chatQ') || {}).value || '';
  const tok = c => Math.round(c / 2);
  return [
    ['对话历史', tok(chatHistory.reduce((n, m) => n + (m.content || '').length, 0))],
    ['当前输入/引用', tok(q.length + quote.length)],
    ['附件解析', (typeof attachments !== 'undefined' ? attachments.length : 0) * 800],
    ['关联文档', file ? 750 : 0],
    ['系统与记忆', 1200],
  ];
}
function renderCtxPop(rows, used, pctStr) {
  const pop = document.getElementById('ctxPop');
  if (!pop) return;
  const free = Math.max(128000 - used, 0);
  const fmt = v => v >= 1000 ? (v / 1000).toFixed(1) + 'k' : String(v);
  pop.innerHTML = `<div class="ctx-pop-head">上下文窗口 <b>${fmt(used)} / 128k（${pctStr}%）</b></div>
    <div class="ctx-bar"><i style="width:${pctStr}%"></i></div>
    ${rows.map(([n, v]) => `<div class="ctx-row"><span>${n}</span><b>${fmt(v)}</b></div>`).join('')}
    <div class="ctx-row"><span>剩余空间</span><b>${fmt(free)}</b></div>`;
}
function updateCtxStats() {
  const el = document.getElementById('ctxStats');
  if (!el) return;
  const rows = ctxBreakdown();
  const used = rows.reduce((n, r) => n + r[1], 0);
  const pct = Math.min(used / 128000 * 100, 100);
  const pctStr = pct < 10 ? pct.toFixed(1) : String(Math.round(pct));
  const r = 6, c = 2 * Math.PI * r;
  const off = c * (1 - pct / 100);
  const fmt = v => v >= 1000 ? (v / 1000).toFixed(1) + 'k' : String(v);
  el.innerHTML = `<svg width="15" height="15" viewBox="0 0 16 16" aria-hidden="true">
      <circle cx="8" cy="8" r="${r}" fill="none" stroke="var(--line)" stroke-width="2.2"></circle>
      <circle cx="8" cy="8" r="${r}" fill="none" stroke="#d97757" stroke-width="2.2"
        stroke-linecap="round" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${off.toFixed(1)}"
        transform="rotate(-90 8 8)"></circle>
    </svg><span class="ctx-tokens">${fmt(used)} / 128k</span>`;
  el.title = 'Context usage';
  const pop = document.getElementById('ctxPop');
  if (pop && pop.classList.contains('show')) renderCtxPop(rows, used, pctStr);
}
function toggleCtxPop() {
  const pop = document.getElementById('ctxPop');
  if (!pop) return;
  if (pop.classList.toggle('show')) updateCtxStats();
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
  sessions = sessions.map(s => ({ pinned: false, archived: false, msgs: [], ...s }));
  if (!sessions.length) newSession(true);
}
function saveSessions() {
  // 置顶会话永不被截断
  const pinned = sessions.filter(s => s.pinned);
  const rest = sessions.filter(s => !s.pinned).slice(-30);
  try { localStorage.setItem(SESS_KEY, JSON.stringify(pinned.concat(rest))); } catch (e) { }
}
function newSession(silent) {
  sessions.push({ id: Date.now(), title: '新会话', time: new Date().toLocaleString('zh-CN', { hour12: false }), msgs: [], pinned: false, archived: false });
  curSess = sessions.length - 1;
  chatHistory = [];
  saveSessions();
  if (!silent) {
    const log = document.getElementById('chatLog');
    if (log) log.innerHTML = '<div class="greet"><div class="greet-title">TeleAgent</div><div class="greet-sub">Good day</div><div class="linked-chip" id="linkedChip">\u{1F517} Linked content: \u77e5\u8bc6\u5e93</div></div>';
    renderSessions();
    zenUpdate('\u65b0\u4f1a\u8bdd\u5df2\u521b\u5efa');
  }
}
function switchSession(i) {
  curSess = i;
  const log = document.getElementById('chatLog');
  const s = sessions[i];
  if (!log || !s) return;
  chatHistory = s.msgs.map(m => ({
    role: m.cls === 'user' ? 'user' : 'assistant',
    content: String(m.html || '').replace(/<[^>]+>/g, ' ').slice(0, 600),
  })).filter(m => m.content.trim());
  log.innerHTML = s.msgs.map(m => '<div class="msg ' + m.cls + '">' + m.html + '</div>').join('')
    || '<div class="greet"><div class="greet-title">TeleAgent</div><div class="greet-sub">Good day</div><div class="linked-chip" id="linkedChip">\u{1F517} Linked content: \u77e5\u8bc6\u5e93</div></div>';
  renderSessions();
  updateCtxStats();
}

// ---- 会话面板（Claudian 式：New/Search/Archive + PINNED + 置顶/归档/删除） ----
let sessView = 'active';        // active | archived
let sessSearchOpen = false;
let sessFilter = '';

function renderSessions() {
  const pop = document.getElementById('sessionsPop');
  if (!pop) return;
  const f = sessFilter.toLowerCase();
  const match = s => !f || (s.title || '').toLowerCase().includes(f);
  const archived = sessions.filter(s => s.archived && match(s));
  const active = sessions.filter(s => !s.archived && match(s));
  const pinned = active.filter(s => s.pinned);
  const normal = active.filter(s => !s.pinned);
  const item = s => {
    const i = sessions.indexOf(s);
    return `<div class="sess-item ${i === curSess ? 'sel' : ''}" onclick="switchSession(${i})">
      <span class="t">${s.title}</span>
      <span class="sess-acts">
        <button class="sess-act" title="${s.pinned ? 'Unpin' : 'Pin'}" onclick="event.stopPropagation();pinSession(${i})">${s.pinned ? '\u{1F4CC}' : '\u{1F4CD}'}</button>
        <button class="sess-act" title="${s.archived ? '\u53d6\u6d88\u5f52\u6863' : 'Archive'}" onclick="event.stopPropagation();archiveSession(${i})">${s.archived ? '\u{1F4E4}' : '\u{1F4E5}'}</button>
        <button class="sess-act" title="\u5220\u9664" onclick="event.stopPropagation();delSession(${i})">\u{1F5D1}</button>
      </span>
    </div>`;
  };
  const searchBox = sessSearchOpen
    ? `<input class="sess-search" placeholder="\u641c\u7d22\u4f1a\u8bdd\u2026" value="${sessFilter}"
        oninput="sessFilter=this.value;renderSessions()">` : '';
  const toolbar = `<div class="sess-bar">
      <button class="sess-new" onclick="newSession()">\uFF0B \u65b0\u4f1a\u8bdd</button>
      <button class="sess-tool" title="\u641c\u7d22" onclick="sessSearchOpen=!sessSearchOpen;renderSessions()">\u{1F50D}</button>
      <button class="sess-tool" title="\u5f52\u6863" onclick="sessView=sessView==='archived'?'active':'archived';renderSessions()">${sessView === 'archived' ? '\u2190 \u8fd4\u56de' : '\u{1F5C3} \u5f52\u6863'}</button>
    </div>${searchBox}`;
  if (sessView === 'archived') {
    pop.innerHTML = toolbar + (archived.length
      ? '<div class="sess-label">ARCHIVED</div>' + archived.map(item).join('')
      : '<p class="muted" style="padding:8px">\u{1F5C3} \u5f52\u6863\u533a\u4e3a\u7a7a</p>');
    return;
  }
  pop.innerHTML = toolbar +
    (pinned.length ? '<div class="sess-label">PINNED</div>' + pinned.map(item).join('') : '') +
    '<div class="sess-label">SESSIONS</div>' +
    (normal.length ? normal.map(item).join('') : '<p class="muted" style="padding:8px">\u6682\u65e0\u4f1a\u8bdd</p>');
}
function toggleSessions() {
  const pop = document.getElementById('sessionsPop');
  if (pop) pop.classList.toggle('show');
}
function pinSession(i) {
  if (!sessions[i]) return;
  sessions[i].pinned = !sessions[i].pinned;
  saveSessions(); renderSessions();
}
function archiveSession(i) {
  if (!sessions[i]) return;
  sessions[i].archived = !sessions[i].archived;
  if (sessions[i].archived && i === curSess) {
    const next = sessions.findIndex((s, j) => j !== i && !s.archived);
    if (next >= 0) switchSession(next); else newSession();
  }
  saveSessions(); renderSessions();
}
function delSession(i) {
  if (!sessions[i]) return;
  if (!confirm('\u786e\u8ba4\u5220\u9664\u4f1a\u8bdd\u300c' + sessions[i].title + '\u300d\uff1f')) return;
  sessions.splice(i, 1);
  if (!sessions.length) { newSession(); return; }
  if (i === curSess) switchSession(Math.min(curSess, sessions.length - 1));
  else { if (i < curSess) curSess--; saveSessions(); renderSessions(); }
}

// ---- 会话记录：DOM 同步（消息渲染完成后再捕获，修复历史不加载） ----
let _sessSyncT = null;
function sessSync() {
  if (!sessions.length) loadSessions();
  const s = sessions[curSess];
  const log = document.getElementById('chatLog');
  if (!s || !log) return;
  const divs = [...log.querySelectorAll(':scope > .msg')];
  if (!divs.length) return;
  s.msgs = divs.map(d => ({ cls: d.classList.contains('user') ? 'user' : 'bot', html: d.innerHTML }));
  if (s.title === '\u65b0\u4f1a\u8bdd') {
    const u = divs.find(d => d.classList.contains('user'));
    if (u) s.title = u.textContent.trim().slice(0, 18) || s.title;
  }
  s.time = new Date().toLocaleString('zh-CN', { hour12: false });
  saveSessions();
}

// ===== Markdown+数学 渲染（Claudian 式：公式先抽保护区，防 marked 吃反斜杠/下划线） =====
function renderMD(text) {
  const slots = [];
  const stash = m => { slots.push(m); return '\uE000' + (slots.length - 1) + '\uE001'; };
  let t = String(text || '');
  t = t.replace(/\$\$[\s\S]+?\$\$/g, stash);
  t = t.replace(/\\\[[\s\S]+?\\\]/g, stash);
  t = t.replace(/\\\([\s\S]+?\\\)/g, stash);
  t = t.replace(/\$[^$\n]+?\$/g, stash);
  let html;
  try { html = marked.parse(t); } catch (e) { html = t; }
  html = html.replace(/\uE000(\d+)\uE001/g, (_, i) => {
    let m = slots[+i];
    if (m.startsWith('\\[')) m = '$$' + m.slice(2, -2) + '$$';
    else if (m[0] === '$' && m[1] !== '$') m = '\\(' + m.slice(1, -1) + '\\)';
    return m;
  });
  return html;
}

// ===== 聊天/预览区 LaTeX 渲染（KaTeX，修公式裸显） =====
let _mathT = null;
function renderChatMath() {
  if (typeof renderMathInElement !== 'function') return;
  for (const id of ['chatLog', 'relatedList', 'mainScroll']) {
    const el = document.getElementById(id);
    if (!el) continue;
    try {
      renderMathInElement(el, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true },
        ],
        throwOnError: false,
      });
    } catch (e) { }
  }
}
function renderChatMathSoon() {
  clearTimeout(_mathT);
  _mathT = setTimeout(renderChatMath, 250);
}

function sessSyncSoon() {
  clearTimeout(_sessSyncT);
  _sessSyncT = setTimeout(sessSync, 300);
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
    updateCtxStats();
    const _log = document.getElementById('chatLog');
    if (_log && window.MutationObserver) {
      new MutationObserver(() => { sessSyncSoon(); renderChatMathSoon(); })
        .observe(_log, { childList: true, subtree: true });
    }
    const _main = document.getElementById('mainScroll');
    if (_main && window.MutationObserver) {
      new MutationObserver(renderChatMathSoon)
        .observe(_main, { childList: true, subtree: true });
    }
  }
}, 150);

// ================= 新手引导（首次进入 · ChatGPT 式欢迎卡） =================
function showOnboarding() {
  const log = document.getElementById('chatLog');
  if (!log) return;
  const acts = [
    ['✏️', '智能出题', 'agent 查库 + 学情命制新题', "pickSkill('question')"],
    ['📋', '布置作业', 'LLM 代拟 · 学生端立即可见', "pickSkill('homework')"],
    ['🎯', '班级学情', '正确率热力 · 薄弱讲评建议', "openView('klass')"],
    ['✅', '知识库体检', '覆盖率 / 图谱 / 题库一键体检', "runSkill('check', {})"],
    ['🗺', '考点地图', '三级图谱 · 权重可视化', "openView('graph')"],
    ['📝', '编辑 / 勘误', '直接改库或提交勘误单', "openView('edit')"],
  ];
  log.innerHTML = `<div class="onboard-wrap">
    <div class="onboard-hi">TELEAGENT · 编译原理考点地图</div>
    <div class="onboard-title">你好，${MYNAME} 👋</div>
    <div class="onboard-sub">我是课程教学智能体。出题、作业、学情，都可以从这里开始——</div>
    <div class="onboard-grid">
      ${acts.map(([ic, t, d, fn]) => `
        <div class="onboard-item" onclick="${fn}">
          <div class="oi-ic">${ic}</div>
          <div><b>${t}</b><p>${d}</p></div>
        </div>`).join('')}
    </div>
    <div class="onboard-tip">
      <b>/</b> 唤起技能面板　<b>@文档名</b> 切换关联资料　<b>YOLO</b> 开关控制写库<br>
      技能产出自动入库「智能体记录」· 全程可追溯
    </div>
  </div>`;
}
if (!localStorage.getItem('ta_onboard_teacher')) {
  localStorage.setItem('ta_onboard_teacher', '1');
  showOnboarding();
}

// 模型芯片显示实际配置
api('/api/config/status').then(c => {
  const chip = document.getElementById('modelChip');
  if (chip) chip.textContent = c.llm_model + (c.llm_configured ? '' : '（未配Key）');
}).catch(() => { });


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
