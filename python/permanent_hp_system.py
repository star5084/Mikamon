"""
Permanent Character Stats System
Saves permanent stat boosts to character data that persist across all battles
"""

import json
import os

# File to store permanent character modifications
PERMANENT_STATS_FILE = "python/permanent_character_stats.json"

class PermanentCharacterStats:
    """Manages permanent stat modifications for characters"""
    
    def __init__(self):
        self.permanent_boosts = {}
        self.load_permanent_stats()
    
    def load_permanent_stats(self):
        """Load permanent stats from file"""
        if os.path.exists(PERMANENT_STATS_FILE):
            try:
                with open(PERMANENT_STATS_FILE, 'r') as f:
                    self.permanent_boosts = json.load(f)
                print(f"Loaded permanent stats: {self.permanent_boosts}")
            except Exception as e:
                print(f"Error loading permanent stats: {e}")
                self.permanent_boosts = {}
        else:
            self.permanent_boosts = {}
    
    def save_permanent_stats(self):
        """Save permanent stats to file"""
        try:
            os.makedirs(os.path.dirname(PERMANENT_STATS_FILE), exist_ok=True)
            with open(PERMANENT_STATS_FILE, 'w') as f:
                json.dump(self.permanent_boosts, f, indent=2)
            print(f"Saved permanent stats: {self.permanent_boosts}")
        except Exception as e:
            print(f"Error saving permanent stats: {e}")
    
    def add_hp_boost(self, character_name, boost_amount):
        """Add permanent HP boost to a character"""
        if character_name not in self.permanent_boosts:
            self.permanent_boosts[character_name] = {
                "hp_boost": 0,
                "mp_boost": 0,
                "attack_boost": 0,
                "defense_boost": 0
            }
        
        self.permanent_boosts[character_name]["hp_boost"] += boost_amount
        self.save_permanent_stats()
        return self.permanent_boosts[character_name]["hp_boost"]
    
    def add_mp_boost(self, character_name, boost_amount):
        """Add permanent MP boost to a character"""
        if character_name not in self.permanent_boosts:
            self.permanent_boosts[character_name] = {
                "hp_boost": 0,
                "mp_boost": 0,
                "attack_boost": 0,
                "defense_boost": 0
            }
        
        self.permanent_boosts[character_name]["mp_boost"] += boost_amount
        self.save_permanent_stats()
        return self.permanent_boosts[character_name]["mp_boost"]
    
    def get_character_boosts(self, character_name):
        """Get all permanent boosts for a character"""
        if character_name not in self.permanent_boosts:
            return {
                "hp_boost": 0,
                "mp_boost": 0,
                "attack_boost": 0,
                "defense_boost": 0
            }
        return self.permanent_boosts[character_name].copy()
    
    def get_total_hp(self, character_name, base_hp):
        """Get character's total HP including permanent boosts"""
        boosts = self.get_character_boosts(character_name)
        return base_hp + boosts["hp_boost"]
    
    def get_total_mp(self, character_name, base_mp):
        """Get character's total MP including permanent boosts"""
        boosts = self.get_character_boosts(character_name)
        return base_mp + boosts["mp_boost"]
    
    def reset_character(self, character_name):
        """Reset all permanent boosts for a character"""
        if character_name in self.permanent_boosts:
            del self.permanent_boosts[character_name]
            self.save_permanent_stats()
    
    def reset_all(self):
        """Reset all permanent boosts for all characters"""
        self.permanent_boosts = {}
        self.save_permanent_stats()


# Global instance
permanent_character_stats = PermanentCharacterStats()


def apply_permanent_boosts_to_character(character_data, character_name):
    """
    Apply permanent boosts to a character's data before battle
    
    Args:
        character_data: The character dictionary
        character_name: Name of the character
    
    Returns:
        Modified character_data with permanent boosts applied
    """
    boosts = permanent_character_stats.get_character_boosts(character_name)
    
    # Store original values
    if "_original_hp" not in character_data:
        character_data["_original_hp"] = character_data["hp"]
    if "_original_max_energy" not in character_data:
        character_data["_original_max_energy"] = character_data.get("max_energy", 100)
    
    # Apply permanent boosts
    character_data["hp"] = character_data["_original_hp"] + boosts["hp_boost"]
    character_data["max_energy"] = character_data["_original_max_energy"] + boosts["mp_boost"]
    
    # Store boost info for display
    character_data["_permanent_boosts"] = boosts
    
    return character_data


def use_permanent_hp_item(character_name, character_data, boost_amount):
    """
    Use a permanent HP boost item on a character
    
    Args:
        character_name: Name of the character
        character_data: Current character data dictionary
        boost_amount: Amount to boost HP by
    
    Returns:
        tuple: (new_hp, new_max_hp, total_permanent_boost)
    """
    # Add to permanent storage
    total_boost = permanent_character_stats.add_hp_boost(character_name, boost_amount)
    
    # Update current battle stats
    if "_original_hp" not in character_data:
        character_data["_original_hp"] = character_data["hp"]
    
    # Calculate new max HP
    new_max_hp = character_data["_original_hp"] + total_boost
    
    # Current HP increases by the boost amount (healing effect)
    current_hp = character_data.get("current_hp", character_data["hp"])
    new_current_hp = current_hp + boost_amount
    
    # Update character data
    character_data["hp"] = new_max_hp
    character_data["_permanent_boosts"] = permanent_character_stats.get_character_boosts(character_name)
    
    return new_current_hp, new_max_hp, total_boost


def get_character_display_info(character_name, base_hp, base_mp):
    """
    Get display information about a character's permanent boosts
    
    Args:
        character_name: Name of the character
        base_hp: Base HP value
        base_mp: Base MP value
    
    Returns:
        dict with display info
    """
    boosts = permanent_character_stats.get_character_boosts(character_name)
    
    return {
        "has_boosts": any(v > 0 for v in boosts.values()),
        "hp_boost": boosts["hp_boost"],
        "mp_boost": boosts["mp_boost"],
        "total_hp": base_hp + boosts["hp_boost"],
        "total_mp": base_mp + boosts["mp_boost"],
        "boost_text": f"HP: {base_hp}+{boosts['hp_boost']} | MP: {base_mp}+{boosts['mp_boost']}"
    }