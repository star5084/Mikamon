"""
Game Save/Load System
Manages game saves including inventory, difficulty, and settings
Also manages permanent character stats deletion
"""

import json
import os
from datetime import datetime

SAVE_FILE = "python/game_save.json"
PERMANENT_CHARACTER_STATS = "python/permanent_character_stats.json"

class SaveSystem:
    """Manages game saves and loading"""
    
    def __init__(self):
        self.save_data = None
        self.save_exists = os.path.exists(SAVE_FILE)
    
    def create_new_save(self, difficulty="Normal"):
        """Create a new game save with default values"""
        self.save_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "last_played": datetime.now().isoformat(),
            "difficulty": difficulty,
            "settings": {
                "music_volume": 0.1,
                "fight_music_volume": 0.1,
                "show_clock": True,
                "show_ai_predictions": False,
                "difficulty": difficulty  # Store difficulty in settings too
            },
            "inventory": {
                "Healing Potion": 2,
                "MP Elixir": 1,
                "Attack Boost": 1,
                "Speed Boost": 1
            },
            "stats": {
                "battles_won": 0,
                "battles_lost": 0,
                "total_battles": 0
            }
        }
        self.save_game()
        return self.save_data
    
    def load_game(self):
        """Load existing save file"""
        if not os.path.exists(SAVE_FILE):
            return None
        
        try:
            with open(SAVE_FILE, 'r') as f:
                self.save_data = json.load(f)
            
            # Update last played time
            self.save_data["last_played"] = datetime.now().isoformat()
            self.save_game()
            
            print(f"Game loaded successfully. Last played: {self.save_data['last_played']}")
            return self.save_data
        except Exception as e:
            print(f"Error loading save: {e}")
            return None
    
    def save_game(self):
        """Save current game data to file"""
        if self.save_data is None:
            print("No save data to write!")
            return False
        
        try:
            # Update last played time
            self.save_data["last_played"] = datetime.now().isoformat()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
            
            with open(SAVE_FILE, 'w') as f:
                json.dump(self.save_data, f, indent=2)
            
            print(f"Game saved successfully at {self.save_data['last_played']}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def update_inventory(self, inventory_dict):
        """Update inventory in save data"""
        if self.save_data:
            self.save_data["inventory"] = inventory_dict
            self.save_game()
    
    def update_difficulty(self, difficulty):
        """Update difficulty setting"""
        if self.save_data:
            self.save_data["difficulty"] = difficulty
            # Also update in settings
            self.save_data["settings"]["difficulty"] = difficulty
            self.save_game()
    
    def update_settings(self, settings_dict):
        """Update game settings"""
        if self.save_data:
            self.save_data["settings"].update(settings_dict)
            self.save_game()
    
    def update_battle_stats(self, won):
        """Update battle statistics"""
        if self.save_data:
            self.save_data["stats"]["total_battles"] += 1
            if won:
                self.save_data["stats"]["battles_won"] += 1
            else:
                self.save_data["stats"]["battles_lost"] += 1
            self.save_game()
    
    def delete_permanent_stats(self):
        """Delete the permanent character stats file"""
        try:
            if os.path.exists(PERMANENT_CHARACTER_STATS):
                os.remove(PERMANENT_CHARACTER_STATS)
                print("Permanent character stats deleted")
                return True
            return True  # Return True even if file doesn't exist
        except Exception as e:
            print(f"Error deleting permanent stats: {e}")
            return False
    
    def delete_save(self):
        """Delete the current save file AND permanent character stats"""
        success = True
        
        # Delete main save file
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
                print("Save file deleted")
                self.save_data = None
                self.save_exists = False
        except Exception as e:
            print(f"Error deleting save: {e}")
            success = False
        
        # Delete permanent character stats
        if not self.delete_permanent_stats():
            success = False
        
        # Reset permanent stats system if it's loaded
        try:
            from python.permanent_hp_system import permanent_character_stats
            permanent_character_stats.reset_all()
            print("Permanent character stats system reset")
        except Exception as e:
            print(f"Error resetting permanent stats system: {e}")
        
        return success
    
    def has_save(self):
        """Check if a save file exists"""
        return os.path.exists(SAVE_FILE)
    
    def get_save_info(self):
        """Get information about the save file for display"""
        if not self.has_save():
            return None
        
        save = self.load_game()
        if save:
            try:
                last_played = datetime.fromisoformat(save["last_played"])
                time_str = last_played.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = "Unknown"
            
            return {
                "last_played": time_str,
                "difficulty": save.get("difficulty", "Normal"),
                "battles_won": save.get("stats", {}).get("battles_won", 0),
                "battles_lost": save.get("stats", {}).get("battles_lost", 0),
                "total_battles": save.get("stats", {}).get("total_battles", 0)
            }
        return None

# Global save system instance
save_system = SaveSystem()