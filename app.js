(() => {
  const GRID_SIZE = 12;
  const WORDS_PER_PUZZLE = 6;
  const ROUND_SECONDS = 30;
  const DIRECTIONS = [
    [0, 1], [1, 0], [1, 1], [-1, 1],
    [0, -1], [-1, 0], [-1, -1], [1, -1]
  ];
  const RING_CIRCUMFERENCE = 2 * Math.PI * 17;

  const $ = (id) => document.getElementById(id);
  const els = {
    prompt: $('prompt'),
    grid: $('grid'),
    timerText: $('timer-text'),
    timerRing: $('timer-progress'),
    timerWrap: document.querySelector('.timer'),
    foundCount: $('found-count'),
    sessionScore: $('session-score'),
    modal: $('modal'),
    modalIcon: $('modal-icon'),
    modalTitle: $('modal-title'),
    modalSub: $('modal-sub'),
    modalGrid: $('modal-grid'),
    nextBtn: $('next-btn')
  };

  let puzzle = null;
  let foundCount = 0;
  let sessionScore = 0;
  let rafId = 0;
  let timerEndsAt = 0;
  let timerRunning = false;
  let cellNodes = [];

  const ICONS = {
    trophy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4z"/><path d="M5 4H3v3a3 3 0 0 0 3 3M19 4h2v3a3 3 0 0 1-3 3"/></svg>',
    sad: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M16 16s-1.5-2-4-2-4 2-4 2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>'
  };

  // ---------------- Grid generation ----------------

  const rand = (n) => Math.floor(Math.random() * n);
  const shuffle = (arr) => {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = rand(i + 1);
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };

  function emptyGrid(n) {
    return Array.from({ length: n }, () => Array(n).fill(''));
  }

  function tryPlace(grid, word) {
    const n = grid.length;
    for (let attempt = 0; attempt < 80; attempt++) {
      const dir = DIRECTIONS[rand(DIRECTIONS.length)];
      const r0 = rand(n);
      const c0 = rand(n);
      const endR = r0 + dir[0] * (word.length - 1);
      const endC = c0 + dir[1] * (word.length - 1);
      if (endR < 0 || endR >= n || endC < 0 || endC >= n) continue;

      let ok = true;
      for (let i = 0; i < word.length; i++) {
        const ch = grid[r0 + dir[0] * i][c0 + dir[1] * i];
        if (ch !== '' && ch !== word[i]) { ok = false; break; }
      }
      if (!ok) continue;

      const cells = [];
      for (let i = 0; i < word.length; i++) {
        const r = r0 + dir[0] * i;
        const c = c0 + dir[1] * i;
        grid[r][c] = word[i];
        cells.push({ r, c });
      }
      return cells;
    }
    return null;
  }

  function buildPuzzle() {
    const category = CATEGORIES[rand(CATEGORIES.length)];
    const candidates = shuffle(category.pool).filter(w => w.length <= GRID_SIZE);
    const grid = emptyGrid(GRID_SIZE);
    const words = [];
    for (const w of candidates) {
      if (words.length >= WORDS_PER_PUZZLE) break;
      const cells = tryPlace(grid, w);
      if (cells) words.push({ text: w, cells });
    }
    if (words.length < WORDS_PER_PUZZLE) {
      // Extremely unlikely with current pools; retry once.
      return buildPuzzle();
    }
    // Fill empties with random letters
    for (let r = 0; r < GRID_SIZE; r++) {
      for (let c = 0; c < GRID_SIZE; c++) {
        if (grid[r][c] === '') {
          grid[r][c] = String.fromCharCode(65 + rand(26));
        }
      }
    }
    return { prompt: category.prompt, words, grid };
  }

  // ---------------- Render ----------------

  function renderGrid() {
    els.grid.style.setProperty('--cols', GRID_SIZE);
    els.grid.innerHTML = '';
    cellNodes = [];
    const frag = document.createDocumentFragment();
    for (let r = 0; r < GRID_SIZE; r++) {
      const row = [];
      for (let c = 0; c < GRID_SIZE; c++) {
        const el = document.createElement('div');
        el.className = 'cell';
        el.textContent = puzzle.grid[r][c];
        el.dataset.r = r;
        el.dataset.c = c;
        row.push(el);
        frag.appendChild(el);
      }
      cellNodes.push(row);
    }
    els.grid.appendChild(frag);
  }

  // ---------------- Selection ----------------

  let dragging = false;
  let startCell = null;
  let activeLine = [];

  function cellFromPoint(x, y) {
    const el = document.elementFromPoint(x, y);
    if (!el || !el.classList || !el.classList.contains('cell')) return null;
    if (el.classList.contains('found')) return null;
    return { r: +el.dataset.r, c: +el.dataset.c };
  }

  function snapLine(start, end) {
    // Returns list of {r,c} from start to nearest 8-axis line ending at or near end.
    const dr = end.r - start.r;
    const dc = end.c - start.c;
    if (dr === 0 && dc === 0) return [{ r: start.r, c: start.c }];

    // Determine principal direction by comparing |dr|, |dc|
    let stepR, stepC, length;
    const absDr = Math.abs(dr);
    const absDc = Math.abs(dc);
    if (absDr > absDc * 2) {
      // vertical
      stepR = Math.sign(dr); stepC = 0; length = absDr + 1;
    } else if (absDc > absDr * 2) {
      // horizontal
      stepR = 0; stepC = Math.sign(dc); length = absDc + 1;
    } else {
      // diagonal
      stepR = Math.sign(dr) || 1; stepC = Math.sign(dc) || 1;
      length = Math.max(absDr, absDc) + 1;
    }
    const cells = [];
    for (let i = 0; i < length; i++) {
      const r = start.r + stepR * i;
      const c = start.c + stepC * i;
      if (r < 0 || r >= GRID_SIZE || c < 0 || c >= GRID_SIZE) break;
      cells.push({ r, c });
    }
    return cells;
  }

  function clearDragHighlight() {
    for (const { r, c } of activeLine) {
      const el = cellNodes[r][c];
      if (!el.classList.contains('found')) el.classList.remove('dragging');
    }
    activeLine = [];
  }

  function applyDragHighlight(line) {
    clearDragHighlight();
    activeLine = line;
    for (const { r, c } of line) {
      const el = cellNodes[r][c];
      if (!el.classList.contains('found')) el.classList.add('dragging');
    }
  }

  function lettersOf(cells) {
    return cells.map(({ r, c }) => puzzle.grid[r][c]).join('');
  }

  function onPointerDown(e) {
    if (!timerRunning) return;
    const cell = cellFromPoint(e.clientX, e.clientY);
    if (!cell) return;
    dragging = true;
    startCell = cell;
    applyDragHighlight([cell]);
    els.grid.setPointerCapture && els.grid.setPointerCapture(e.pointerId);
    e.preventDefault();
  }

  function onPointerMove(e) {
    if (!dragging) return;
    const end = cellFromPoint(e.clientX, e.clientY);
    if (!end) return;
    const line = snapLine(startCell, end);
    applyDragHighlight(line);
  }

  function onPointerUp() {
    if (!dragging) return;
    dragging = false;
    const selectedCells = activeLine.slice();
    if (selectedCells.length < 2) {
      clearDragHighlight();
      return;
    }
    const forward = lettersOf(selectedCells);
    const backward = forward.split('').reverse().join('');
    const match = puzzle.words.find(w => !w.found && (w.text === forward || w.text === backward));
    if (match) {
      match.found = true;
      for (const { r, c } of selectedCells) {
        const el = cellNodes[r][c];
        el.classList.remove('dragging');
        el.classList.add('found');
      }
      activeLine = [];
      foundCount++;
      els.foundCount.textContent = foundCount;
      if (foundCount >= WORDS_PER_PUZZLE) onWin();
    } else {
      // Wrong: flash red on those cells
      const flashed = selectedCells.slice();
      for (const { r, c } of flashed) {
        const el = cellNodes[r][c];
        el.classList.remove('dragging');
        el.classList.add('wrong');
      }
      activeLine = [];
      setTimeout(() => {
        for (const { r, c } of flashed) {
          const el = cellNodes[r][c];
          if (!el.classList.contains('found')) el.classList.remove('wrong');
        }
      }, 420);
    }
  }

  function bindSelection() {
    els.grid.addEventListener('pointerdown', onPointerDown);
    els.grid.addEventListener('pointermove', onPointerMove);
    els.grid.addEventListener('pointerup', onPointerUp);
    els.grid.addEventListener('pointercancel', onPointerUp);
    els.grid.addEventListener('pointerleave', (e) => {
      // continue tracking via document if user drags out
    });
    document.addEventListener('pointerup', onPointerUp);
  }

  // ---------------- Timer ----------------

  function startTimer() {
    timerEndsAt = performance.now() + ROUND_SECONDS * 1000;
    timerRunning = true;
    cancelAnimationFrame(rafId);
    const tick = () => {
      const remainingMs = Math.max(0, timerEndsAt - performance.now());
      const remaining = remainingMs / 1000;
      els.timerText.textContent = Math.ceil(remaining);
      const frac = remaining / ROUND_SECONDS;
      els.timerRing.setAttribute('stroke-dashoffset', String(RING_CIRCUMFERENCE * (1 - frac)));
      els.timerWrap.classList.toggle('is-warn', remaining <= 15 && remaining > 7);
      els.timerWrap.classList.toggle('is-danger', remaining <= 7);
      if (remainingMs <= 0) {
        timerRunning = false;
        onTimeout();
        return;
      }
      rafId = requestAnimationFrame(tick);
    };
    rafId = requestAnimationFrame(tick);
  }

  function stopTimer() {
    timerRunning = false;
    cancelAnimationFrame(rafId);
  }

  // ---------------- Modals ----------------

  function showModal({ win }) {
    els.modal.hidden = false;
    els.modalIcon.classList.toggle('is-fail', !win);
    els.modalIcon.innerHTML = win ? ICONS.trophy : ICONS.sad;
    els.modalTitle.textContent = win ? 'Champion!' : 'Oopsie!';
    els.modalSub.textContent = win
      ? `You found all ${WORDS_PER_PUZZLE} in time.`
      : `You found ${foundCount} / ${WORDS_PER_PUZZLE}. Here are the answers:`;

    if (win) {
      els.modalGrid.hidden = true;
      els.modalGrid.innerHTML = '';
    } else {
      // Render mini-grid with all answers revealed
      els.modalGrid.hidden = false;
      els.modalGrid.style.setProperty('--cols', GRID_SIZE);
      els.modalGrid.innerHTML = '';
      const revealed = new Set();
      for (const w of puzzle.words) {
        for (const { r, c } of w.cells) revealed.add(r * GRID_SIZE + c);
      }
      const frag = document.createDocumentFragment();
      for (let r = 0; r < GRID_SIZE; r++) {
        for (let c = 0; c < GRID_SIZE; c++) {
          const el = document.createElement('div');
          el.className = 'mcell' + (revealed.has(r * GRID_SIZE + c) ? ' revealed' : '');
          el.textContent = puzzle.grid[r][c];
          frag.appendChild(el);
        }
      }
      els.modalGrid.appendChild(frag);
    }
  }

  function hideModal() {
    els.modal.hidden = true;
  }

  function onWin() {
    stopTimer();
    sessionScore++;
    els.sessionScore.textContent = sessionScore;
    showModal({ win: true });
  }

  function onTimeout() {
    showModal({ win: false });
  }

  // ---------------- Round lifecycle ----------------

  function newRound() {
    hideModal();
    foundCount = 0;
    els.foundCount.textContent = '0';
    puzzle = buildPuzzle();
    els.prompt.textContent = puzzle.prompt;
    renderGrid();
    // Reset ring instantly
    els.timerRing.setAttribute('stroke-dashoffset', '0');
    els.timerWrap.classList.remove('is-warn', 'is-danger');
    startTimer();
  }

  // ---------------- Init ----------------

  function init() {
    bindSelection();
    els.nextBtn.addEventListener('click', newRound);
    els.timerRing.setAttribute('stroke-dasharray', String(RING_CIRCUMFERENCE));
    newRound();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
