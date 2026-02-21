'use strict';

// ═══════════════════════════════════════════════════════════════
//  State
// ═══════════════════════════════════════════════════════════════
let sessionId  = null;
let state      = null;   // last known game state from server
let busy       = false;  // true while an AI request is in flight
let cvcTimer   = null;   // setTimeout handle for CvC auto-play

// ═══════════════════════════════════════════════════════════════
//  Canvas drawing constants  (updated by initCanvas on each new game)
// ═══════════════════════════════════════════════════════════════
const GRID_SPAN = 520;   // CSS px for the full grid area
let margin   = 35;
let cellSize = 37;

// ═══════════════════════════════════════════════════════════════
//  DOM references
// ═══════════════════════════════════════════════════════════════
const canvas          = document.getElementById('board');
const ctx             = canvas.getContext('2d');
const statusDot       = document.getElementById('status-dot');
const statusText      = document.getElementById('status-text');
const thinkingOverlay = document.getElementById('thinking-overlay');
const btnNew          = document.getElementById('btn-new');
const btnRegret       = document.getElementById('btn-regret');
const selMode         = document.getElementById('sel-mode');
const selN            = document.getElementById('sel-n');
const selM            = document.getElementById('sel-m');
const selFirst        = document.getElementById('sel-first');
const selAI           = document.getElementById('sel-ai');
const rowFirst        = document.getElementById('row-first');
const rowAI           = document.getElementById('row-ai');

// ═══════════════════════════════════════════════════════════════
//  Initial UI visibility
// ═══════════════════════════════════════════════════════════════
function syncSettingsVisibility() {
  const mode = selMode.value;
  rowFirst.style.display = mode === 'hvc' ? '' : 'none';
  rowAI.style.display    = (mode === 'hvc' || mode === 'cvc') ? '' : 'none';
}
selMode.addEventListener('change', syncSettingsVisibility);
syncSettingsVisibility();

// ═══════════════════════════════════════════════════════════════
//  Event listeners
// ═══════════════════════════════════════════════════════════════
btnNew.addEventListener('click', startNewGame);
btnRegret.addEventListener('click', onRegret);
canvas.addEventListener('click', onCanvasClick);

// ═══════════════════════════════════════════════════════════════
//  API helpers
// ═══════════════════════════════════════════════════════════════
async function apiPost(url, body) {
  try {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return r.json();
  } catch (err) {
    console.error('Network error:', err);
    return { error: String(err) };
  }
}

// ═══════════════════════════════════════════════════════════════
//  Game-flow functions
// ═══════════════════════════════════════════════════════════════

async function startNewGame() {
  // Cancel any running CvC loop.
  if (cvcTimer) { clearTimeout(cvcTimer); cvcTimer = null; }
  busy = false;

  const N           = parseInt(selN.value,    10);
  const m           = parseInt(selM.value,    10);
  const mode        = selMode.value;
  const humanFirst  = selFirst.value === 'first';
  const humanPlayer = humanFirst ? 1 : 2;
  const aiScorer    = selAI.value;

  const data = await apiPost('/api/new_game', {
    N, m, mode,
    human_player: humanPlayer,
    ai_scorer:    aiScorer,
  });

  if (data.error) { alert('Could not start game: ' + data.error); return; }

  sessionId = data.session_id;
  state     = data.state;

  initCanvas(state.N);
  render();
  btnRegret.disabled = false;

  // Trigger AI for the first move when applicable.
  if (mode === 'hvc' && !humanFirst) {
    await runAiMove();
  } else if (mode === 'cvc') {
    scheduleCvc();
  }
}

/** Ask the server to compute and play the AI's move. */
async function runAiMove() {
  if (!sessionId || !state || state.game_over) return;

  setBusy(true);
  const data = await apiPost('/api/ai_move', { session_id: sessionId });
  setBusy(false);

  if (data.error) { console.error('AI error:', data.error); return; }

  state = data.state;
  render();

  if (!state.game_over && state.mode === 'cvc') scheduleCvc();
}

function scheduleCvc() {
  cvcTimer = setTimeout(runAiMove, 700);
}

// ═══════════════════════════════════════════════════════════════
//  Canvas click → human move
// ═══════════════════════════════════════════════════════════════
async function onCanvasClick(e) {
  if (busy || !state || state.game_over)                      return;
  if (state.mode === 'cvc')                                   return;
  if (state.mode === 'hvc' &&
      state.current_player !== state.human_player)            return;

  // Convert CSS pixels to grid indices.
  const rect = canvas.getBoundingClientRect();
  const cssX = e.clientX - rect.left;
  const cssY = e.clientY - rect.top;
  const col  = Math.round((cssX - margin) / cellSize);
  const row  = Math.round((cssY - margin) / cellSize);
  const N    = state.N;

  if (col < 0 || col >= N || row < 0 || row >= N)  return;
  if (state.grids[row][col] !== 0)                  return;  // occupied

  setBusy(true);

  const data = await apiPost('/api/move', {
    session_id: sessionId, i: row, j: col,
  });

  if (data.error) {
    setBusy(false);
    return;
  }

  state = data.state;
  render();

  if (!state.game_over && state.mode === 'hvc') {
    await runAiMove();   // runAiMove calls setBusy(false) on completion
  } else {
    setBusy(false);
  }
}

// ═══════════════════════════════════════════════════════════════
//  Regret (undo)
// ═══════════════════════════════════════════════════════════════
async function onRegret() {
  if (busy || !sessionId || !state) return;

  // In hvc: undo both the AI's reply and the human's move (2 steps).
  // In hvh/cvc: undo 1 step.
  const placed = state.grids.reduce((s, row) => s + row.filter(v => v !== 0).length, 0);
  const count  = state.mode === 'hvc' ? Math.min(2, placed) : Math.min(1, placed);
  if (count === 0) return;

  if (cvcTimer) { clearTimeout(cvcTimer); cvcTimer = null; }

  const data = await apiPost('/api/regret', { session_id: sessionId, count });
  if (data.error) return;

  state = data.state;
  render();
}

// ═══════════════════════════════════════════════════════════════
//  Canvas setup
// ═══════════════════════════════════════════════════════════════
function initCanvas(N) {
  margin   = 32;
  cellSize = Math.floor(GRID_SPAN / (N - 1));
  const size = 2 * margin + (N - 1) * cellSize;
  const dpr  = window.devicePixelRatio || 1;

  canvas.width        = size * dpr;
  canvas.height       = size * dpr;
  canvas.style.width  = size + 'px';
  canvas.style.height = size + 'px';

  // Apply DPR scaling once; all drawing then uses CSS-pixel coords.
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

// ═══════════════════════════════════════════════════════════════
//  Rendering
// ═══════════════════════════════════════════════════════════════
function render() {
  updateStatus();
  drawBoard();
}

function drawBoard() {
  if (!state) return;
  const N    = state.N;
  const size = 2 * margin + (N - 1) * cellSize;

  // ── Background ──────────────────────────────────────────────
  ctx.fillStyle = '#D4A84B';
  ctx.fillRect(0, 0, size, size);

  // Subtle edge shadow inset
  const edgeGrad = ctx.createLinearGradient(0, 0, 10, 10);
  edgeGrad.addColorStop(0, 'rgba(0,0,0,0.18)');
  edgeGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = edgeGrad;
  ctx.fillRect(0, 0, size, size);

  // ── Grid lines ───────────────────────────────────────────────
  ctx.strokeStyle = '#7A5200';
  ctx.lineWidth   = 1;
  for (let k = 0; k < N; k++) {
    // Horizontal
    ctx.beginPath();
    ctx.moveTo(margin,                   margin + k * cellSize);
    ctx.lineTo(margin + (N - 1) * cellSize, margin + k * cellSize);
    ctx.stroke();
    // Vertical
    ctx.beginPath();
    ctx.moveTo(margin + k * cellSize, margin);
    ctx.lineTo(margin + k * cellSize, margin + (N - 1) * cellSize);
    ctx.stroke();
  }

  // ── Star points ──────────────────────────────────────────────
  const starR = Math.max(2.5, cellSize * 0.1);
  ctx.fillStyle = '#7A5200';
  for (const [sr, sc] of starPoints(N)) {
    ctx.beginPath();
    ctx.arc(margin + sc * cellSize, margin + sr * cellSize, starR, 0, 2 * Math.PI);
    ctx.fill();
  }

  // ── Coordinate labels ────────────────────────────────────────
  const fontSize = Math.min(11, Math.max(8, cellSize * 0.36));
  ctx.font         = `${fontSize}px sans-serif`;
  ctx.fillStyle    = '#5A3800';
  ctx.textAlign    = 'center';
  ctx.textBaseline = 'middle';
  for (let k = 0; k < N; k++) {
    const label = String(k + 1);
    ctx.fillText(label, margin + k * cellSize, margin / 2);       // top
    ctx.fillText(label, margin / 2,            margin + k * cellSize); // left
  }

  // ── Stones ───────────────────────────────────────────────────
  const lm = state.last_move;
  for (let r = 0; r < N; r++) {
    for (let c = 0; c < N; c++) {
      if (state.grids[r][c] !== 0) {
        const isLast = lm && lm[0] === r && lm[1] === c;
        drawStone(r, c, state.grids[r][c], isLast);
      }
    }
  }
}

function drawStone(r, c, player, isLast) {
  const x      = margin + c * cellSize;
  const y      = margin + r * cellSize;
  const radius = cellSize * 0.46;

  ctx.beginPath();
  ctx.arc(x, y, radius, 0, 2 * Math.PI);

  if (player === 1) {
    // Black stone with radial gradient for a 3-D look.
    const g = ctx.createRadialGradient(
      x - radius * 0.3, y - radius * 0.3, radius * 0.05,
      x,                y,                radius,
    );
    g.addColorStop(0,   '#5a5a5a');
    g.addColorStop(0.6, '#1a1a1a');
    g.addColorStop(1,   '#080808');
    ctx.fillStyle = g;
    ctx.fill();
  } else {
    // White stone
    const g = ctx.createRadialGradient(
      x - radius * 0.3, y - radius * 0.3, radius * 0.05,
      x,                y,                radius,
    );
    g.addColorStop(0, '#ffffff');
    g.addColorStop(1, '#c0c0c0');
    ctx.fillStyle   = g;
    ctx.fill();
    ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    ctx.lineWidth   = 0.8;
    ctx.stroke();
  }

  // Last-move indicator dot.
  if (isLast) {
    const dotR = Math.max(2, radius * 0.22);
    ctx.beginPath();
    ctx.arc(x, y, dotR, 0, 2 * Math.PI);
    ctx.fillStyle = player === 1 ? '#e0e0e0' : '#333333';
    ctx.fill();
  }
}

/** Return star-point [row, col] pairs for an N×N board. */
function starPoints(N) {
  const edge   = N >= 13 ? 3 : 2;
  const center = (N - 1) / 2;
  const far    = N - 1 - edge;

  // Only include positions that lie on integer grid coordinates.
  const pos = [edge];
  if (Number.isInteger(center) && center !== edge) pos.push(center);
  if (far !== edge && far !== center)              pos.push(far);

  const pts = [];
  for (const r of pos) for (const c of pos) pts.push([r, c]);
  return pts;
}

// ═══════════════════════════════════════════════════════════════
//  Status panel
// ═══════════════════════════════════════════════════════════════
function updateStatus() {
  if (!state) {
    statusDot.style.background  = '#555';
    statusDot.style.borderColor = 'transparent';
    statusDot.classList.remove('thinking');
    statusText.textContent = 'Start a new game';
    thinkingOverlay.hidden = true;
    return;
  }

  if (state.game_over) {
    const w = state.winner;
    statusDot.style.background  = w === 1 ? '#111' : w === 2 ? '#f0f0f0' : '#555';
    statusDot.style.borderColor = w === 2 ? '#888' : 'transparent';
    statusDot.classList.remove('thinking');
    statusText.textContent = state.game_over_text || 'Game over';
    thinkingOverlay.hidden = true;
    return;
  }

  const p       = state.current_player;
  const colour  = p === 1 ? 'Black' : 'White';
  statusDot.style.background  = p === 1 ? '#111' : '#f0f0f0';
  statusDot.style.borderColor = p === 2 ? '#888' : 'transparent';

  if (busy) {
    statusDot.classList.add('thinking');
    statusText.textContent = `AI is thinking (${colour})…`;
    thinkingOverlay.hidden = false;
  } else {
    statusDot.classList.remove('thinking');
    thinkingOverlay.hidden = true;

    if (state.mode === 'hvh') {
      statusText.textContent = `Player ${p} (${colour}) to move`;
    } else if (state.mode === 'cvc') {
      statusText.textContent = `AI ${p} (${colour}) to move`;
    } else {
      const isHumanTurn = p === state.human_player;
      statusText.textContent = isHumanTurn
        ? `Your turn (${colour})`
        : `AI (${colour}) to move`;
    }
  }
}

function setBusy(val) {
  busy = val;
  updateStatus();
}
