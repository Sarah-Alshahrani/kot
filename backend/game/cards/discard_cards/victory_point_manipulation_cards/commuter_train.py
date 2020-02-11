from game.cards.discard_card import DiscardCard


class CommuterTrain(DiscardCard):
    def __init__(self):
        super().__init__("Commuter Train", 4, "+ 2[Star]", "")

    def immediate_effect(self, player_that_bought_the_card, other_players):
        player_that_bought_the_card.update_victory_points_by(2)
