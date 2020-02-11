from game.cards.card import Card
from game.cards.keep_cards.nova_breath import NovaBreath
from game.values.constants import CARD_FOOTNOTE_KEY, CARD_EFFECT_KEY, CARD_COST_KEY, CARD_NAME_KEY

title = "Test title"
cost = 100
description = "Lose 100 energy"
footnote = "Why would you buy this?"


class TestCard(Card):
    def __init__(self):
        Card.__init__(self, title, cost, description, footnote)


def test_card_dict():
    card = TestCard()
    dict = card.to_dict()
    assert dict.get(CARD_NAME_KEY) == title
    assert dict.get(CARD_COST_KEY) == 100
    assert dict.get(CARD_EFFECT_KEY) == description
    assert dict.get(CARD_FOOTNOTE_KEY) == footnote


def test_card_json():
    card = TestCard()
    json = card.to_json()
    assert json == '{{"{}": "Test title", "{}": 100, "{}": "Lose 100 energy", "{}": "Why would you buy this?"}}'.format(
        CARD_NAME_KEY, CARD_COST_KEY, CARD_EFFECT_KEY, CARD_FOOTNOTE_KEY)


def test_methods_carry_to_inherited_classes():
    card = NovaBreath()
    assert card.to_dict().get("effect")

    assert card.to_json() == '{{"{}": "Nova Breath", "{}": 7, "{}": "Your [attack] Smash all other monsters", ' \
                             '"{}": null}}'.format(CARD_NAME_KEY, CARD_COST_KEY, CARD_EFFECT_KEY, CARD_FOOTNOTE_KEY)