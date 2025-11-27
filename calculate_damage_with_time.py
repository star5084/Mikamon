"""
Enhanced Damage Calculation with Day/Night Support
This replaces your existing calculate_damage_with_time.py
"""

import random
from python.type_effectiveness import get_type_effectiveness
from python.color import ORANGE, CYAN, GREEN, RED, YELLOW, PURPLE

def calculate_damage_with_time(move_data, attacker_stats, defender_stats, weather=None, day_night=None, action_messages=None):
    """
    Complete damage calculation with:
    - STAB bonus (1.5x if move type matches attacker type)
    - Type effectiveness
    - Weather bonuses
    - Day/Night bonuses (NEW!)
    - Physical vs Special attack/defense
    - Speed-based dodge system (improved to Speed/5 = dodge%, max 20%)
    - Speed-based critical hit (Speed/10 = crit%, max 10%)
    - Proper defense reduction (each point = 0.5% reduction)
    - Stat boost support
    """
    
    base_power = move_data["power"]
    move_type = move_data["type"]
    accuracy = move_data.get("accuracy", 100)
    effect = move_data.get("effect", "physical")
    
    # Skip turn check
    if effect == "skip_turn":
        return 0, 1.0, False
    
    # Miss check based on accuracy
    if random.randint(1, 100) > accuracy:
        return 0, 1.0, True
    
    # ===== APPLY DAY/NIGHT BONUSES TO STATS =====
    attacker_modified = attacker_stats.copy()
    defender_modified = defender_stats.copy()
    
    if day_night:
        attacker_modified, _ = day_night.apply_time_bonus(attacker_stats)
        defender_modified, _ = day_night.apply_time_bonus(defender_stats)
    
    # ===== SPEED-BASED DODGE SYSTEM =====
    # Speed / 5 = dodge % (max 20%)
    defender_speed = defender_modified.get("speed", 50)
    base_dodge_chance = min(20.0, defender_speed / 5.0)
    
    # Apply day/night dodge multiplier if present
    dodge_multiplier = 1.0
    if day_night:
        phase_info = day_night.get_phase_info()
        dodge_multiplier = phase_info["bonuses"].get("dodge_chance", 1.0)
    
    final_dodge_chance = base_dodge_chance * dodge_multiplier
    
    if random.random() * 100 < final_dodge_chance:
        if action_messages is not None:
            action_messages.append({
                "text": f"Dodged with {defender_speed} SPEED! ({final_dodge_chance:.1f}% chance)",
                "color": CYAN
            })
        return 0, 1.0, True
    
    # ===== DETERMINE ATTACK TYPE =====
    physical_effects = ["physical", "strong", "devastating", "stun", "combo", "pierce", 
                       "speed", "rush", "intimidate", "evasive", "authority"]
    special_effects = ["special", "psychic", "energy", "heal", "charm", "cute", "piercing",
                      "artistic", "confuse", "slip", "status", "disable", "charge", "multi"]
    
    is_physical = effect in physical_effects
    
    # Get appropriate offensive stat (with time bonuses applied)
    if is_physical:
        attack_stat = attacker_modified.get("attack", 100)
        # Apply temporary boosts
        if "temp_boosts" in attacker_stats:
            attack_boost = attacker_stats["temp_boosts"].get("attack", 0)
            attack_stat += attack_boost
    else:
        attack_stat = attacker_modified.get("special_attack", 100)
        # Apply temporary boosts
        if "temp_boosts" in attacker_stats:
            attack_boost = attacker_stats["temp_boosts"].get("special_attack", 0)
            attack_stat += attack_boost
    
    # Get appropriate defensive stat (with time bonuses applied)
    if is_physical:
        defense_stat = defender_modified.get("defense", 100)
        # Apply temporary boosts
        if "temp_boosts" in defender_stats:
            defense_boost = defender_stats["temp_boosts"].get("defense", 0)
            defense_stat += defense_boost
    else:
        defense_stat = defender_modified.get("special_defense", 100)
        # Apply temporary boosts
        if "temp_boosts" in defender_stats:
            defense_boost = defender_stats["temp_boosts"].get("special_defense", 0)
            defense_stat += defense_boost
    
    # ===== CALCULATE DAMAGE =====
    # Step 1: Apply attack stat (each point = 1% of base power)
    damage = base_power * (attack_stat / 100.0)
    
    # Different defense effectiveness for physical vs special)
    if is_physical:
        defense_factor = 100.0 / (100.0 + defense_stat * 0.5)
    else:
        defense_factor = 100.0 / (100.0 + defense_stat * 0.7)
    damage *= defense_factor
    
    # ===== STAB BONUS (Same Type Attack Bonus) =====
    stab = 1.5 if move_type in attacker_stats.get("types", []) else 1.0
    damage *= stab
    
    # ===== TYPE EFFECTIVENESS =====
    effectiveness = 1.0
    for def_type in defender_stats.get("types", ["Normal"]):
        effectiveness *= get_type_effectiveness(move_type, def_type)
    
    damage *= effectiveness
    
    # ===== WEATHER BONUS =====
    if weather is not None:
        weather_bonus = weather.get_boost_multiplier(move_type)
        damage *= weather_bonus
        
        if weather_bonus != 1.0 and action_messages is not None:
            weather_boost_percent = int(abs(weather_bonus - 1.0) * 100)
            if weather_bonus > 1.0:
                action_messages.append({
                    "text": f"Weather boosted the move by {weather_boost_percent}%!", 
                    "color": CYAN
                })
    
    # ===== TIME OF DAY BONUS =====
    if day_night:
        time_bonus = day_night.get_type_time_bonus(attacker_stats.get("types", []))
        if time_bonus > 1.0:
            damage *= time_bonus
            if action_messages is not None:
                phase_info = day_night.get_phase_info()
                action_messages.append({
                    "text": f"{phase_info['name']} bonus: +{int((time_bonus - 1.0) * 100)}%!",
                    "color": phase_info['color']
                })
    
    # ===== CRITICAL HIT SYSTEM =====
    # Speed / 10 = base crit % (max 10%)
    attacker_speed = attacker_modified.get("speed", 50)
    crit_chance = min(10.0, attacker_speed / 10.0)
    
    # Critical/devastating effects increase crit chance
    if effect in ["critical", "devastating"]:
        crit_chance = min(25.0, crit_chance + 15.0)
    
    critical_multiplier = 1.0
    if random.random() * 100 < crit_chance:
        critical_multiplier = 1.5
        if action_messages is not None:
            action_messages.append({
                "text": f"Critical hit! ({crit_chance:.1f}% chance)",
                "color": ORANGE
            })
    
    damage *= critical_multiplier
    
    # ===== RANDOM VARIANCE =====
    randomness = random.uniform(0.85, 1.0)
    damage *= randomness
    
    # ===== FINAL DAMAGE =====
    final_damage = max(1, int(damage))
    
    # Debug info (optional, only show occasionally to avoid spam)
    if action_messages and random.random() < 0.3:
        debug_text = f"ATK:{int(attack_stat)} DEF:{int(defense_stat)} DMG:{final_damage}"
        action_messages.append({
            "text": debug_text,
            "color": PURPLE
        })
    
    return final_damage, effectiveness, False


# Alias for backward compatibility
calculate_enhanced_damage = calculate_damage_with_time


def get_effectiveness_text(effectiveness):
    """Get text description and color for type effectiveness"""
    if effectiveness >= 2.0:
        return ("It's super effective!", GREEN)
    elif effectiveness >= 1.5:
        return ("It's very effective!", GREEN)
    elif effectiveness > 1.0:
        return ("It's effective!", GREEN)
    elif effectiveness < 0.5:
        return ("It's not very effective at all...", RED)
    elif effectiveness < 0.8:
        return ("It's not very effective...", RED)
    elif effectiveness < 1.0:
        return ("It's somewhat resisted...", YELLOW)
    return ("", (255, 255, 255))


def get_dodge_info(character, day_night=None):
    """Get dodge chance information for display"""
    speed = character.get("speed", 50)
    base_dodge = min(20.0, speed / 5.0)
    
    dodge_multiplier = 1.0
    if day_night:
        phase_info = day_night.get_phase_info()
        dodge_multiplier = phase_info["bonuses"].get("dodge_chance", 1.0)
    
    final_dodge = base_dodge * dodge_multiplier
    
    return {
        "dodge_chance": final_dodge,
        "speed": speed,
        "display_text": f"{final_dodge:.1f}% dodge"
    }


def get_crit_info(character):
    """Get critical hit chance information"""
    speed = character.get("speed", 50)
    crit_chance = min(10.0, speed / 10.0)
    
    return {
        "crit_chance": crit_chance,
        "display_text": f"{crit_chance:.1f}% crit"
    }


def calculate_speed_order(attacker, defender):
    """
    Determine who goes first based on speed
    Returns: True if attacker goes first, False if defender goes first
    """
    attacker_speed = attacker.get("speed", 50)
    defender_speed = defender.get("speed", 50)
    
    # Add small random factor (±5%) to prevent same-speed ties
    attacker_speed_final = attacker_speed * random.uniform(0.95, 1.05)
    defender_speed_final = defender_speed * random.uniform(0.95, 1.05)
    
    return attacker_speed_final >= defender_speed_final


def get_stat_effectiveness_display(attacker, defender, move_data):
    """
    Show how effective the attack will be based on stats
    Useful for AI decision making and player feedback
    """
    effect = move_data.get("effect", "physical")
    physical_effects = ["physical", "strong", "devastating", "stun", "combo", "pierce"]
    is_physical = effect in physical_effects
    
    if is_physical:
        attack = attacker.get("attack", 100)
        defense = defender.get("defense", 100)
        stat_ratio = attack / defense
    else:
        attack = attacker.get("special_attack", 100)
        defense = defender.get("special_defense", 100)
        stat_ratio = attack / defense
    
    if stat_ratio >= 1.3:
        return ("Strong matchup!", GREEN)
    elif stat_ratio >= 1.1:
        return ("Good matchup", GREEN)
    elif stat_ratio <= 0.7:
        return ("Poor matchup...", RED)
    elif stat_ratio <= 0.9:
        return ("Weak matchup", YELLOW)
    else:
        return ("Even matchup", (200, 200, 200))


def get_damage_breakdown(move_data, attacker, defender, weather=None, day_night=None):
    """
    Get detailed breakdown of damage calculation for debugging/display
    Returns dictionary with all damage components
    """
    effect = move_data.get("effect", "physical")
    physical_effects = ["physical", "strong", "devastating", "stun", "combo", "pierce"]
    is_physical = effect in physical_effects
    
    breakdown = {
        "base_power": move_data["power"],
        "attack_stat": attacker.get("attack" if is_physical else "special_attack", 100),
        "defense_stat": defender.get("defense" if is_physical else "special_defense", 100),
        "attack_type": "Physical" if is_physical else "Special",
        "stab": 1.5 if move_data["type"] in attacker.get("types", []) else 1.0,
        "type_effectiveness": 1.0,
        "weather_bonus": 1.0,
        "time_bonus": 1.0,
        "dodge_chance": min(20.0, defender.get("speed", 50) / 5.0),
        "crit_chance": min(10.0, attacker.get("speed", 50) / 10.0)
    }
    
    # Calculate type effectiveness
    for def_type in defender.get("types", ["Normal"]):
        breakdown["type_effectiveness"] *= get_type_effectiveness(move_data["type"], def_type)
    
    # Weather bonus
    if weather:
        breakdown["weather_bonus"] = weather.get_boost_multiplier(move_data["type"])
    
    # Time bonus
    if day_night:
        breakdown["time_bonus"] = day_night.get_type_time_bonus(attacker.get("types", []))
    
    # Estimate final damage with new formula
    damage = breakdown["base_power"]
    damage *= breakdown["attack_stat"] / 100.0
    damage *= 100.0 / (100.0 + breakdown["defense_stat"] * 0.5)  # New defense formula
    damage *= breakdown["stab"]
    damage *= breakdown["type_effectiveness"]
    damage *= breakdown["weather_bonus"]
    damage *= breakdown["time_bonus"]
    
    breakdown["estimated_damage"] = int(damage * 0.925)  # Average with variance
    breakdown["estimated_damage_max"] = int(damage * 1.5)  # With crit
    
    return breakdown


def get_stat_display_info(character):
    """Get formatted stat display with what they do"""
    return {
        "attack": f"{character['attack']} (Physical DMG)",
        "defense": f"{character['defense']} (Physical RES)",
        "special_attack": f"{character['special_attack']} (Special DMG)",
        "special_defense": f"{character['special_defense']} (Special RES)",
        "speed": f"{character['speed']} (Dodge/Crit/Initiative)",
        "hp": f"{character['hp']} HP"
    }