
#===============================================================================
# Imports
#===============================================================================

import abstract
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP
import time
from collections import defaultdict

PAWN_WEIGHT = 1
KING_WEIGHT = 1.5
RED_RANGE_H = range(4, 8)
BLACK_RANGE_H = range(4)


def distance(x, y):
    dx = abs((x[0] - y[0]))
    dy = abs((x[1] - y[1]))
    return max(dx, dy)
    # sum = 0
    # for i in range(len(x)):
    #     sum += (x[i] - y[i]) ** 2
    # return sum


# ===============================================================================
# Player
# ===============================================================================

class Player(abstract.AbstractPlayer):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        abstract.AbstractPlayer.__init__(self, setup_time, player_color, time_per_k_turns, k)
        self.clock = time.process_time()

        # We are simply providing (remaining time / remaining turns) for each turn in round.
        # Taking a spare time of 0.05 seconds.
        self.turns_remaining_in_round = self.k
        self.time_remaining_in_round = self.time_per_k_turns
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

    def get_move(self, game_state, possible_moves):
        self.clock = time.process_time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05
        if len(possible_moves) == 1:
            # self.turns_remaining_in_round -= 1
            # self.time_remaining_in_round -= (time.process_time() - self.clock)
            return possible_moves[0]

        current_depth = 2
        prev_alpha = -INFINITY

        # Choosing an arbitrary move in case Minimax does not return an answer:
        best_move = possible_moves[0]

        # Initialize Minimax algorithm, still not running anything
        minimax = MiniMaxWithAlphaBetaPruning(self.utility, self.color, self.no_more_time,
                                              self.selective_deepening_criterion)

        # Iterative deepening until the time runs out.
        while True:

            print('going to depth: {}, remaining time: {}, prev_alpha: {}, best_move: {}'.format(
                current_depth,
                self.time_for_current_move - (time.process_time() - self.clock),
                prev_alpha,
                best_move))

            try:
                (alpha, move), run_time = run_with_limited_time(
                    minimax.search, (game_state, current_depth, -INFINITY, INFINITY, True), {},
                    self.time_for_current_move - (time.process_time() - self.clock))
            except (ExceededTimeError, MemoryError):
                print('no more time, achieved depth {}'.format(current_depth))
                break

            if self.no_more_time():
                print('no more time')
                break

            prev_alpha = alpha
            best_move = move

            if alpha == INFINITY:
                print('the move: {} will guarantee victory.'.format(best_move))
                break

            if alpha == -INFINITY:
                print('all is lost')
                break

            current_depth += 1

        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k
            self.time_remaining_in_round = self.time_per_k_turns
        else:
            self.turns_remaining_in_round -= 1
            self.time_remaining_in_round -= (time.process_time() - self.clock)
        return best_move

    def all_kings(self, state):
        for loc_val in state.board.values():
            if loc_val != EM and (loc_val == 'b' or loc_val =='r'):
                return False
        return True

    """new utility"""
    def utility(self, state):
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0
        score = 0
        num_pieces = 0
        red_kings_loc = []
        black_kings_loc = []
        if self.color == 'red':
            for loc in state.board:
                occ = state.board[loc]
                if occ != EM:
                    num_pieces += 1
                    if occ == 'R':
                        score += 10
                        red_kings_loc.append(loc)
                    elif occ == 'B':
                        score -= 10
                        black_kings_loc.append(loc)
                    elif occ == 'r' and loc[0] < 4:
                        score += 5
                    elif occ == 'b' and loc[0] < 4:
                        score -= 7
                    elif occ == 'r' and loc[0] >= 4:
                        score += 7
                    elif occ == 'b' and loc[0] >= 4:
                        score -= 5
        else:
            for loc in state.board:
                occ = state.board[loc]
                if occ != EM:
                    num_pieces += 1
                    if occ == 'B':
                        score += 10
                        black_kings_loc.append(loc)
                    elif occ == 'R':
                        score -= 10
                        red_kings_loc.append(loc)
                    elif occ == 'b' and loc[0] < 4:
                        score += 7
                    elif occ == 'r' and loc[0] < 4:
                        score -= 5
                    elif occ == 'b' and loc[0] >= 4:
                        score += 5
                    elif occ == 'r' and loc[0] >= 4:
                        score -= 7
        # if self.all_kings(state):
        return score/num_pieces

    def selective_deepening_criterion(self, state):
        # #we choose to deepen once we have a jump
        return False

    def no_more_time(self):
        return (time.process_time() - self.clock) >= self.time_for_current_move

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h')
