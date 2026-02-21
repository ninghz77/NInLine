"""
webapp.py – Flask web server for N-in-a-Line.

Reuses the existing game engine (core/game_base.py) and scorers unchanged.
Existing main*.py scripts continue to work independently.

Run locally:
    python webapp.py

Deploy (Heroku / Render / Railway):
    gunicorn webapp:app
"""
import os
import sys
import uuid

import numpy as np
from flask import Flask, jsonify, render_template, request

# Allow imports of core/ and scorers/ from the project root.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.game_base import GameBase                          # noqa: E402
from scorers.alpha_beta_scorer import AlphaBetaScorer        # noqa: E402
from scorers.full_line_scorer import FullLineScorer          # noqa: E402
from scorers.scorer_base import ScorerBase                   # noqa: E402

app = Flask(
    __name__,
    template_folder='web/templates',
    static_folder='web/static',
)

# ── In-memory session store ───────────────────────────────────────────────────
# Maps session_id (str) -> dict with game state.
# For a production deployment with multiple workers, replace with Redis/DB.
_games: dict = {}

SCORER_MAP = {
    'full_line':  FullLineScorer,
    'alpha_beta': AlphaBetaScorer,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_state(gs: dict) -> dict:
    """Serialise game session to a JSON-safe dict for the frontend."""
    game: GameBase = gs['game']
    last_move = None
    if game.steps:
        _, li, lj = game.steps[-1]
        last_move = [li, lj]
    return {
        'grids':          game.grids.tolist(),
        'current_player': gs['current_player'],
        'game_over':      game.game_over(),
        'game_over_text': game.game_over_text() if game.game_over() else '',
        'winner':         game.winner,
        'N':              game.N,
        'm':              game.m,
        'mode':           gs['mode'],
        'human_player':   gs['human_player'],
        'last_move':      last_move,
    }


def _next_player(player: int) -> int:
    return 3 - player   # toggles between 1 and 2


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.get_json() or {}

    N            = max(5,  min(19, int(data.get('N',            15))))
    m            = max(3,  min(N,  int(data.get('m',             5))))
    mode         = data.get('mode',       'hvc')   # 'hvc' | 'hvh' | 'cvc'
    human_player = int(data.get('human_player', 2))  # 1 or 2 (hvc only)
    ai_name      = data.get('ai_scorer',  'full_line')
    scorer_cls   = SCORER_MAP.get(ai_name, FullLineScorer)

    if mode == 'hvh':
        p1_cls, p2_cls = ScorerBase, ScorerBase
    elif mode == 'cvc':
        p1_cls, p2_cls = scorer_cls, scorer_cls
    elif human_player == 1:
        p1_cls, p2_cls = ScorerBase, scorer_cls
    else:
        p1_cls, p2_cls = scorer_cls, ScorerBase

    game = GameBase(0, N, m, p1_cls, p2_cls)
    game.start()

    session_id = str(uuid.uuid4())
    _games[session_id] = {
        'game':           game,
        'mode':           mode,
        'human_player':   human_player,
        'current_player': 1,
    }
    return jsonify({'session_id': session_id, 'state': _build_state(_games[session_id])})


@app.route('/api/move', methods=['POST'])
def move():
    """Human places a stone."""
    data       = request.get_json() or {}
    session_id = data.get('session_id')
    gs         = _games.get(session_id)
    if not gs:
        return jsonify({'error': 'session not found'}), 404

    game = gs['game']
    if game.game_over():
        return jsonify({'error': 'game already over'}), 400

    player = gs['current_player']
    try:
        i, j = int(data['i']), int(data['j'])
    except (KeyError, ValueError):
        return jsonify({'error': 'invalid coordinates'}), 400

    valid, _ = game.step(i, j, player)
    if not valid:
        return jsonify({'error': 'invalid move'}), 400

    if not game.game_over():
        gs['current_player'] = _next_player(player)

    return jsonify({'state': _build_state(gs)})


@app.route('/api/ai_move', methods=['POST'])
def ai_move():
    """AI computes and places a stone."""
    data       = request.get_json() or {}
    session_id = data.get('session_id')
    gs         = _games.get(session_id)
    if not gs:
        return jsonify({'error': 'session not found'}), 404

    game = gs['game']
    if game.game_over():
        return jsonify({'error': 'game already over'}), 400

    player = gs['current_player']
    i, j   = game.player_best_grid(player)

    if i == -1:
        # Board is empty — fall back to the scorer's opening move.
        scorer = game.scorer1 if player == 1 else game.scorer2
        i, j   = scorer.init_grid()

    valid, _ = game.step(i, j, player)
    if not valid:
        return jsonify({'error': 'AI could not place a stone'}), 500

    if not game.game_over():
        gs['current_player'] = _next_player(player)

    return jsonify({'move': [i, j], 'state': _build_state(gs)})


@app.route('/api/regret', methods=['POST'])
def regret():
    """Undo the last `count` moves."""
    data       = request.get_json() or {}
    session_id = data.get('session_id')
    count      = max(0, int(data.get('count', 1)))
    gs         = _games.get(session_id)
    if not gs:
        return jsonify({'error': 'session not found'}), 404

    game = gs['game']
    for _ in range(count):
        if game.steps:
            game.regret_step()

    # Recalculate whose turn it is from the last recorded step.
    if game.steps:
        gs['current_player'] = _next_player(game.steps[-1][0])
    else:
        gs['current_player'] = 1

    return jsonify({'state': _build_state(gs)})


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
