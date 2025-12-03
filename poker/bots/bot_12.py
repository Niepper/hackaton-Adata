from engine import BaseAgent, Action, ActionType, PlayerState
from treys import Card, Evaluator


class SolidTAG(BaseAgent):


    def __init__(self, name: str):
        super().__init__(name)
        self.evaluator = Evaluator()

        self.premium_pairs = ['AA', 'KK', 'QQ', 'JJ', 'TT']
        self.strong_pairs = ['99', '88', '77']
        self.premium_cards = ['AK', 'AQ', 'AJ', 'KQ']

    def _card_str_to_treys(self, card_str: str):
        return Card.new(card_str)

    def _get_hand_rank(self, hand, community):
        treys_hand = [self._card_str_to_treys(c) for c in hand]
        treys_board = [self._card_str_to_treys(c) for c in community]
        return self.evaluator.evaluate(treys_board, treys_hand)

    def _is_pair_or_better_preflop(self, hand):

        ranks = [c[0] for c in hand]
        is_pair = ranks[0] == ranks[1]

        order = '23456789TJQKA'
        ranks_sorted = sorted(ranks, key=lambda x: order.index(x), reverse=True)
        hand_type = "".join(ranks_sorted)

        return hand_type, is_pair

    def act(self, state: PlayerState) -> Action:

        is_preflop = len(state.community_cards) == 0

        if is_preflop:
            return self.play_preflop(state)
        else:
            return self.play_postflop(state)

    def play_preflop(self, state: PlayerState) -> Action:
        hand_type, is_pair = self._is_pair_or_better_preflop(state.hand)

        if hand_type in self.premium_pairs or hand_type == 'AK':
            raise_amount = max(state.min_raise, state.pot * 1.8)
            return Action(ActionType.RAISE, amount=int(raise_amount))

        if hand_type in self.strong_pairs or hand_type in self.premium_cards:
            if state.current_bet < state.stack * 0.1:
                return Action(ActionType.RAISE, amount=int(state.min_raise))
            return Action(ActionType.CHECK_CALL)

        if state.current_bet == 0:
            return Action(ActionType.CHECK_CALL)

        return Action(ActionType.FOLD)

    def play_postflop(self, state: PlayerState) -> Action:

        score = self._get_hand_rank(state.hand, state.community_cards)

        strength = 1.0 - (score / 7462.0)

        if score < 3325:
            bet_size = state.pot * 0.75
            target_amount = state.current_bet + bet_size
            return Action(ActionType.RAISE, amount=int(target_amount))
        elif score < 6000:
            if state.current_bet > state.stack * 0.4:
                return Action(ActionType.FOLD)
            return Action(ActionType.CHECK_CALL)


        else:
            if state.current_bet == 0:
                return Action(ActionType.CHECK_CALL)

            return Action(ActionType.FOLD)