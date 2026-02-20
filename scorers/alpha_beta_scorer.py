"""
scorers/alpha_beta_scorer.py

Alpha-Beta Minimax scorer for n-in-a-line.

Improvements over FLNStepScorer (NStepScorer with FullLineScorer):

  1. True adversarial minimax – the opponent is a true minimiser, not just
     a "subtract with decay" approximation.  The weighted-sum path
     aggregation in NStepScorer does not model adversarial play correctly:
     the opponent still picks its *highest* move and the result is merely
     subtracted with a discount factor.  Here the opponent genuinely
     minimises our score.

  2. Alpha-beta pruning – branches provably unable to affect the result are
     cut early.  With good move ordering (FullLineScorer already orders
     candidates by descending score) the first branch often sets a tight
     bound and prunes ~50-80 % of the tree, freeing budget for deeper search.

  3. Forced-move collapsing – when an immediate win or a mandatory block
     exists (score >= FORCE_RATIO × max_num), only that small set of moves
     is explored.  In critical positions this reduces branching to 1-2
     candidates, making the search essentially free.

  4. In-place board updates – a single numpy array is modified and then
     restored, avoiding the repeated deepcopy overhead of NStepScorer.
"""
import numpy as np
from scorers.scorer_base import ScorerBase, ScoredGrid
from scorers.full_line_scorer import FullLineScorer


class AlphaBetaScorer(ScorerBase):
    """
    Alpha-beta minimax scorer for n-in-a-line.

    Parameters
    ----------
    DEPTH : int
        Search depth in plies.  DEPTH=4 means we look at our move, then
        the opponent's reply, then our move, then the opponent's reply
        before calling the static evaluator — i.e. two full turns ahead.
    TOP_N : int
        Maximum candidate moves examined at each node (before alpha-beta
        pruning reduces the effective branching factor further).
    FORCE_RATIO : float
        A candidate whose score is >= FORCE_RATIO * max_num is treated as a
        "forced" move (immediate win or mandatory block).  When forced moves
        exist only those are explored, collapsing the branch count.
        At max_num = 10e6 the threshold is 3e6, which captures:
          - immediate wins          (score = max_num ≈ 10e6)
          - self open-four          (score = max_num/3 ≈ 3.3e6)
          - blocking opponent open-four (score = max_num/2 = 5e6)
    """

    DEPTH = 5
    TOP_N = 5
    FORCE_RATIO = 0.30   # threshold = 0.30 × max_num ≈ 3 × 10^6

    def __init__(self, grids, m, player):
        super().__init__(grids, m, player)
        self.name = "AlphaBetaScorer"
        self.author = "ninghz"

    def init_grid(self):
        return self.rand_init_grid()

    # ------------------------------------------------------------------ #
    # Public interface                                                     #
    # ------------------------------------------------------------------ #

    def best_grid(self):
        candidates = self._candidates(self.player)
        if not candidates:
            return ScoredGrid(0, self.init_grid())

        # Immediate win at the root — no need to search further.
        for c in candidates:
            if c.win:
                c.score = self.max_num * (self.DEPTH + 1)
                return c

        best_move  = candidates[0]
        best_score = -float('inf')
        alpha = -float('inf')
        beta  =  float('inf')

        for c in candidates:
            i, j = c.grid
            self.grids[i, j] = self.player
            score = self._minimax(self.DEPTH - 1, alpha, beta, maximizing=False)
            self.grids[i, j] = 0            # undo

            if score > best_score:
                best_score = score
                best_move  = c
            alpha = max(alpha, score)
            # No beta cutoff at root (there is no parent node to cut).

        best_move.score = best_score
        return best_move

    # ------------------------------------------------------------------ #
    # Alpha-beta minimax                                                   #
    # ------------------------------------------------------------------ #

    def _minimax(self, depth, alpha, beta, maximizing):
        player     = self.player if maximizing else self.opponent
        # At leaf nodes use only the top-1 candidate to avoid a full board
        # re-scan; the top candidate's attack_score serves as the positional
        # estimate without any extra FullLineScorer call.
        n          = self.TOP_N if depth > 0 else 1
        candidates = self._candidates(player, n)

        if not candidates:
            return 0

        # Shortcut: top candidate is an immediate win for the current player.
        if candidates[0].win:
            sign = 1 if maximizing else -1
            return sign * self.max_num * (depth + 2)

        if depth == 0:
            # Leaf evaluation: sign-adjusted attack score of the best move
            # available to the current player.  Using attack_score (the purely
            # offensive sub-score) avoids double-counting defensive info that
            # the minimax recursion already handles via the opponent's minimisation.
            sign = 1 if maximizing else -1
            return sign * candidates[0].attack_score

        if maximizing:
            value = -float('inf')
            for c in candidates:
                if c.win:
                    return self.max_num * (depth + 2)
                i, j = c.grid
                self.grids[i, j] = player
                value = max(value, self._minimax(depth - 1, alpha, beta, False))
                self.grids[i, j] = 0
                alpha = max(alpha, value)
                if beta <= alpha:
                    break               # beta cut-off: parent minimiser won't allow this
            return value
        else:
            value = float('inf')
            for c in candidates:
                if c.win:
                    return -self.max_num * (depth + 2)
                i, j = c.grid
                self.grids[i, j] = player
                value = min(value, self._minimax(depth - 1, alpha, beta, True))
                self.grids[i, j] = 0
                beta = min(beta, value)
                if beta <= alpha:
                    break               # alpha cut-off: parent maximiser already has better
            return value

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def _candidates(self, player, n=None):
        """
        Return up to *n* candidate moves for *player* (default: TOP_N).

        When any candidate is a forced move (immediate win, or a blocking
        move scoring above the FORCE_RATIO threshold), return *only* the
        forced candidates.  This collapses the branching factor to 1-2 in
        critical positions without losing correctness.
        """
        if n is None:
            n = self.TOP_N
        scorer    = FullLineScorer(self.grids, self.m, player)
        all_cands = scorer.top_n_grids(n)
        if not all_cands:
            return all_cands

        threshold = self.max_num * self.FORCE_RATIO
        forced    = [c for c in all_cands if c.win or c.score >= threshold]
        return forced if forced else all_cands
