from game.cards.card import Card
from game.cards.keep_card import KeepCard
from game.values import constants


class SolarPowered(KeepCard):
    def __init__(self):
        Card.__init__(self, "Solar Powered", 4, "At the end of your turn gain 1[Energy] if you have no [Energy].", "")

    def immediate_effect(self, player_that_bought_the_card, other_players):
        card = SolarPowered()
        player_that_bought_the_card.add_card(card)

    def special_effect(self, player_that_bought_the_card, other_players):
        if player_that_bought_the_card.energy == constants.DEATH_HIT_POINT:
            player_that_bought_the_card.update_energy_by(1)

# TODO Turn related logic for trigger
