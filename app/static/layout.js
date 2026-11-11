// 可调节/可收起的三栏布局（学生端/教师端共用）
(function () {
  const layout = document.querySelector('.layout');
  if (!layout) return;
  const left = document.getElementById('sidebarLeft');
  const right = document.getElementById('sidebarRight');
  const spL = document.getElementById('splitLeft');
  const spR = document.getElementById('splitRight');

  // 恢复宽度偏好
  const lw = localStorage.getItem('ta_left_w');
  const rw = localStorage.getItem('ta_right_w');
  if (lw) layout.style.setProperty('--left-w', lw + 'px');
  if (rw) layout.style.setProperty('--right-w', rw + 'px');

  const isCollapsed = side => localStorage.getItem('ta_' + side + '_c') === '1';

  function applyCollapse(side) {
    const el = side === 'left' ? left : right;
    const sp = side === 'left' ? spL : spR;
    const collapsed = isCollapsed(side);
    el.classList.toggle('collapsed', collapsed);
    sp.classList.toggle('collapsed', collapsed);
    const grip = sp && sp.querySelector('.grip');
    if (grip) grip.textContent = side === 'left' ? (collapsed ? '»' : '«') : (collapsed ? '«' : '»');
    window.dispatchEvent(new Event('resize'));
  }

  window.toggleSidebar = function (side) {
    localStorage.setItem('ta_' + side + '_c', isCollapsed(side) ? '0' : '1');
    applyCollapse(side);
  };

  function dragify(splitter, side) {
    if (!splitter) return;
    const target = side === 'left' ? left : right;
    const varName = side === 'left' ? '--left-w' : '--right-w';
    splitter.addEventListener('mousedown', e => {
      if (e.target.classList.contains('grip')) return;
      const startX = e.clientX;
      const startW = target.getBoundingClientRect().width;
      splitter.classList.add('dragging');
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
      const move = ev => {
        const dx = ev.clientX - startX;
        const w = Math.min(Math.max(side === 'left' ? startW + dx : startW - dx, 160), 1000);
        layout.style.setProperty(varName, w + 'px');
      };
      const up = () => {
        document.removeEventListener('mousemove', move);
        document.removeEventListener('mouseup', up);
        splitter.classList.remove('dragging');
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        localStorage.setItem(side === 'left' ? 'ta_left_w' : 'ta_right_w',
          String(Math.round(target.getBoundingClientRect().width)));
        window.dispatchEvent(new Event('resize'));
      };
      document.addEventListener('mousemove', move);
      document.addEventListener('mouseup', up);
      e.preventDefault();
    });
    splitter.addEventListener('dblclick', () => window.toggleSidebar(side));
  }

  // grip 按钮（点击收起/展开）
  [spL, spR].forEach((sp, i) => {
    if (!sp) return;
    const grip = sp.querySelector('.grip');
    if (grip) grip.addEventListener('click', e => {
      e.stopPropagation();
      window.toggleSidebar(i === 0 ? 'left' : 'right');
    });
  });

  dragify(spL, 'left');
  dragify(spR, 'right');
  applyCollapse('left');
  applyCollapse('right');
})();
