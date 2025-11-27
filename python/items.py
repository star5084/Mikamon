from python.color import GRAY, GREEN, BLUE, PURPLE, GOLD
import random

# Battle Items
class BattleItem:
    """Base class for battle items"""
    def __init__(self, name, description, category, effect_type, effect_value, cost=0, rarity="Common"):
        self.name = name
        self.description = description
        self.category = category  # "Healing", "MP", "Stat", "Special"
        self.effect_type = effect_type
        self.effect_value = effect_value
        self.cost = cost
        self.rarity = rarity
        self.color = self.get_rarity_color()
    def get_rarity_color(self):
        """Get color based on rarity"""
        rarity_colors = {
            "Common": GRAY,
            "Uncommon": GREEN,
            "Rare": BLUE,
            "Epic": PURPLE,
            "Legendary": GOLD
        }
        return rarity_colors.get(self.rarity, GRAY)
    def use(self, target_stats, battle_context=None):
        """Use the item and return result message"""
        result = {"success": False, "message": "", "effect": None}
        if self.category == "Healing":
            if self.effect_type == "heal_hp":
                old_hp = target_stats["current_hp"]
                if self.effect_value < 1:  # Percentage heal
                    heal_amount = int(target_stats["max_hp"] * self.effect_value)
                else:  # Flat heal
                    heal_amount = self.effect_value
                if old_hp >= target_stats["max_hp"]:
                    result["message"] = f"{target_stats['name']} is already at full HP!"
                    return result
                target_stats["current_hp"] = min(target_stats["max_hp"], old_hp + heal_amount)
                actual_heal = target_stats["current_hp"] - old_hp
                result["success"] = True
                result["message"] = f"{target_stats['name']} recovered {actual_heal} HP!"
                result["effect"] = {"type": "heal", "amount": actual_heal, "target_pos": target_stats.get("position", (0, 0))}
        elif self.category == "MP":
            if self.effect_type == "restore_mp":
                old_mp = target_stats["current_mp"]
                if self.effect_value < 1:  # Percentage restore
                    mp_amount = int(target_stats["max_mp"] * self.effect_value)
                else:  # Flat restore
                    mp_amount = self.effect_value
                if old_mp >= target_stats["max_mp"]:
                    result["message"] = f"{target_stats['name']} already has full MP!"
                    return result
                target_stats["current_mp"] = min(target_stats["max_mp"], old_mp + mp_amount)
                actual_restore = target_stats["current_mp"] - old_mp
                result["success"] = True
                result["message"] = f"{target_stats['name']} recovered {actual_restore} MP!"
                result["effect"] = {"type": "mp_restore", "amount": actual_restore, "target_pos": target_stats.get("position", (0, 0))}
        elif self.category == "Stat":
            if self.effect_type in ["attack_boost", "defense_boost", "speed_boost", "special_boost"]:
                if "temp_boosts" not in target_stats:
                    target_stats["temp_boosts"] = {}
                boost_type = self.effect_type.split("_")[0]
                current_boost = target_stats["temp_boosts"].get(boost_type, 0)
                
                # Limit stacking
                max_stack = 3
                if current_boost >= max_stack:
                    result["message"] = f"{target_stats['name']}'s {boost_type} can't be boosted further!"
                    return result
                target_stats["temp_boosts"][boost_type] = current_boost + self.effect_value
                result["success"] = True
                result["message"] = f"{target_stats['name']}'s {boost_type.title()} rose!"
                result["effect"] = {"type": "stat_boost", "stat": boost_type, "amount": self.effect_value, "target_pos": target_stats.get("position", (0, 0))}
        elif self.category == "Special":
            if self.effect_type == "max_hp_boost":
                # IMPORTANT: For permanent HP boosts, we handle the logic in battle_system.py
                # This just signals that it's a permanent boost
                result["success"] = True
                result["message"] = f"Permanent max HP boost item used!"
                result["effect"] = {"type": "max_hp_boost", "amount": self.effect_value, "target_pos": target_stats.get("position", (0, 0))}
            elif self.effect_type == "full_restore":
                hp_healed = target_stats["max_hp"] - target_stats["current_hp"]
                mp_restored = target_stats["max_mp"] - target_stats["current_mp"]
                if hp_healed == 0 and mp_restored == 0:
                    result["message"] = f"{target_stats['name']} is already at full health and MP!"
                    return result
                target_stats["current_hp"] = target_stats["max_hp"]
                target_stats["current_mp"] = target_stats["max_mp"]
                
                # Clear negative status effects
                if "temp_boosts" in target_stats:
                    for stat in list(target_stats["temp_boosts"].keys()):
                        if target_stats["temp_boosts"][stat] < 0:
                            del target_stats["temp_boosts"][stat]
                result["success"] = True
                result["message"] = f"{target_stats['name']} was fully restored!"
                result["effect"] = {"type": "full_restore", "hp": hp_healed, "mp": mp_restored, "target_pos": target_stats.get("position", (0, 0))}
        return result

class ItemInventory:
    """Manages player's item inventory"""
    def __init__(self):
        self.items = {}  # item_name: quantity
        self.initialize_starting_items()
    def initialize_starting_items(self):
        """Give player starting items"""
        starting_items = {
            "Healing Potion": 2,
            "MP Elixir": 1,
            "Attack Boost": 1,
            "Speed Boost": 1
        }
        self.items = starting_items.copy()
    def add_item(self, item_name, quantity=1):
        """Add items to inventory"""
        self.items[item_name] = self.items.get(item_name, 0) + quantity
    def remove_item(self, item_name, quantity=1):
        """Remove items from inventory"""
        if item_name in self.items:
            self.items[item_name] = max(0, self.items[item_name] - quantity)
            if self.items[item_name] == 0:
                del self.items[item_name]
    def has_item(self, item_name, quantity=1):
        """Check if inventory has enough of an item"""
        return self.items.get(item_name, 0) >= quantity
    def get_items_by_category(self, category=None):
        """Get items filtered by category"""
        available_items = []
        for item_name, quantity in self.items.items():
            if quantity > 0:
                item = get_item_by_name(item_name)
                if item and (category is None or item.category == category):
                    available_items.append((item, quantity))
        return available_items

# Define all available items
BATTLE_ITEMS = {
    # Healing Items
    "Healing Potion": BattleItem(
        "Healing Potion", "Restores 50 HP", "Healing", "heal_hp", 50, 100, "Common"
    ),
    "Super Potion": BattleItem(
        "Super Potion", "Restores 100 HP", "Healing", "heal_hp", 100, 200, "Uncommon"
    ),
    "Hyper Potion": BattleItem(
        "Hyper Potion", "Restores 200 HP", "Healing", "heal_hp", 200, 400, "Rare"
    ),
    "Max Potion": BattleItem(
        "Max Potion", "Fully restores HP", "Healing", "heal_hp", 400, 800, "Epic"
    ),
    
    # MP Items
    "MP Elixir": BattleItem(
        "MP Elixir", "Restores 30 MP", "MP", "restore_mp", 30, 80, "Common"
    ),
    "Super Elixir": BattleItem(
        "Super Elixir", "Restores 60 MP", "MP", "restore_mp", 60, 160, "Uncommon"
    ),
    "Max Elixir": BattleItem(
        "Max Elixir", "Fully restores MP", "MP", "restore_mp", 400, 400, "Rare"
    ),
    
    # Stat Boosters
    "Attack Boost": BattleItem(
        "Attack Boost", "Raises Attack for this battle", "Stat", "attack_boost", 1, 150, "Common"
    ),
    "Defense Boost": BattleItem(
        "Defense Boost", "Raises Defense for this battle", "Stat", "defense_boost", 1, 150, "Common"
    ),
    "Speed Boost": BattleItem(
        "Speed Boost", "Raises Speed for this battle", "Stat", "speed_boost", 1, 150, "Common"
    ),
    "Special Boost": BattleItem(
        "Special Boost", "Raises Special Attack & Defense", "Stat", "special_boost", 1, 200, "Uncommon"
    ),
    "Mega Booster": BattleItem(
        "Mega Booster", "Greatly raises all stats", "Stat", "attack_boost", 2, 500, "Epic"
    ),
    
    # Special Items - PERMANENT HP BOOSTS
    "HP Up": BattleItem(
        "HP Up", "Permanently increases max HP by 10", "Special", "max_hp_boost", 10, 1000, "Rare"
    ),
    "Vitality Stone": BattleItem(
        "Vitality Stone", "Permanently increases max HP by 25", "Special", "max_hp_boost", 25, 2500, "Epic"
    ),
    "Life Crystal": BattleItem(
        "Life Crystal", "Permanently increases max HP by 50", "Special", "max_hp_boost", 50, 5000, "Legendary"
    ),
    "Full Restore": BattleItem(
        "Full Restore", "Completely restores HP and MP", "Special", "full_restore", 1200, 1200, "Epic"
    ),
}
def get_item_by_name(item_name):
    """Get item object by name"""
    return BATTLE_ITEMS.get(item_name)
# Global inventory
player_inventory = ItemInventory()

# Item Drop System
class ItemDropSystem:
    def __init__(self):
        # Base drop rates
        self.base_drop_rates = {
            "Common": 50.0,      # 50%
            "Uncommon": 25.0,    # 25%  
            "Rare": 15.0,        # 15%
            "Epic": 8.0,         # 8%
            "Legendary": 2.0     # 2%
        }
        
        # Luck multipliers for better drop chances
        self.luck_multipliers = {
            "none": 1.0,         # Normal chances
            "low": 1.2,          # 20% better chances for rare+
            "medium": 1.5,       # 50% better chances for rare+
            "high": 2.0,         # 100% better chances for rare+
            "blessed": 3.0       # 200% better chances for rare+
        }
    def calculate_drop_rates(self, luck_level="none"):
        """Calculate adjusted drop rates based on luck"""
        rates = self.base_drop_rates.copy()
        multiplier = self.luck_multipliers.get(luck_level, 1.0)
        
        if multiplier > 1.0:
            # Increase rare+ item chances
            rates["Rare"] *= multiplier
            rates["Epic"] *= multiplier
            rates["Legendary"] *= multiplier
            
            # Normalize to 100%
            total = sum(rates.values())
            for rarity in rates:
                rates[rarity] = (rates[rarity] / total) * 100
        
        return rates
    
    def get_random_rarity(self, luck_level="none"):
        """Get a random rarity based on drop rates"""
        rates = self.calculate_drop_rates(luck_level)
        
        rand = random.uniform(0, 100)
        cumulative = 0
        
        # Check from rarest to most common
        for rarity in ["Legendary", "Epic", "Rare", "Uncommon", "Common"]:
            cumulative += rates[rarity]
            if rand <= cumulative:
                return rarity
        
        return "Common"  # Fallback
    
    def get_items_by_rarity(self, rarity):
        """Get all items of a specific rarity"""
        return [item for item in BATTLE_ITEMS.values() if item.rarity == rarity]
    
    def get_random_item(self, luck_level="none", category_filter=None):
        """Get a random item with specified luck modifiers"""
        rarity = self.get_random_rarity(luck_level)
        possible_items = self.get_items_by_rarity(rarity)
        
        # Filter by category if specified
        if category_filter:
            possible_items = [item for item in possible_items if item.category == category_filter]
        
        if not possible_items:
            # Fallback to common items if no items found
            possible_items = self.get_items_by_rarity("Common")
            if category_filter:
                possible_items = [item for item in possible_items if item.category == category_filter]
        
        return random.choice(possible_items) if possible_items else None

# Simple reward functions  
def get_random_item_drop(luck_level="none"):
    """Get a random item drop with specified luck level"""
    drop_system = ItemDropSystem()
    return drop_system.get_random_item(luck_level)

def get_random_item_by_category(category, luck_level="none"):
    """Get a random item from specific category with luck"""
    drop_system = ItemDropSystem()
    return drop_system.get_random_item(luck_level, category_filter=category)