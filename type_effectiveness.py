# Type effectiveness chart
TYPE_CHART = {
    "Grass": {"Oil": 1.4, "Light": 0.6, "Car": 1.8, "Human": 1.2},
    "Oil": {"Catgirl": 1.7, "Bonk": 0.7, "Grass": 1.9, "Light": 0.8},
    "Light": {"Imagination": 1.6, "Grass": 1.9, "Human": 1.1, "Car": 1.3, "Star": 0.5},
    "Star": {"Human": 1.5, "Imagination": 1.6, "Light": 0.6, "Bonk": 1.3},
    "Bonk": {"Star": 1.8, "Light": 1.7, "Oil": 0.5, "Human": 1.4},
    "Mod": {"Miwiwi": 2.0, "Miwawa": 2.0, "Crude Oil": 0.5, "Human": 1.6},
    "Imagination": {"Catgirl": 1.7, "Human": 1.5, "Mod": 0.6, "Car": 1.3},
    "Miwiwi": {"Car": 2.0, "Oil": 1.9, "Star": 0.5, "Grass": 1.2},
    "Crude Oil": {"Catgirl": 2.0, "Grass": 0.5, "Car": 0.5, "Light": 1.3},
    "Catgirl": {"Human": 1.7, "Miwawa": 2.0, "Car": 0.6, "Imagination": 1.2},
    "Car": {"Miwiwi": 1.7, "Mod": 1.8, "Oil": 0.6, "Grass": 0.7},
    "Miwawa": {"Miwiwi": 0.6, "Catgirl": 1.8, "Imagination": 0.6, "Bonk": 1.2},
    "Human": {"Bonk": 1.5, "Imagination": 1.6, "Star": 0.7, "Catgirl": 0.8},
}

def get_type_effectiveness(attack_type, defend_type):
    """Calculate type effectiveness multiplier"""
    if attack_type in TYPE_CHART and defend_type in TYPE_CHART[attack_type]:
        return TYPE_CHART[attack_type][defend_type]
    return 1.0