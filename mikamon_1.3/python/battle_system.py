import sys, random, math, pygame
from python.character_data import characters
from python.music import play_fight_music, play_title_music, stop_all_music, update_music_volumes, fight_music_loaded, title_music_loaded, current_music_type,test_fight_volume, get_music_status
from python.weather import Weather, WeatherEffects, Particle
from python.ai import *
from python.items import player_inventory, get_random_item_drop, get_random_item_by_category
from python.pygame1 import SCREEN, FONT, BIG_FONT, SMALL_FONT, CLOCK
from python.settings import game_settings
from python.color import LIGHT_GRAY, DARK_GRAY, BLACK, WHITE, GREEN, DARK_GREEN, RED, DARK_RED, BLUE, DARK_BLUE, PURPLE, PINK, GRAY, ORANGE, CYAN, GOLD, YELLOW
from python.shadowed_text_and_buttons import draw_text_with_shadow, draw_gradient_button
from python.energy_and_health_bars import draw_energy_bar, draw_animated_health_bar
from python.item_menu import draw_item_menu, handle_item_menu_scroll, reset_item_scroll
from python.clock import draw_real_time_clock
from python.floating_text import FloatingText
from python.item_particle import ItemParticle
from python.calculate_damage_with_time import calculate_damage_with_time, get_dodge_info, get_effectiveness_text
from python.day_night_cycle import day_night_cycle
from python.wait_for_key import wait_for_key
from collections import defaultdict, Counter
from python.type_effectiveness import get_type_effectiveness
from python.permanent_hp_system import permanent_character_stats, apply_permanent_boosts_to_character, use_permanent_hp_item, get_character_display_info
from python.attack_animations import AttackAnimationManager, create_animation_for_move
from python.save_system import save_system
import time
from python.special_attack_display import draw_enhanced_move_button
from python.special_attack_anims import create_special_animation


# Test volume cooldown tracker
test_volume_cooldown = 0

# AI with prediction
class PredictiveAI:
    def __init__(self, character_data, difficulty="Normal"):
        self.character = character_data
        self.difficulty = difficulty
        self.turn_count = 0
        self.last_effectiveness = {}
        self.move_history = []
        self.energy_management_strategy = "balanced"
        
        # Prediction system attributes
        self.player_move_history = []
        self.player_patterns = {
            'move_sequences': defaultdict(list),
            'situational_preferences': {
                'low_hp': defaultdict(int),
                'high_hp': defaultdict(int),
                'low_energy': defaultdict(int),
                'high_energy': defaultdict(int)
            },
            'type_preferences': defaultdict(int),
            'timing_patterns': defaultdict(int),
            'counter_history': defaultdict(int),
            'repetition_tendency': 0,
            'aggression_level': 0.5
        }
        self.prediction_accuracy = {'correct': 0, 'total': 0}
        self.last_prediction = None
        self.player_character_data = None
    
    def record_player_move(self, move_name, player_hp_ratio, player_energy_ratio, 
                          our_last_move=None, game_phase="early"):
        """Record a player's move with contextual information"""
        self.player_move_history.append({
            'move': move_name,
            'hp_ratio': player_hp_ratio,
            'energy_ratio': player_energy_ratio,
            'turn': self.turn_count,
            'our_last_move': our_last_move,
            'phase': game_phase
        })
        
        self._update_patterns(move_name, player_hp_ratio, player_energy_ratio, 
                            our_last_move, game_phase)
        
        # Check prediction accuracy
        if self.last_prediction:
            self.prediction_accuracy['total'] += 1
            if self.last_prediction == move_name:
                self.prediction_accuracy['correct'] += 1
    
    def _update_patterns(self, move_name, hp_ratio, energy_ratio, our_last_move, phase):
        """Update pattern recognition data"""
        # Situational preferences
        if hp_ratio < 0.3:
            self.player_patterns['situational_preferences']['low_hp'][move_name] += 1
        elif hp_ratio > 0.7:
            self.player_patterns['situational_preferences']['high_hp'][move_name] += 1
            
        if energy_ratio < 0.3:
            self.player_patterns['situational_preferences']['low_energy'][move_name] += 1
        elif energy_ratio > 0.7:
            self.player_patterns['situational_preferences']['high_energy'][move_name] += 1
        
        # Move sequences
        if len(self.player_move_history) >= 2:
            prev_move = self.player_move_history[-2]['move']
            self.player_patterns['move_sequences'][prev_move].append(move_name)
        
        # Response to our moves
        if our_last_move:
            self.player_patterns['counter_history'][our_last_move + '->' + move_name] += 1
        
        # Timing patterns
        self.player_patterns['timing_patterns'][phase + '_' + move_name] += 1
        
        # Calculate repetition tendency
        if len(self.player_move_history) >= 5:
            recent_moves = [m['move'] for m in self.player_move_history[-5:]]
            unique_moves = len(set(recent_moves))
            self.player_patterns['repetition_tendency'] = 1.0 - (unique_moves / 5.0)
        
        # Update aggression level
        if move_name != "Skip Turn" and self.player_character_data:
            if move_name in self.player_character_data["moves"]:
                move_data = self.player_character_data["moves"][move_name]
                power = move_data.get('power', 0)
                energy_cost = move_data.get('energy_cost', 0)
                
                aggression_indicator = (power / 50.0) + (energy_cost / 30.0)
                current_aggression = self.player_patterns['aggression_level']
                self.player_patterns['aggression_level'] = (current_aggression * 0.8 + 
                                                          min(aggression_indicator, 1.0) * 0.2)
        else:
            current_aggression = self.player_patterns['aggression_level']
            self.player_patterns['aggression_level'] = current_aggression * 0.9
    
    def predict_next_move(self, player_hp_ratio, player_energy_ratio, 
                         our_last_move, game_phase="mid"):
        """Predict the player's next move based on patterns"""
        if len(self.player_move_history) < 3:
            self.last_prediction = None
            return None, 0.0
        
        move_probabilities = defaultdict(float)
        total_confidence = 0.0
        
        # Pattern 1: Situational preferences
        situation_weight = 0.3
        if player_hp_ratio < 0.3:
            for move, count in self.player_patterns['situational_preferences']['low_hp'].items():
                move_probabilities[move] += count * situation_weight
                total_confidence += situation_weight
        elif player_hp_ratio > 0.7:
            for move, count in self.player_patterns['situational_preferences']['high_hp'].items():
                move_probabilities[move] += count * situation_weight
                total_confidence += situation_weight
        
        if player_energy_ratio < 0.3:
            for move, count in self.player_patterns['situational_preferences']['low_energy'].items():
                move_probabilities[move] += count * situation_weight
                total_confidence += situation_weight
            move_probabilities["Skip Turn"] += 5 * situation_weight
        elif player_energy_ratio > 0.7:
            for move, count in self.player_patterns['situational_preferences']['high_energy'].items():
                move_probabilities[move] += count * situation_weight
                total_confidence += situation_weight
        
        # Pattern 2: Move sequences
        sequence_weight = 0.25
        if len(self.player_move_history) >= 1:
            last_move = self.player_move_history[-1]['move']
            if last_move in self.player_patterns['move_sequences']:
                next_moves = self.player_patterns['move_sequences'][last_move]
                move_counts = Counter(next_moves)
                for move, count in move_counts.items():
                    move_probabilities[move] += count * sequence_weight
                    total_confidence += sequence_weight
        
        # Pattern 3: Response to our moves
        counter_weight = 0.2
        if our_last_move:
            for pattern, count in self.player_patterns['counter_history'].items():
                if pattern.startswith(our_last_move + '->'):
                    response_move = pattern.split('->')[-1]
                    move_probabilities[response_move] += count * counter_weight
                    total_confidence += counter_weight
        
        # Pattern 4: Timing patterns
        timing_weight = 0.15
        phase_key = game_phase + '_'
        for pattern, count in self.player_patterns['timing_patterns'].items():
            if pattern.startswith(phase_key):
                move = pattern[len(phase_key):]
                move_probabilities[move] += count * timing_weight
                total_confidence += timing_weight
        
        # Pattern 5: Repetition tendency
        repetition_weight = 0.1
        if (self.player_patterns['repetition_tendency'] > 0.6 and 
            len(self.player_move_history) >= 2):
            recent_move = self.player_move_history[-1]['move']
            move_probabilities[recent_move] += self.player_patterns['repetition_tendency'] * repetition_weight
            total_confidence += repetition_weight
        
        if not move_probabilities:
            self.last_prediction = None
            return None, 0.0
        
        predicted_move = max(move_probabilities, key=move_probabilities.get)
        max_probability = move_probabilities[predicted_move]
        confidence = min(1.0, max_probability / max(1.0, total_confidence))
        
        if self.prediction_accuracy['total'] > 5:
            accuracy_rate = self.prediction_accuracy['correct'] / self.prediction_accuracy['total']
            confidence *= (0.5 + accuracy_rate * 0.5)
        
        self.last_prediction = predicted_move
        return predicted_move, confidence
    
    def get_prediction_stats(self):
        """Get AI prediction statistics"""
        if self.prediction_accuracy['total'] == 0:
            return {"accuracy": 0.0, "predictions_made": 0, "player_aggression": 0.5, "repetition_tendency": 0.0}
        
        accuracy = self.prediction_accuracy['correct'] / self.prediction_accuracy['total']
        return {
            "accuracy": accuracy,
            "predictions_made": self.prediction_accuracy['total'],
            "player_aggression": self.player_patterns['aggression_level'],
            "repetition_tendency": self.player_patterns['repetition_tendency']
        }
    
    def choose_move(self, player_types, player_hp, max_player_hp, own_hp, max_own_hp, weather):
        """Move selection with prediction integration"""
        self.turn_count += 1
        
        player_hp_ratio = player_hp / max_player_hp
        player_energy_ratio = getattr(self, 'player_energy_ratio', 0.5)
        game_phase = "early" if self.turn_count < 5 else "mid" if self.turn_count < 10 else "late"
        
        predicted_move, confidence = self.predict_next_move(
            player_hp_ratio, player_energy_ratio,
            self.move_history[-1] if self.move_history else None,
            game_phase
        )
        
        if predicted_move and confidence > 0.4:
            return self._choose_counter_move(predicted_move, confidence, player_types,
                                           player_hp, max_player_hp, own_hp, max_own_hp, weather)
        else:
            return self._choose_basic_move(player_types, player_hp, max_player_hp, own_hp, max_own_hp, weather)
    
    def _choose_basic_move(self, player_types, player_hp, max_player_hp, own_hp, max_own_hp, weather):
        """Basic AI move selection"""
        moves = list(self.character["moves"].items())
        skip_turn_data = get_skip_turn_move(self.character)
        
        current_energy = getattr(self, 'current_energy', self.character.get("max_energy", 100))
        max_energy = self.character.get("max_energy", 100)
        
        if self.difficulty == "Easy":
            available_moves = [(name, data) for name, data in moves 
                             if current_energy >= data.get("energy_cost", 0)]
            if available_moves:
                return random.choice(available_moves)
            else:
                return ("Skip Turn", skip_turn_data)
        
        move_scores = {}
        
        for move_name, move_data in moves:
            energy_cost = move_data.get("energy_cost", 0)
            if current_energy < energy_cost:
                continue
                
            base_power = move_data.get("power", 0)
            move_type = move_data.get("type", "Normal")
            accuracy = move_data.get("accuracy", 100)
            
            score = base_power
            
            total_effectiveness = 1.0
            for player_type in player_types:
                effectiveness = get_type_effectiveness(move_type, player_type)
                total_effectiveness *= effectiveness
            
            if total_effectiveness >= 2.0:
                score += 40
            elif total_effectiveness >= 1.5:
                score += 25
            elif total_effectiveness < 0.8:
                score -= 30
            elif total_effectiveness < 0.5:
                score -= 50
            
            if weather:
                weather_multiplier = weather.get_boost_multiplier(move_type)
                score += (weather_multiplier - 1.0) * 50
            
            score *= (accuracy / 100.0)
            
            if energy_cost > 0:
                efficiency = base_power / energy_cost
                score += efficiency * 2
            
            move_scores[move_name] = score
        
        energy_ratio = current_energy / max_energy
        health_ratio = own_hp / max_own_hp
        
        skip_score = 0
        if energy_ratio < 0.3:
            skip_score += 40
        elif energy_ratio < 0.5:
            skip_score += 20
        
        if health_ratio < 0.3:
            skip_score += 15
            
        move_scores["Skip Turn"] = skip_score
        
        randomness_factor = 5 if self.difficulty == "Hard" else 15
        for move_name in move_scores:
            move_scores[move_name] += random.uniform(-randomness_factor, randomness_factor)
        
        if not move_scores:
            return ("Skip Turn", skip_turn_data)
            
        best_move = max(move_scores, key=move_scores.get)
        self._record_move(best_move)
        
        if best_move == "Skip Turn":
            return (best_move, skip_turn_data)
        else:
            return (best_move, self.character["moves"][best_move])
    
    def _record_move(self, move_name):
        """Record move for pattern analysis"""
        self.move_history.append(move_name)
        if len(self.move_history) > 10:
            self.move_history.pop(0)
    
    def _choose_counter_move(self, predicted_move, confidence, player_types,
                           player_hp, max_player_hp, own_hp, max_own_hp, weather):
        """Choose a move to counter the predicted player move"""
        current_energy = getattr(self, 'current_energy', self.character.get("max_energy", 100))
        moves = list(self.character["moves"].items())
        skip_turn_data = get_skip_turn_move(self.character)
        
        counter_strategies = self._get_counter_strategies(predicted_move, player_types, weather)
        
        move_scores = {}
        for move_name, move_data in moves:
            energy_cost = move_data.get("energy_cost", 0)
            if current_energy < energy_cost:
                continue
                
            base_power = move_data.get("power", 0)
            move_type = move_data.get("type", "Normal")
            accuracy = move_data.get("accuracy", 100)
            
            score = base_power
            
            total_effectiveness = 1.0
            for player_type in player_types:
                effectiveness = get_type_effectiveness(move_type, player_type)
                total_effectiveness *= effectiveness
            
            if total_effectiveness >= 2.0:
                score += 40
            elif total_effectiveness >= 1.5:
                score += 25
            
            if weather:
                weather_multiplier = weather.get_boost_multiplier(move_type)
                score += (weather_multiplier - 1.0) * 50
            
            score *= (accuracy / 100.0)
            
            counter_bonus = 0
            for strategy, bonus in counter_strategies.items():
                if self._move_fits_strategy(move_name, move_data, strategy):
                    counter_bonus += bonus * confidence
            
            move_scores[move_name] = score + counter_bonus
        
        energy_ratio = current_energy / self.character.get("max_energy", 100)
        skip_score = 0
        if energy_ratio < 0.3:
            skip_score += 40
        elif energy_ratio < 0.5:
            skip_score += 20
        
        move_scores["Skip Turn"] = skip_score
        
        if not move_scores:
            return ("Skip Turn", skip_turn_data)
        
        randomness_factor = 10 if confidence > 0.7 else 20
        for move_name in move_scores:
            move_scores[move_name] += random.uniform(-randomness_factor, randomness_factor)
        
        best_move = max(move_scores, key=move_scores.get)
        self._record_move(best_move)
        
        if best_move == "Skip Turn":
            return (best_move, skip_turn_data)
        else:
            return (best_move, self.character["moves"][best_move])
    
    def _get_counter_strategies(self, predicted_move, player_types, weather):
        """Define counter strategies for different predicted moves"""
        strategies = {}
        
        if predicted_move == "Skip Turn":
            strategies["high_damage"] = 40
            strategies["energy_efficient"] = 20
        else:
            if self.player_character_data and predicted_move in self.player_character_data["moves"]:
                predicted_move_data = self.player_character_data["moves"][predicted_move]
                predicted_power = predicted_move_data.get('power', 0)
                predicted_type = predicted_move_data.get('type', 'Normal')
                predicted_effect = predicted_move_data.get('effect', '')
                
                if predicted_power > 40:
                    strategies["defensive"] = 30
                    strategies["disable"] = 25
                
                for our_move_name, our_move_data in self.character["moves"].items():
                    our_type = our_move_data.get('type', 'Normal')
                    resistance = get_type_effectiveness(predicted_type, our_type)
                    if resistance < 1.0:
                        strategies["type_resistant"] = 35
                
                effect_counters = {
                    "critical": "defensive",
                    "devastating": "defensive", 
                    "heal": "high_damage",
                    "status": "disable",
                    "stun": "quick_attack",
                    "multi": "defensive"
                }
                
                counter_strategy = effect_counters.get(predicted_effect)
                if counter_strategy:
                    strategies[counter_strategy] = 25
        
        return strategies
    
    def _move_fits_strategy(self, move_name, move_data, strategy):
        """Check if a move fits a counter strategy"""
        if strategy == "high_damage":
            return move_data.get('power', 0) > 35
        elif strategy == "energy_efficient":
            power = move_data.get('power', 0)
            cost = move_data.get('energy_cost', 1)
            if cost == 0:
                return power > 0
            return power / cost > 1.5
        elif strategy == "defensive":
            effect = move_data.get('effect', '')
            return effect in ["heal", "status", "disable"] or move_data.get('power', 0) < 25
        elif strategy == "disable":
            effect = move_data.get('effect', '')
            return effect in ["disable", "stun", "confuse"]
        elif strategy == "quick_attack":
            return move_data.get('energy_cost', 0) < 20 and move_data.get('power', 0) > 15
        elif strategy == "type_resistant":
            return True
        return False

def start_battle_music():
    """Start battle music with better error handling"""
    print("=== STARTING BATTLE MUSIC ===")
    
    music_status = get_music_status()
    print(f"Music system status: {music_status}")
    
    if not music_status['mixer_initialized']:
        print("ERROR: Audio mixer not initialized!")
        return False
    
    if music_status['fight_loaded']:
        print("Fight music is loaded, attempting to play...")
        
        if play_fight_music():
            print("Fight music started successfully")
            return True
        else:
            print("Failed to start fight music")
            return False
    else:
        print("Fight music not available - check that fight_music.wav exists in the music folder")
        return False

def battle(player_name, sprites, battle_sprites, background):
    global test_volume_cooldown
    player = characters[player_name].copy()
    enemy_chars = [name for name in characters.keys() if name != player_name]
    enemy_name = random.choice(enemy_chars)
    enemy_data = characters[enemy_name].copy()
    
    # Apply permanent boosts from previous battles
    player = apply_permanent_boosts_to_character(player, player_name)
    enemy_data = apply_permanent_boosts_to_character(enemy_data, enemy_name)
    
    print("Starting battle between", player_name, "and", enemy_name)
    
    music_started = start_battle_music()
    
    if not music_started:
        print("Continuing battle without fight music...")
    
    # Battle variables
    player_hp = player["hp"]
    max_player_hp = player["hp"]
    enemy_hp = enemy_data["hp"]
    max_enemy_hp = enemy_data["hp"]
    
    # Energy system - properly initialized from character data
    max_player_energy = player.get("max_energy", 100)
    player_energy = max_player_energy  # Start at max
    player_energy_regen = player.get("energy_regen", 15)
    
    max_enemy_energy = enemy_data.get("max_energy", 100)
    enemy_energy = max_enemy_energy  # Start at max
    enemy_energy_regen = enemy_data.get("energy_regen", 15)
    
    print(f"Player {player_name}: Max Energy={max_player_energy}, Regen={player_energy_regen}")
    print(f"Enemy {enemy_name}: Max Energy={max_enemy_energy}, Regen={enemy_energy_regen}")
    
    # Initialize temporary boosts
    player["temp_boosts"] = {}
    enemy_data["temp_boosts"] = {}
    
    # Player stats for item usage
    player_battle_stats = {
        "name": player_name,
        "current_hp": player_hp,
        "max_hp": max_player_hp,
        "current_mp": player_energy,
        "max_mp": max_player_energy,
        "temp_boosts": player["temp_boosts"],
        "position": (960 - 400, 250)
    }

    
    # Weather system (existing)
    weather = Weather()
    weather_effects = WeatherEffects()
    weather_effects.set_weather(weather.current_weather)
    
    # Day/Night cycle
    day_night = day_night_cycle
    day_night.update_phase()
    print(f"Battle starting at {day_night.get_phase_info()['name']}")
    
    # AI system with prediction
    enemy_ai = PredictiveAI(enemy_data, game_settings["difficulty"])
    enemy_ai.current_energy = enemy_energy
    enemy_ai.player_character_data = player
    
    move_names = list(player["moves"].keys())
    move_names.append("Skip Turn")
    action_messages = []
    floating_texts = []
    particles = []
    item_particles = []
    animation_manager = AttackAnimationManager()
    screen_width, screen_height = SCREEN.get_size()
    center_x = screen_width // 2
    show_exit_menu = False
    show_battle_settings = False
    show_item_menu = False
    current_item_category = "All"
    
    # Animation variables
    battle_timer = 0
    shake_intensity = 0
    shake_duration = 0
    turn_count = 0
    running = True
    last_save_time = pygame.time.get_ticks()
    SAVE_INTERVAL = 5 * 60 * 1000

    def use_item(item, target_stats):
        """Use an item and update game state with permanent HP tracking"""
        nonlocal player_hp, max_player_hp, player_energy, max_player_energy
        if not player_inventory.has_item(item.name):
            action_messages.append({"text": f"You don't have any {item.name}!", "color": RED})
            return
        
        result = item.use(target_stats)
        if result["success"]:
            player_inventory.remove_item(item.name)
            
            # Handle permanent HP boost items - SAVES FOREVER
            if item.effect_type == "max_hp_boost":
                # Use the permanent character stats system
                player_hp, max_player_hp, total_boost = use_permanent_hp_item(
                    player_name, player, item.effect_value
                )
                
                # Update battle stats
                target_stats["max_hp"] = max_player_hp
                target_stats["current_hp"] = player_hp
                
                action_messages.append({
                "text": f"{target_stats['name']}'s max HP +{item.effect_value} permanently! (Total: +{total_boost})", 
                    "color": GOLD
                })
                
                # Extra visual feedback for permanent boost
                action_messages.append({
                    "text": f"This boost will carry over to ALL future battles!", 
                    "color": PURPLE
                })
                
                pos = target_stats["position"]
                floating_texts.append(FloatingText(f"PERMANENT +{item.effect_value} MAX HP!", pos[0] - 50, pos[1] - 20, GOLD))
                
                colors = [GOLD, PURPLE, CYAN, WHITE]
                for _ in range(30):
                    px = pos[0] + random.randint(-60, 60)
                    py = pos[1] + random.randint(-40, 40)
                    color = random.choice(colors)
                    item_particles.append(ItemParticle(px, py, color, "permanent"))
            else:
                player_hp = target_stats["current_hp"]
                max_player_hp = target_stats["max_hp"]
                player_energy = target_stats["current_mp"]
                max_player_energy = target_stats["max_mp"]
                
                action_messages.append({"text": result["message"], "color": GREEN})
                
                if result["effect"]:
                    effect = result["effect"]
                    pos = target_stats["position"]
                    if effect["type"] == "heal":
                        floating_texts.append(FloatingText(f"+{effect['amount']} HP", pos[0], pos[1] - 20, GREEN))
                        
                        for _ in range(15):
                            px = pos[0] + random.randint(-60, 30)
                            py = pos[1] + random.randint(-20, 20)
                            item_particles.append(ItemParticle(px, py, GREEN, "heal"))
                    elif effect["type"] == "mp_restore":
                        floating_texts.append(FloatingText(f"+{effect['amount']} MP", pos[0], pos[1] - 20, CYAN))
                        
                        for _ in range(12):
                            px = pos[0] + random.randint(-25, 25)
                            py = pos[1] + random.randint(-15, 15)
                            item_particles.append(ItemParticle(px, py, CYAN, "mp_restore"))
                    elif effect["type"] == "stat_boost":
                        floating_texts.append(FloatingText(f"{effect['stat'].title()} UP!", pos[0], pos[1] - 20, GOLD))
                        
                        for _ in range(10):
                            px = pos[0] + random.randint(-20, 20)
                            py = pos[1] + random.randint(-10, 10)
                            item_particles.append(ItemParticle(px, py, GOLD, "stat_boost"))
                    elif effect["type"] == "full_restore":
                        floating_texts.append(FloatingText("FULLY RESTORED!", pos[0] - 30, pos[1] - 20, GOLD))
                        
                        colors = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN]
                        for _ in range(25):
                            px = pos[0] + random.randint(-50, 50)
                            py = pos[1] + random.randint(-40, 40)
                            color = random.choice(colors)
                            item_particles.append(ItemParticle(px, py, color, "special"))
        else:
            action_messages.append({"text": result["message"], "color": ORANGE})
    
    def execute_move(move):
        nonlocal player_hp, enemy_hp, player_energy, enemy_energy, turn_count
        nonlocal shake_intensity, shake_duration, max_player_hp, max_player_energy, max_enemy_hp, max_enemy_energy

        
        player_hp_ratio = player_hp / max_player_hp
        player_energy_ratio = player_energy / max_player_energy
        game_phase = "early" if turn_count < 5 else "mid" if turn_count < 10 else "late"
        
        our_last_move = enemy_ai.move_history[-1] if enemy_ai.move_history else None
        
        # Handle Skip Turn
        if move == "Skip Turn":
            skip_turn_data = get_skip_turn_move(player)
            mp_regen = skip_turn_data.get("mp_regeneration", 0)
            
            player_energy = min(max_player_energy, player_energy + mp_regen)
            action_messages.append({
                "text": f"{player_name} skipped their turn and regenerated {mp_regen} MP!", 
                "color": CYAN
            })
            
            floating_texts.append(FloatingText(f"+{mp_regen} MP", center_x - 400, 190, CYAN))
            
            for _ in range(10):
                px = center_x - 400 + random.randint(-30, 30)
                py = 230 + random.randint(-30, 30)
                vx = random.uniform(-2, 2)
                vy = random.uniform(-4, -1)
                particles.append(Particle(px, py, CYAN, vx, vy, 1000))
        else:
            move_data = player["moves"][move]
            energy_cost = move_data.get("energy_cost", 0)
            
            if player_energy < energy_cost:
                action_messages.append({"text": f"Not enough MP to use {move}!", "color": RED})
                print(f"Player tried to use {move} but only has {player_energy}/{energy_cost} MP")
                return
            
            # Deduct energy BEFORE the attack
            player_energy = max(0, player_energy - energy_cost)
            print(f"Player used {move}: Cost={energy_cost} MP, Remaining={player_energy}/{max_player_energy} MP")
            
            # CREATE ATTACK ANIMATION
            player_pos = (center_x - 400, 250)
            enemy_pos = (center_x + 250, 250)

            # Try special animation first
            special_anim = create_special_animation(
                move, move_data,
                player_pos[0], player_pos[1],
                enemy_pos[0], enemy_pos[1]
            )

            if special_anim:
                animation_manager.add_animation(special_anim)
            else:
                animation = create_animation_for_move(
                    move, move_data,
                    player_pos[0], player_pos[1],
                    enemy_pos[0], enemy_pos[1],
                    character_name=player_name
                )
                animation_manager.add_animation(animation)

            # Calculate and apply damage
            damage, effectiveness, missed = calculate_damage_with_time(move_data, player, enemy_data, weather, day_night, action_messages)
            if missed:
                action_messages.append({"text": f"{player_name}'s {move} missed!", "color": RED})
                floating_texts.append(FloatingText("MISS!", center_x + 250, 230, RED))
            else:
                enemy_hp = max(enemy_hp - damage, 0)
                effect_text, effect_color = get_effectiveness_text(effectiveness)
                
                action_messages.append({
                    "text": f"{player_name} used {move}! Dealt {damage} damage.", 
                    "color": WHITE
                })
                
                damage_color = GREEN if effectiveness > 1.0 else RED if effectiveness < 1.0 else WHITE
                floating_texts.append(FloatingText(f"-{damage}", center_x + 250, 210, damage_color))
                if effect_text:
                    action_messages.append({"text": effect_text, "color": effect_color})
                
                if damage > 25 or effectiveness > 1.5:
                    shake_intensity = min(10, damage // 3)
                    shake_duration = 300
                    
                    for _ in range(15):
                        px = center_x + 280 + random.randint(-20, 20)
                        py = 210 + random.randint(-20, 20)
                        vx = random.uniform(-3, 3)
                        vy = random.uniform(-3, 3)
                        particles.append(Particle(px, py, damage_color, vx, vy, 800))
        
        enemy_ai.record_player_move(
            move, 
            player_hp_ratio, 
            player_energy_ratio,
            our_last_move,
            game_phase
        )
        
        turn_count += 1
        
        # Enemy turn
        if enemy_hp > 0:
            enemy_ai.current_energy = enemy_energy
            enemy_ai.player_energy_ratio = player_energy / max_player_energy
            
            enemy_move_name, enemy_move_data = enemy_ai.choose_move(
                player["types"], player_hp, max_player_hp, 
                enemy_hp, max_enemy_hp, weather
            )
            
            if enemy_move_name == "Skip Turn":
                mp_regen = enemy_move_data.get("mp_regeneration", 0)
                enemy_energy = min(max_enemy_energy, enemy_energy + mp_regen)
                action_messages.append({
                    "text": f"{enemy_name} skipped their turn and regenerated {mp_regen} MP!", 
                    "color": CYAN
                })
                
                floating_texts.append(FloatingText(f"+{mp_regen} MP", center_x + 250, 190, CYAN))
                
                for _ in range(10):
                    px = center_x + 250 + random.randint(-30, 30)
                    py = 230 + random.randint(-30, 30)
                    vx = random.uniform(-2, 2)
                    vy = random.uniform(-4, -1)
                    particles.append(Particle(px, py, CYAN, vx, vy, 1000))
            else:
                enemy_energy_cost = enemy_move_data.get("energy_cost", 0)
                
                if enemy_energy >= enemy_energy_cost:
                    enemy_energy = max(0, enemy_energy - enemy_energy_cost)
                    print(f"Enemy used {enemy_move_name}: Cost={enemy_energy_cost} MP, Remaining={enemy_energy}/{max_enemy_energy} MP")
                    
                    enemy_pos = (center_x + 250, 250)
                    player_pos = (center_x - 400, 250)
                    # Try special animation for enemy
                    enemy_special_anim = create_special_animation(
                        enemy_move_name, enemy_move_data,
                        enemy_pos[0], enemy_pos[1],
                        player_pos[0], player_pos[1]
                    )

                    if enemy_special_anim:
                        animation_manager.add_animation(enemy_special_anim)
                    else:
                        enemy_animation = create_animation_for_move(
                            enemy_move_name, enemy_move_data,
                            enemy_pos[0], enemy_pos[1],
                            player_pos[0], player_pos[1],
                            character_name=enemy_name
                        )
                        animation_manager.add_animation(enemy_animation)
                    
                    enemy_damage, enemy_effectiveness, enemy_missed = calculate_damage_with_time(enemy_move_data, enemy_data, player, weather, day_night, action_messages)
                    if enemy_missed:
                        action_messages.append({"text": f"{enemy_name}'s {enemy_move_name} missed!", "color": RED})
                        floating_texts.append(FloatingText("MISS!", center_x - 400, 230, RED))
                    else:
                        player_hp = max(player_hp - enemy_damage, 0)
                        enemy_effect_text, enemy_effect_color = get_effectiveness_text(enemy_effectiveness)
                        
                        action_messages.append({
                            "text": f"{enemy_name} used {enemy_move_name}! Dealt {enemy_damage} damage.", 
                            "color": WHITE
                        })
                        
                        if hasattr(enemy_ai, 'last_prediction') and enemy_ai.last_prediction:
                            prediction_result = "correctly" if enemy_ai.last_prediction == move else "incorrectly"
                            if game_settings.get("show_ai_predictions", False):
                                action_messages.append({
                                    "text": f"AI {prediction_result} predicted your {move}!", 
                                    "color": GREEN if prediction_result == "correctly" else ORANGE
                                })
                        
                        damage_color = RED if enemy_effectiveness > 1.0 else GREEN if enemy_effectiveness < 1.0 else WHITE
                        floating_texts.append(FloatingText(f"-{enemy_damage}", center_x - 400, 210, damage_color))
                        if enemy_effect_text:
                            action_messages.append({"text": enemy_effect_text, "color": enemy_effect_color})
                        
                        if enemy_damage > 25:
                            shake_intensity = min(8, enemy_damage // 4)
                            shake_duration = 250
                else:
                    action_messages.append({"text": f"{enemy_name} doesn't have enough MP!", "color": RED})
        
        # Energy regeneration at end of turn
        old_player_energy = player_energy
        old_enemy_energy = enemy_energy
        player_energy = min(max_player_energy, player_energy + player_energy_regen)
        enemy_energy = min(max_enemy_energy, enemy_energy + enemy_energy_regen)
        print(f"Turn end regen: Player {old_player_energy}->{player_energy} (+{player_energy_regen}), Enemy {old_enemy_energy}->{enemy_energy} (+{enemy_energy_regen})")
        
        player_battle_stats.update({
            "current_hp": player_hp,
            "max_hp": max_player_hp,
            "current_mp": player_energy,
            "max_mp": max_player_energy
        })
        
        weather_changed = weather.update_turn()
        if weather_changed:
            weather_msg = weather.weather_types[weather.current_weather]["message"]
            action_messages.append({"text": weather_msg, "color": CYAN})
            weather_effects.set_weather(weather.current_weather)
    
    while running:
        dt = CLOCK.get_time()
        battle_timer += dt
        # Periodic auto-save every 5 minutes
        current_time = pygame.time.get_ticks()
        if current_time - last_save_time >= SAVE_INTERVAL:
            try:
                save_system.update_inventory(player_inventory.items)
                print(f"Auto-saved at {time.strftime('%H:%M:%S')}")
                last_save_time = current_time
            except Exception as e:
                print(f"Auto-save failed: {e}")
        weather_effects.update(dt)
        
        shake_x = shake_y = 0
        if shake_duration > 0:
            shake_x = random.randint(-shake_intensity, shake_intensity)
            shake_y = random.randint(-shake_intensity, shake_intensity)
            shake_duration -= dt
        
        SCREEN.blit(background, (shake_x, shake_y))
        weather_effects.draw(SCREEN)
        
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        alpha = int(140 + 20 * math.sin(battle_timer * 0.003))
        overlay.fill((*LIGHT_GRAY[:3], alpha))
        SCREEN.blit(overlay, (0, 0))
        
        player_bounce = int(5 * math.sin(battle_timer * 0.005))
        enemy_bounce = int(5 * math.cos(battle_timer * 0.005))
        
        weather_info = weather.get_weather_info()
        weather_rect = pygame.Rect(center_x - 250, 10, 500, 70)
        
        weather_surface = pygame.Surface((500, 70))
        base_color = weather_info["color"]
        for i in range(70):
            t = i / 70
            color = tuple(int(base_color[j] * (0.8 + 0.2 * t)) for j in range(3))
            pygame.draw.line(weather_surface, color, (0, i), (500, i))
        SCREEN.blit(weather_surface, weather_rect.topleft)
        pygame.draw.rect(SCREEN, BLACK, weather_rect, 3)
        
        weather_text = f"Weather: {weather_info['name']} ({weather_info['duration']} turns left)"
        weather_render = FONT.render(weather_text, True, BLACK)
        weather_text_rect = weather_render.get_rect(x=weather_rect.x + 50, y=weather_rect.y + 8)
        SCREEN.blit(weather_render, weather_text_rect)
        
        # Enhanced day/night panel with custom icon
        phase_info = day_night.get_phase_info()
        time_rect = pygame.Rect(center_x - 250, 90, 500, 60)
        
        # Use the enhanced drawing method if available
        if hasattr(day_night, 'draw_sky_overlay'):
            day_night.draw_sky_overlay(SCREEN, alpha=60)
            day_night.update_animation(dt)
            
            # Optional: Draw atmospheric overlay (subtle tint based on time)
            if hasattr(day_night, 'draw_sky_overlay'):
                day_night.draw_sky_overlay(SCREEN, alpha=40)
            
            # Draw weather panel (your existing code)
            phase_info = day_night.get_phase_info()
            weather_info = weather.get_weather_info()
            weather_rect = pygame.Rect(center_x - 250, 10, 500, 70)
            
            weather_surface = pygame.Surface((500, 70))
            base_color = weather_info["color"]
            for i in range(70):
                t = i / 70
                color = tuple(int(base_color[j] * (0.8 + 0.2 * t)) for j in range(3))
                pygame.draw.line(weather_surface, color, (0, i), (500, i))
            SCREEN.blit(weather_surface, weather_rect.topleft)
            pygame.draw.rect(SCREEN, BLACK, weather_rect, 3)
            
            weather_text = f"Weather: {weather_info['name']} ({weather_info['duration']} turns left)"
            weather_render = FONT.render(weather_text, True, BLACK)
            weather_text_rect = weather_render.get_rect(x=weather_rect.x + 50, y=weather_rect.y + 8)
            SCREEN.blit(weather_render, weather_text_rect)
            
            boost_text = f"Boosts {weather_info['boosted_types']} by {weather_info['boost_percent']}%"
            boost_render = SMALL_FONT.render(boost_text, True, BLACK)
            boost_text_rect = boost_render.get_rect(x=weather_rect.x + 50, y=weather_rect.y + 35)
            SCREEN.blit(boost_render, boost_text_rect)
            
            # Draw enhanced time panel
            time_rect = pygame.Rect(center_x - 250, 90, 500, 60)
            
            if hasattr(day_night, 'draw_time_panel_enhanced'):
                # Use the beautiful enhanced panel with custom icon
                day_night.draw_time_panel_enhanced(
                    SCREEN, 
                    time_rect.x, time_rect.y, 
                    time_rect.width, time_rect.height,
                    FONT, SMALL_FONT
                )
            else:
                # Fallback to simple panel
                time_surface = pygame.Surface((500, 60))
                base_color = phase_info["color"]
                for i in range(60):
                    t = i / 60
                    color = tuple(int(base_color[j] * (0.8 + 0.2 * t)) for j in range(3))
                    pygame.draw.line(time_surface, color, (0, i), (500, i))
                SCREEN.blit(time_surface, time_rect.topleft)
                pygame.draw.rect(SCREEN, BLACK, time_rect, 3)
                
                # Text without icon
                time_text = f"Time: {phase_info['name']}"
                time_render = FONT.render(time_text, True, BLACK)
                time_text_rect = time_render.get_rect(x=time_rect.x + 50, y=time_rect.y + 8)
                SCREEN.blit(time_render, time_text_rect)
                
                desc_render = SMALL_FONT.render(phase_info['description'], True, BLACK)
                desc_text_rect = desc_render.get_rect(x=time_rect.x + 50, y=time_rect.y + 35)
                SCREEN.blit(desc_render, desc_text_rect)
        
        boost_text = f"Boosts {weather_info['boosted_types']} by {weather_info['boost_percent']}%"
        boost_render = SMALL_FONT.render(boost_text, True, BLACK)
        boost_text_rect = boost_render.get_rect(x=weather_rect.x + 50, y=weather_rect.y + 35)
        SCREEN.blit(boost_render, boost_text_rect)
        
        player_battle_stats.update({
            "current_hp": player_hp,
            "max_hp": max_player_hp,
            "current_mp": player_energy,
            "max_mp": max_player_energy
        })
        
        # ============= PLAYER DISPLAY =============
        draw_text_with_shadow(f" {player_name}", center_x - 650, 90, BLACK, BIG_FONT)
        
        # Add player type text (like enemy has)
        player_type_text = " / ".join(player['types'])
        draw_text_with_shadow(f"Type: {player_type_text}", center_x - 650, 135, DARK_GRAY, FONT)
        
        # Health and energy bars
        draw_animated_health_bar(center_x - 650, 170, player_hp, max_player_hp, animate_time=battle_timer)
        draw_energy_bar(center_x - 650, 200, player_energy, max_player_energy)
        
        # Display permanent boosts from all battles
        display_info = get_character_display_info(player_name, player.get("_original_hp", player["hp"]), 
                                                player.get("_original_max_energy", max_player_energy))
        if display_info["has_boosts"]:
            boost_text = f"Permanent: +{display_info['hp_boost']} HP"
            draw_text_with_shadow(boost_text, center_x - 650, 225, GOLD, SMALL_FONT)
            forever_text = "(FOREVER)"
            draw_text_with_shadow(forever_text, center_x - 650, 245, PURPLE, SMALL_FONT)
        
        # Initialize boost_y based on whether permanent boosts are shown
        boost_y = 265 if display_info["has_boosts"] else 225
        
        # Temporary boosts
        if player["temp_boosts"]:
            for stat, boost in player["temp_boosts"].items():
                if boost != 0:
                    boost_text = f"{stat.title()}: +{boost}"
                    boost_color = GREEN if boost > 0 else RED
                    draw_text_with_shadow(boost_text, center_x - 650, boost_y, boost_color, SMALL_FONT)
                    boost_y += 15
        
        # Player sprite
        player_sprite_pos = (center_x - 400, 230 + player_bounce + shake_y)
        SCREEN.blit(battle_sprites[player_name], player_sprite_pos)
        
        # Player stats display
        draw_text_with_shadow(f"ATK: {player['attack']}", center_x - 650, 330, DARK_BLUE, SMALL_FONT)
        draw_text_with_shadow(f"DEF: {player['defense']}", center_x - 650, 350, DARK_GREEN, SMALL_FONT)
        draw_text_with_shadow(f"SP.A: {player['special_attack']}", center_x - 550, 330, PURPLE, SMALL_FONT)
        draw_text_with_shadow(f"SP.D: {player['special_defense']}", center_x - 550, 350, ORANGE, SMALL_FONT)
        draw_text_with_shadow(f"SPD: {player['speed']}", center_x - 450, 330, PURPLE, SMALL_FONT)
        
        # ============= ENEMY DISPLAY  =============
        draw_text_with_shadow(f" {enemy_name}", center_x + 400, 90, BLACK, BIG_FONT)
        
        # Enemy type text
        enemy_type_text = " / ".join(enemy_data['types'])
        draw_text_with_shadow(f"Type: {enemy_type_text}", center_x + 400, 135, DARK_GRAY, FONT)
        
        # Health and energy bars
        draw_animated_health_bar(center_x + 400, 170, enemy_hp, max_enemy_hp, animate_time=battle_timer)
        draw_energy_bar(center_x + 400, 200, enemy_energy, max_enemy_energy)
        
        # Temporary boosts
        if enemy_data["temp_boosts"]:
            boost_y = 225
            for stat, boost in enemy_data["temp_boosts"].items():
                if boost != 0:
                    boost_text = f"{stat.title()}: +{boost}"
                    boost_color = GREEN if boost > 0 else RED
                    draw_text_with_shadow(boost_text, center_x + 400, boost_y, boost_color, SMALL_FONT)
                    boost_y += 15
        
        # Enemy sprite
        enemy_sprite_pos = (center_x + 400, 230 + enemy_bounce + shake_y)
        SCREEN.blit(battle_sprites[enemy_name], enemy_sprite_pos)
        
        # Enemy stats display
        draw_text_with_shadow(f"ATK: {enemy_data['attack']}", center_x + 400, 330, DARK_BLUE, SMALL_FONT)
        draw_text_with_shadow(f"DEF: {enemy_data['defense']}", center_x + 400, 350, DARK_GREEN, SMALL_FONT)
        draw_text_with_shadow(f"SP.A: {enemy_data['special_attack']}", center_x + 500, 330, PURPLE, SMALL_FONT)
        draw_text_with_shadow(f"SP.D: {enemy_data['special_defense']}", center_x + 500, 350, ORANGE, SMALL_FONT)
        draw_text_with_shadow(f"SPD: {enemy_data['speed']}", center_x + 600, 330, PURPLE, SMALL_FONT)
        
        if game_settings.get("show_ai_predictions", False):
            stats = enemy_ai.get_prediction_stats()
            if stats["predictions_made"] > 0:
                pred_text = f"AI Accuracy: {stats['accuracy']:.1%} | Aggression: {stats['player_aggression']:.1f}"
                draw_text_with_shadow(pred_text, 50, screen_height - 250, PURPLE, SMALL_FONT)
                
                if hasattr(enemy_ai, 'last_prediction') and enemy_ai.last_prediction:
                    pred_move_text = f"AI Predicts: {enemy_ai.last_prediction}"
                    draw_text_with_shadow(pred_move_text, 50, screen_height - 230, CYAN, SMALL_FONT)
                else:
                    draw_text_with_shadow("AI Predicts: Analyzing...", 50, screen_height - 230, GRAY, SMALL_FONT)
            else:
                draw_text_with_shadow("AI Learning: Gathering data...", 50, screen_height - 250, YELLOW, SMALL_FONT)
                draw_text_with_shadow("Make a few moves to see predictions", 50, screen_height - 230, GRAY, SMALL_FONT)
        
        move_bg = pygame.Surface((screen_width, 450), pygame.SRCALPHA)
        move_bg.fill((255, 255, 255, 200))
        SCREEN.blit(move_bg, (0, 380))
        draw_text_with_shadow("Choose Your Action (1-7 keys or click)", center_x - 300, 400, BLACK, BIG_FONT)
        buttons = []
        mouse_pos = pygame.mouse.get_pos()
        
        buttons = []
        mouse_pos = pygame.mouse.get_pos()
        
        # Move buttons - now supporting 5 moves (4 regular + 1 special)
        buttons = []
        mouse_pos = pygame.mouse.get_pos()

        # First row: 4 moves
        for i, move in enumerate(move_names):
            if i >= 5:  # Now we support 5 moves
                break
            
            if i < 4:  # First 4 moves in first row
                x = center_x - 640 + i * 320
                y = 460
                width = 300
                height = 70
            else:  # 5th move (special/ultimate) - centered below, slightly bigger
                x = center_x - 200  # Centered
                y = 545  # Below first row
                width = 400  # Slightly wider than regular moves
                height = 75  # Slightly taller than regular moves
            
            rect = pygame.Rect(x, y, width, height)
            buttons.append((rect, move, "move"))
            hover = rect.collidepoint(mouse_pos)
            move_data = player["moves"][move]
            energy_cost = move_data.get("energy_cost", 0)
            can_use = player_energy >= energy_cost
            
            # Build button text
            if i < 4:
                button_text = f"{i+1}. {move} | {move_data['power']} DMG | {energy_cost} MP"
            else:
                # Special formatting for 5th move
                if move_data.get("is_ultimate"):
                    button_text = f"5. [ULTIMATE] {move.upper()} | {move_data['power']} DMG | {energy_cost} MP"
                elif move_data.get("is_special"):
                    button_text = f"5. [SPECIAL] {move.upper()} | {move_data['power']} DMG | {energy_cost} MP"
                else:
                    button_text = f"5. {move} | {move_data['power']} DMG | {energy_cost} MP"
            
            if not can_use:
                button_text += " (Not enough MP!)"
            
            # Use enhanced drawing function (same font size for all moves)
            draw_enhanced_move_button(button_text, rect, move_data, can_use, hover, 
                                    SMALL_FONT, SCREEN, battle_timer)
        
        # Skip Turn button - moved up
        skip_rect = pygame.Rect(center_x - 320, 630, 300, 70)
        buttons.append((skip_rect, "Skip Turn", "move"))
        skip_hover = skip_rect.collidepoint(mouse_pos)
        skip_turn_data = get_skip_turn_move(player)
        mp_regen = skip_turn_data.get("mp_regeneration", 0)
        button_text = f"6. Skip Turn | Regen {mp_regen} MP"
        draw_gradient_button(button_text, skip_rect, CYAN, 
                            tuple(max(0, c - 40) for c in CYAN), skip_hover, SMALL_FONT)

        # Items button - moved up
        items_rect = pygame.Rect(center_x + 20, 630, 300, 70)
        buttons.append((items_rect, "Items", "items"))
        items_hover = items_rect.collidepoint(mouse_pos)
        items_available = len(player_inventory.items) > 0
        if items_available:
            draw_gradient_button("7. ITEMS", items_rect, GOLD, (200, 150, 0), 
                                items_hover, SMALL_FONT)
        else:
            draw_gradient_button("7. ITEMS (Empty)", items_rect, DARK_GRAY, GRAY, 
                                False, SMALL_FONT)
        
        log_bg = pygame.Surface((800, 120), pygame.SRCALPHA)
        log_bg.fill((0, 0, 0, 150))
        SCREEN.blit(log_bg, (center_x - 400, 700))
        for i, msg in enumerate(action_messages[-4:]):
            color = msg.get("color", WHITE)
            draw_text_with_shadow(msg["text"], center_x - 380, 710 + i * 25, color, SMALL_FONT, 1)
        
        menu_rect = pygame.Rect(50, screen_height - 130, 180, 50)
        settings_rect = pygame.Rect(50, screen_height - 70, 180, 50)
        draw_gradient_button("MENU", menu_rect, DARK_GRAY, GRAY, menu_rect.collidepoint(mouse_pos))
        draw_gradient_button("SETTINGS", settings_rect, DARK_BLUE, BLUE, settings_rect.collidepoint(mouse_pos))
        
        # Draw floating texts
        floating_texts = [text for text in floating_texts if text.update(dt)]
        for text in floating_texts:
            text.draw(SCREEN)
        
        # Draw particles
        particles = [particle for particle in particles if particle.update(dt)]
        for particle in particles:
            particle.draw(SCREEN)
        
        # Draw item particles
        item_particles = [particle for particle in item_particles if particle.update(dt)]
        for particle in item_particles:
            particle.draw(SCREEN)
        
        # Update and draw attack animations
        animation_manager.update(dt)
        animation_manager.draw(SCREEN)
        
        if show_item_menu:
            category_buttons, item_buttons, close_button = draw_item_menu(player_inventory, current_item_category)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                pygame.mixer.stop()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            elif event.type == pygame.MOUSEWHEEL:
                if show_item_menu:
                    handle_item_menu_scroll(event.y)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_item_menu:
                        show_item_menu = False
                    elif show_battle_settings:
                        show_battle_settings = False
                    else:
                        show_exit_menu = not show_exit_menu
                elif not show_exit_menu and not show_battle_settings and not show_item_menu:
                    if event.key == pygame.K_1 and len(move_names) >= 1:
                        execute_move(move_names[0])
                    elif event.key == pygame.K_2 and len(move_names) >= 2:
                        execute_move(move_names[1])
                    elif event.key == pygame.K_3 and len(move_names) >= 3:
                        execute_move(move_names[2])
                    if event.key == pygame.K_4 and len(move_names) >= 4:
                        execute_move(move_names[3])
                    elif event.key == pygame.K_5 and len(move_names) >= 5:  # NEW: 5th move
                        execute_move(move_names[4])
                    elif event.key == pygame.K_6:  # Skip is now 6
                        execute_move("Skip Turn")
                    elif event.key == pygame.K_7:  # Items is now 7
                        if len(player_inventory.items) > 0:
                            show_item_menu = True
                            reset_item_scroll()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if show_item_menu:
                    if close_button.collidepoint((mx, my)):
                        show_item_menu = False
                    else:
                        for cat_rect, category in category_buttons:
                            if cat_rect.collidepoint((mx, my)):
                                current_item_category = category
                                reset_item_scroll()
                                break
                        
                        for item_rect, item in item_buttons:
                            if item_rect.collidepoint((mx, my)):
                                use_item(item, player_battle_stats)
                                show_item_menu = False
                                break
                elif show_exit_menu:
                    leave_battle = pygame.Rect(center_x - 220, 340, 200, 60)
                    quit_game = pygame.Rect(center_x + 20, 340, 200, 60)
                    resume_game = pygame.Rect(center_x - 100, 420, 200, 50)
                    
                    if leave_battle.collidepoint((mx, my)):
                        if title_music_loaded:
                            play_title_music()
                        return
                    elif quit_game.collidepoint((mx, my)):
                        pygame.quit()
                        sys.exit()
                    elif resume_game.collidepoint((mx, my)):
                        show_exit_menu = False
                elif show_battle_settings:
                    y_pos = 270
                    play_fight_btn = pygame.Rect(400, y_pos, 150, 40)
                    stop_music_btn = pygame.Rect(570, y_pos, 150, 40)
                    
                    current_time = pygame.time.get_ticks()
                    test_available = current_time >= test_volume_cooldown
                    test_fight_btn = pygame.Rect(740, y_pos, 150, 40)
                    
                    y_pos += 60
                    ai_toggle_btn = pygame.Rect(400, y_pos, 200, 40)
                    close_settings_btn = pygame.Rect(760, 850, 200, 60)
                    
                    if close_settings_btn.collidepoint((mx, my)):
                        show_battle_settings = False
                    elif play_fight_btn.collidepoint((mx, my)):
                        print("Manual fight music start requested")
                        music_status = get_music_status()
                        if music_status['fight_loaded']:
                            if play_fight_music():
                                print("Fight music restarted")
                            else:
                                print("Failed to restart fight music")
                        else:
                            print("Fight music not loaded - cannot play")
                    elif stop_music_btn.collidepoint((mx, my)):
                        print("Stopping all music")
                        stop_all_music()
                    elif test_fight_btn.collidepoint((mx, my)) and test_available:
                        print("Testing fight music volume")
                        test_fight_volume()
                        test_volume_cooldown = current_time + 3000
                    elif ai_toggle_btn.collidepoint((mx, my)):
                        current_setting = game_settings.get("show_ai_predictions", False)
                        game_settings["show_ai_predictions"] = not current_setting
                        print(f"AI predictions toggled to: {game_settings['show_ai_predictions']}")
                elif menu_rect.collidepoint((mx, my)):
                    show_exit_menu = not show_exit_menu
                elif settings_rect.collidepoint((mx, my)):
                    show_battle_settings = not show_battle_settings
                else:
                    for rect, action, action_type in buttons:
                        if rect.collidepoint((mx, my)):
                            if action_type == "move":
                                execute_move(action)
                            elif action_type == "items" and len(player_inventory.items) > 0:
                                show_item_menu = True
                                reset_item_scroll()
                            break
        
        if show_exit_menu:
            menu_surface = pygame.Surface((500, 300), pygame.SRCALPHA)
            menu_surface.fill((0, 0, 0, 200))
            SCREEN.blit(menu_surface, (center_x - 250, 250))
            pygame.draw.rect(SCREEN, WHITE, (center_x - 250, 250, 500, 300), 3)
            draw_text_with_shadow("BATTLE MENU", center_x - 100, 280, WHITE, BIG_FONT)
            leave_battle = pygame.Rect(center_x - 220, 340, 200, 60)
            quit_game = pygame.Rect(center_x + 20, 340, 200, 60)
            resume_game = pygame.Rect(center_x - 100, 420, 200, 50)
            draw_gradient_button("Leave Battle", leave_battle, DARK_RED, RED, 
                               leave_battle.collidepoint(mouse_pos), SMALL_FONT)
            draw_gradient_button("Quit Game", quit_game, DARK_RED, RED, 
                               quit_game.collidepoint(mouse_pos), SMALL_FONT)
            draw_gradient_button("Resume", resume_game, DARK_GREEN, GREEN, 
                               resume_game.collidepoint(mouse_pos), SMALL_FONT)
        
        if show_battle_settings:
            overlay = pygame.Surface((1920, 1080), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            SCREEN.blit(overlay, (0, 0))
            
            panel_rect = pygame.Rect(360, 150, 1200, 780)
            panel_surface = pygame.Surface((1200, 780))
            panel_surface.fill(LIGHT_GRAY)
            SCREEN.blit(panel_surface, panel_rect.topleft)
            pygame.draw.rect(SCREEN, BLACK, panel_rect, 4)
            
            draw_text_with_shadow("BATTLE SETTINGS", 760, 180, BLACK, BIG_FONT, 3)
            
            y_pos = 270
            play_fight_btn = pygame.Rect(400, y_pos, 150, 40)
            stop_music_btn = pygame.Rect(570, y_pos, 150, 40)
            
            current_time = pygame.time.get_ticks()
            test_available = current_time >= test_volume_cooldown
            test_fight_btn = pygame.Rect(740, y_pos, 150, 40)
            
            draw_gradient_button("Play Fight", play_fight_btn, DARK_BLUE, BLUE, 
                               play_fight_btn.collidepoint(mouse_pos), SMALL_FONT)
            draw_gradient_button("Stop Music", stop_music_btn, DARK_RED, RED, 
                               stop_music_btn.collidepoint(mouse_pos), SMALL_FONT)
            
            if test_available:
                draw_gradient_button("Test Volume", test_fight_btn, PURPLE, PINK, 
                                   test_fight_btn.collidepoint(mouse_pos), SMALL_FONT)
            else:
                cooldown_remaining = (test_volume_cooldown - current_time) / 1000.0
                draw_gradient_button(f"Wait {cooldown_remaining:.1f}s", test_fight_btn, DARK_GRAY, GRAY, 
                                   False, SMALL_FONT)
            
            y_pos += 60
            ai_toggle_btn = pygame.Rect(400, y_pos, 200, 40)
            ai_toggle_text = "Hide AI Info" if game_settings.get("show_ai_predictions", False) else "Show AI Info"
            draw_gradient_button(ai_toggle_text, ai_toggle_btn, PURPLE, PINK, 
                               ai_toggle_btn.collidepoint(mouse_pos), SMALL_FONT)
            
            y_pos += 80
            draw_text_with_shadow("Weather Effects Status:", 400, y_pos, BLACK, FONT)
            current_particles = len(weather_effects.particles)
            particle_text = f"Active Particles: {current_particles}"
            draw_text_with_shadow(particle_text, 400, y_pos + 25, BLUE, SMALL_FONT)
            fog_text = f"Fog Level: {int(weather_effects.fog_alpha)}/255"
            draw_text_with_shadow(fog_text, 400, y_pos + 45, GRAY, SMALL_FONT)
            effects_text = f"Current Effects: {weather.current_weather} Weather"
            draw_text_with_shadow(effects_text, 400, y_pos + 65, weather_info["color"], SMALL_FONT)
            
            y_pos += 120
            draw_text_with_shadow("AI Prediction System:", 400, y_pos, BLACK, FONT)
            ai_stats = enemy_ai.get_prediction_stats()
            if ai_stats["predictions_made"] > 0:
                accuracy_text = f"Prediction Accuracy: {ai_stats['accuracy']:.1%}"
                predictions_text = f"Total Predictions: {ai_stats['predictions_made']}"
                aggression_text = f"Player Aggression: {ai_stats['player_aggression']:.2f}"
                draw_text_with_shadow(accuracy_text, 400, y_pos + 25, GREEN if ai_stats['accuracy'] > 0.5 else RED, SMALL_FONT)
                draw_text_with_shadow(predictions_text, 400, y_pos + 45, BLUE, SMALL_FONT)
                draw_text_with_shadow(aggression_text, 400, y_pos + 65, ORANGE, SMALL_FONT)
            else:
                draw_text_with_shadow("Learning player patterns...", 400, y_pos + 25, GRAY, SMALL_FONT)
            
            y_pos += 120
            draw_text_with_shadow("Day/Night Cycle:", 400, y_pos, BLACK, FONT)
            
            phase_info = day_night.get_phase_info()
            phase_text = f"Current Time: {phase_info['name']} {phase_info['icon']}"
            draw_text_with_shadow(phase_text, 400, y_pos + 25, phase_info['color'], SMALL_FONT)
            
            draw_text_with_shadow(phase_info['description'], 400, y_pos + 45, DARK_GRAY, SMALL_FONT)
            
            # Show boosted types
            boosted_text = f"Boosted Types: {', '.join(phase_info['boosted_types'])}"
            draw_text_with_shadow(boosted_text, 400, y_pos + 65, phase_info['color'], SMALL_FONT)
            
            # Show active bonuses
            bonus_y = y_pos + 90
            draw_text_with_shadow("Active Bonuses:", 400, bonus_y, BLACK, SMALL_FONT)
            bonus_list_y = bonus_y + 20
            for stat, multiplier in phase_info['bonuses'].items():
                if multiplier != 1.0:
                    bonus_pct = int((multiplier - 1.0) * 100)
                    bonus_text = f"• {stat.replace('_', ' ').title()}: +{bonus_pct}%"
                    draw_text_with_shadow(bonus_text, 410, bonus_list_y, 
                                        phase_info['color'], SMALL_FONT)
                    bonus_list_y += 18

            
            y_pos += 120
            draw_text_with_shadow("Music System Status:", 400, y_pos, BLACK, FONT)
            fight_status = "Loaded & Ready" if fight_music_loaded else "Not Found"
            current_status = f"Currently Playing: {current_music_type.title() if current_music_type else 'None'}"
            fight_color = GREEN if fight_music_loaded else RED
            current_color = BLUE if current_music_type else GRAY
            draw_text_with_shadow(f"Fight Music (fight_music.wav): {fight_status}", 400, y_pos + 35, fight_color, SMALL_FONT)
            draw_text_with_shadow(current_status, 400, y_pos + 60, current_color, SMALL_FONT)
            
            close_settings_btn = pygame.Rect(760, 850, 200, 60)
            draw_gradient_button("CLOSE", close_settings_btn, DARK_BLUE, BLUE, 
                               close_settings_btn.collidepoint(mouse_pos), FONT)
        
        if player_hp <= 0:
            defeat_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            defeat_surface.fill((200, 0, 0, 100))
            SCREEN.blit(defeat_surface, (0, 0))
            draw_text_with_shadow("DEFEAT!", center_x - 76.5, 400, RED, BIG_FONT, 3)
            draw_text_with_shadow("Press ESC to return to character select", center_x - 200, 450, WHITE, FONT, 2)
            
            if game_settings.get("show_ai_predictions", False):
                final_stats = enemy_ai.get_prediction_stats()
                if final_stats["predictions_made"] > 0:
                    stats_text = f"Final AI Accuracy: {final_stats['accuracy']:.1%} ({final_stats['predictions_made']} predictions)"
                    draw_text_with_shadow(stats_text, center_x - 150, 500, PURPLE, SMALL_FONT, 2)
            
            # UPDATE BATTLE STATISTICS - DEFEAT
            try:
                save_system.update_battle_stats(won=False)
                save_system.update_inventory(player_inventory.items)
                print("Battle defeat recorded to save file!")
            except Exception as e:
                print(f"Error saving battle result: {e}")
            
            draw_real_time_clock(game_settings.get("show_clock", True))
            pygame.display.flip()
            
            print("Battle ended in defeat - returning to title music")
            title_status = get_music_status()
            if title_status['title_loaded']:
                if play_title_music():
                    print("Title music restored")
                else:
                    print("Failed to restore title music")
            wait_for_key()
            return
        elif enemy_hp <= 0:
            victory_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            victory_surface.fill((0, 200, 0, 100))
            SCREEN.blit(victory_surface, (0, 0))
            
            for _ in range(30):
                px = random.randint(0, screen_width)
                py = random.randint(0, screen_height)
                particles.append(Particle(px, py, GOLD, random.uniform(-2, 2), random.uniform(-2, 2), 2000))
            
            reward_item = get_random_item_drop("medium")
            if reward_item:
                player_inventory.add_item(reward_item.name, 1)
                item_color = reward_item.get_rarity_color()
                draw_text_with_shadow("VICTORY!", center_x - 76.5, 400, GOLD, BIG_FONT, 3)
                item_text = f"You found a {reward_item.name}!"
                draw_text_with_shadow(item_text, center_x - 120, 450, item_color, FONT, 2)
                rarity_text = f"[{reward_item.rarity}]"
                item_name_width = FONT.size(item_text)[0]
                rarity_width = SMALL_FONT.size(rarity_text)[0]
                rarity_x = (center_x - 120) + (item_name_width - rarity_width) // 2
                draw_text_with_shadow(rarity_text, rarity_x, 480, item_color, SMALL_FONT, 1)
            else:
                player_inventory.add_item("Healing Potion", 1)
                draw_text_with_shadow("VICTORY!", center_x - 76.5, 400, GOLD, BIG_FONT, 3)
                draw_text_with_shadow("You found a Healing Potion!", center_x - 120, 450, GREEN, FONT, 2)
            
            if game_settings.get("show_ai_predictions", False):
                final_stats = enemy_ai.get_prediction_stats()
                if final_stats["predictions_made"] > 0:
                    stats_text = f"Final AI Accuracy: {final_stats['accuracy']:.1%} ({final_stats['predictions_made']} predictions)"
                    draw_text_with_shadow(stats_text, center_x - 150, 520, PURPLE, SMALL_FONT, 2)
            
            # UPDATE BATTLE STATISTICS - VICTORY
            try:
                save_system.update_battle_stats(won=True)
                save_system.update_inventory(player_inventory.items)
                print("Battle victory recorded to save file!")
            except Exception as e:
                print(f"Error saving battle result: {e}")
            
            print("Battle ended in victory - returning to title music")
            title_status = get_music_status()
            if title_status['title_loaded']:
                if play_title_music():
                    print("Title music restored")
                else:
                    print("Failed to restore title music")
            
            draw_real_time_clock(game_settings.get("show_clock", True))
            pygame.display.flip()
            wait_for_key()
            return
        
        draw_real_time_clock(game_settings.get("show_clock", True))
        pygame.display.flip()
        CLOCK.tick(60)