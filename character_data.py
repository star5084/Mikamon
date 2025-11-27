"""
Enhanced Character Data with 5 Moves
- Moves 1-4: Your original attacks (UNCHANGED)
- Move 5: New special or ultimate attack with enhanced effects
"""

from python.color import GREEN, GOLD, PURPLE, PINK, RED, CYAN, ORANGE

characters = {
    "bushy0225": {
        "types": ["Grass", "Oil"], 
        "hp": 145,
        "attack": 75,
        "defense": 120,
        "special_attack": 95,
        "special_defense": 100,
        "speed": 70,
        "color": GREEN, 
        "sprite_file": "Miwawas.png",
        "max_energy": 100, 
        "energy_regen": 12,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Vine Bonk": {"power": 45, "type": "Grass", "accuracy": 95, "effect": "physical", "energy_cost": 10},
            "Grease Seed": {"power": 50, "type": "Oil", "accuracy": 90, "effect": "special", "energy_cost": 15},
            "Solar Beam": {"power": 90, "type": "Grass", "accuracy": 100, "effect": "special", "energy_cost": 35},
            "Oil Slick": {"power": 40, "type": "Oil", "accuracy": 100, "effect": "special", "energy_cost": 20},
            # NEW 5th move - SPECIAL ATTACK
            "Nature's Wrath": {"power": 120, "type": "Grass", "accuracy": 85, "effect": "devastating", "energy_cost": 50, "is_special": True}
        }
    },
    "star5084": {
        "types": ["Light", "Crude Oil"], 
        "hp": 120,
        "attack": 70,
        "defense": 75,
        "special_attack": 130,
        "special_defense": 85,
        "speed": 110,
        "color": GOLD, 
        "sprite_file": "Miwawas.png",
        "max_energy": 100, 
        "energy_regen": 11,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Solar Flare": {"power": 55, "type": "Light", "accuracy": 90, "effect": "special", "energy_cost": 18},
            "Crude Strike": {"power": 50, "type": "Crude Oil", "accuracy": 95, "effect": "physical", "energy_cost": 12},
            "Starlight": {"power": 65, "type": "Light", "accuracy": 85, "effect": "special", "energy_cost": 25},
            "Black Gold": {"power": 85, "type": "Crude Oil", "accuracy": 80, "effect": "special", "energy_cost": 30},
            # NEW 5th move - ULTIMATE ATTACK
            "Supernova": {"power": 140, "type": "Light", "accuracy": 80, "effect": "devastating", "energy_cost": 55, "is_ultimate": True}
        }
    },
    "Mika ga Hoshii": {
        "types": ["Star", "Miwiwi"], 
        "hp": 130,
        "attack": 90,
        "defense": 95,
        "special_attack": 110,
        "special_defense": 105,
        "speed": 95,
        "color": PURPLE, 
        "sprite_file": "Miwawas.png",
        "max_energy": 110, 
        "energy_regen": 13,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Galaxy Beam": {"power": 55, "type": "Star", "accuracy": 90, "effect": "special", "energy_cost": 16},
            "Miwiwi Beam": {"power": 70, "type": "Miwiwi", "accuracy": 85, "effect": "special", "energy_cost": 28},
            "Cosmic Ray": {"power": 50, "type": "Star", "accuracy": 95, "effect": "special", "energy_cost": 14},
            "Miwiwi Storm": {"power": 65, "type": "Miwiwi", "accuracy": 100, "effect": "special", "energy_cost": 25},
            # NEW 5th move - ULTIMATE ATTACK
            "Celestial Collapse": {"power": 130, "type": "Star", "accuracy": 75, "effect": "devastating", "energy_cost": 60, "is_ultimate": True}
        }
    },
    "Mika": {
        "types": ["Catgirl", "Mod"], 
        "hp": 155,
        "attack": 70,
        "defense": 110,
        "special_attack": 95,
        "special_defense": 125,
        "speed": 80,
        "color": PINK, 
        "sprite_file": "Mikawr.png",
        "max_energy": 120, 
        "energy_regen": 12,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Cat Ears": {"power": 55, "type": "Catgirl", "accuracy": 95, "effect": "special", "energy_cost": 15},
            "Mod Hammer": {"power": 70, "type": "Mod", "accuracy": 87, "effect": "physical", "energy_cost": 28},
            "Catgirl Beam": {"power": 65, "type": "Catgirl", "accuracy": 85, "effect": "special", "energy_cost": 24},
            "Catnip Wave": {"power": 50, "type": "Catgirl", "accuracy": 100, "effect": "special", "energy_cost": 18},
            # NEW 5th move - SPECIAL ATTACK
            "Divine Judgment": {"power": 125, "type": "Mod", "accuracy": 85, "effect": "devastating", "energy_cost": 55, "is_special": True}
        }
    },
    "Jay": {
        "types": ["Bonk", "Mod"], 
        "hp": 140,
        "attack": 125,
        "defense": 95,
        "special_attack": 70,
        "special_defense": 90,
        "speed": 65,
        "color": RED, 
        "sprite_file": "Miwawas.png",
        "max_energy": 90, 
        "energy_regen": 12,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Banhammer": {"power": 80, "type": "Bonk", "accuracy": 86, "effect": "physical", "energy_cost": 32},
            "Timeout Wave": {"power": 40, "type": "Mod", "accuracy": 100, "effect": "special", "energy_cost": 12},
            "Mega Bonk": {"power": 100, "type": "Bonk", "accuracy": 75, "effect": "physical", "energy_cost": 40},
            "Admin Strike": {"power": 60, "type": "Mod", "accuracy": 90, "effect": "physical", "energy_cost": 20},
            # NEW 5th move - ULTIMATE ATTACK
            "Permaban": {"power": 135, "type": "Bonk", "accuracy": 78, "effect": "devastating", "energy_cost": 58, "is_ultimate": True}
        }
    },
    "Belisarius": {
        "types": ["Oil", "Imagination"], 
        "hp": 115,
        "attack": 65,
        "defense": 80,
        "special_attack": 135,
        "special_defense": 110,
        "speed": 120,
        "color": CYAN, 
        "sprite_file": "Miwawas.png",
        "max_energy": 130, 
        "energy_regen": 13,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Dream Splash": {"power": 55, "type": "Imagination", "accuracy": 90, "effect": "special", "energy_cost": 16},
            "Creative Oil": {"power": 50, "type": "Oil", "accuracy": 95, "effect": "special", "energy_cost": 14},
            "Reality Warp": {"power": 80, "type": "Imagination", "accuracy": 80, "effect": "special", "energy_cost": 30},
            "Oil Canvas": {"power": 45, "type": "Oil", "accuracy": 100, "effect": "special", "energy_cost": 12},
            # NEW 5th move - ULTIMATE ATTACK
            "Infinite Canvas": {"power": 145, "type": "Imagination", "accuracy": 80, "effect": "devastating", "energy_cost": 62, "is_ultimate": True}
        }
    },
    "car_tanle": {
        "types": ["Car", "Miwawa"], 
        "hp": 165,
        "attack": 105,
        "defense": 130,
        "special_attack": 65,
        "special_defense": 100,
        "speed": 55,
        "color": ORANGE, 
        "sprite_file": "Miwawas.png",
        "max_energy": 80, 
        "energy_regen": 14,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Turbo Ram": {"power": 65, "type": "Car", "accuracy": 90, "effect": "physical", "energy_cost": 24},
            "Miwawa Rush": {"power": 55, "type": "Miwawa", "accuracy": 95, "effect": "physical", "energy_cost": 18},
            "Engine Roar": {"power": 85, "type": "Car", "accuracy": 85, "effect": "physical", "energy_cost": 35},
            "Drift Attack": {"power": 50, "type": "Car", "accuracy": 100, "effect": "physical", "energy_cost": 16},
            # NEW 5th move - SPECIAL ATTACK
            "Nitro Crash": {"power": 115, "type": "Car", "accuracy": 85, "effect": "devastating", "energy_cost": 52, "is_special": True}
        }
    },
    "Mutthunter1": {
        "types": ["Human", "Bonk"], 
        "hp": 135,
        "attack": 115,
        "defense": 100,
        "special_attack": 80,
        "special_defense": 95,
        "speed": 100,
        "color": (255, 220, 177), 
        "sprite_file": "Miwawas.png",
        "max_energy": 95, 
        "energy_regen": 14,
        "moves": {
            # Original 4 moves - UNCHANGED
            "Power Punch": {"power": 55, "type": "Human", "accuracy": 95, "effect": "physical", "energy_cost": 16},
            "Bonk Slam": {"power": 70, "type": "Bonk", "accuracy": 85, "effect": "physical", "energy_cost": 26},
            "Haymaker": {"power": 65, "type": "Human", "accuracy": 90, "effect": "physical", "energy_cost": 22},
            "Bonk Combo": {"power": 60, "type": "Bonk", "accuracy": 100, "effect": "physical", "energy_cost": 20},
            # NEW 5th move - ULTIMATE ATTACK
            "Final Bonk": {"power": 128, "type": "Bonk", "accuracy": 82, "effect": "devastating", "energy_cost": 56, "is_ultimate": True}
        }
    },
}