from game.cards.discard_cards.energy_manipulation_cards.energize import Energize


def test_energize_adds_9_energy_cubes(player):
    Energize().immediate_effect(player, None)
    assert player.energy == 9


def test_energize_costs_8_energy():
    assert Energize().cost == 8
