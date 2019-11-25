from game.cards.discard_card import DiscardCard
from game.cards.card import Card


class GasRefinery(DiscardCard):
    def __init__(self):
        Card.__init__(self, "Gas Refinery", 6,
                         "+ 2[Star] and other monsters lose 3[health]", "")

    def immediate_effect(self, player_that_bought_the_card, other_players):
        player_that_bought_the_card.update_victory_points_by(2)
        for other_player in other_players:
            other_player.update_health_by(-3)