from python.color import GREEN, DARK_GREEN, RED, DARK_RED, BLACK
def get_effectiveness_text(multiplier):
    if multiplier >= 2.0:
        return "SUPER EFFECTIVE!", GREEN
    elif multiplier > 1.0:
        return "It's effective!", DARK_GREEN
    elif multiplier < 0.75:
        return "Not very effective...", RED
    elif multiplier < 1.0:
        return "It's not very effective", DARK_RED
    else:
        return "", BLACK