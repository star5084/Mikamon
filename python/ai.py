import random
from python.type_effectiveness import get_type_effectiveness
from collections import defaultdict, Counter

class PredictionAI:
    def __init__(self, character_data, difficulty="Normal"):
        self.character = character_data
        self.difficulty = difficulty
        self.turn_count = 0
        self.last_effectiveness = {}
        self.move_history = []
        self.energy_management_strategy = "balanced"
        
        # New prediction system attributes
        self.player_move_history = []  # Track player's moves
        self.player_patterns = {
            'move_sequences': defaultdict(list),  # What moves follow other moves
            'situational_preferences': {  # What moves used in specific situations
                'low_hp': defaultdict(int),
                'high_hp': defaultdict(int),
                'low_energy': defaultdict(int),
                'high_energy': defaultdict(int)
            },
            'type_preferences': defaultdict(int),  # Preferred move types
            'timing_patterns': defaultdict(int),   # Early/mid/late game preferences
            'counter_history': defaultdict(int),   # How player responds to our moves
            'repetition_tendency': 0,              # How often player repeats moves
            'aggression_level': 0.5                # Player's aggression (0=defensive, 1=aggressive)
        }
        
        # Prediction confidence tracking
        self.prediction_accuracy = {'correct': 0, 'total': 0}
        self.last_prediction = None
        
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
        
        # Update patterns
        self._update_patterns(move_name, player_hp_ratio, player_energy_ratio, 
                            our_last_move, game_phase)
        
        # Check prediction accuracy if we made one
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
        
        # Move sequences (what follows what)
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
        
        # Update aggression level based on move choice
        if move_name != "Skip Turn":
            move_data = self._get_player_move_data(move_name)
            if move_data:
                power = move_data.get('power', 0)
                energy_cost = move_data.get('energy_cost', 0)
                
                # High power or high energy cost suggests aggression
                aggression_indicator = (power / 50.0) + (energy_cost / 30.0)
                current_aggression = self.player_patterns['aggression_level']
                self.player_patterns['aggression_level'] = (current_aggression * 0.8 + 
                                                          min(aggression_indicator, 1.0) * 0.2)
        else:
            # Skip turn suggests defensive play
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
            # Low energy makes Skip Turn very likely
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
        
        # Find most likely move
        predicted_move = max(move_probabilities, key=move_probabilities.get)
        max_probability = move_probabilities[predicted_move]
        
        # Calculate confidence (0-1)
        confidence = min(1.0, max_probability / max(1.0, total_confidence))
        
        # Adjust confidence based on historical accuracy
        if self.prediction_accuracy['total'] > 5:
            accuracy_rate = self.prediction_accuracy['correct'] / self.prediction_accuracy['total']
            confidence *= (0.5 + accuracy_rate * 0.5)  # Scale by historical accuracy
        
        self.last_prediction = predicted_move
        return predicted_move, confidence
    
    def choose_counter_move(self, predicted_move, confidence, player_types, 
                          player_hp, max_player_hp, own_hp, max_own_hp, weather):
        """Choose a move to counter the predicted player move"""
        if not predicted_move or confidence < 0.3:
            # Fall back to normal AI behavior if prediction confidence is low
            return self.choose_move(player_types, player_hp, max_player_hp, 
                                  own_hp, max_own_hp, weather)
        
        current_energy = getattr(self, 'current_energy', self.character.get("max_energy", 100))
        moves = list(self.character["moves"].items())
        skip_turn_data = get_skip_turn_move(self.character)
        moves.append(("Skip Turn", skip_turn_data))
        
        counter_strategies = self._get_counter_strategies(predicted_move, player_types, weather)
        
        # Evaluate moves based on counter potential
        move_scores = {}
        for move_name, move_data in moves:
            energy_cost = move_data.get("energy_cost", 0)
            if current_energy < energy_cost:
                continue
                
            base_score = self._evaluate_attack_move(
                move_name, move_data, player_types, player_hp, max_player_hp,
                own_hp, max_own_hp, weather, current_energy, energy_cost
            )
            
            # Add counter bonus
            counter_bonus = 0
            for strategy, bonus in counter_strategies.items():
                if self._move_fits_strategy(move_name, move_data, strategy):
                    counter_bonus += bonus * confidence  # Scale by prediction confidence
            
            move_scores[move_name] = base_score + counter_bonus
        
        if not move_scores:
            return ("Skip Turn", skip_turn_data)
        
        # Add some randomness to prevent complete predictability
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
            # Player will regenerate energy - punish with strong attack
            strategies["high_damage"] = 40
            strategies["energy_efficient"] = 20
            
        else:
            predicted_move_data = self._get_player_move_data(predicted_move)
            if predicted_move_data:
                predicted_power = predicted_move_data.get('power', 0)
                predicted_type = predicted_move_data.get('type', 'Normal')
                predicted_effect = predicted_move_data.get('effect', '')
                
                # Counter high-damage moves with defensive strategies
                if predicted_power > 40:
                    strategies["defensive"] = 30
                    strategies["disable"] = 25
                
                # Counter based on type (use resistant types)
                for our_move_name, our_move_data in self.character["moves"].items():
                    our_type = our_move_data.get('type', 'Normal')
                    # If we can resist their attack type, prioritize it
                    resistance = get_type_effectiveness(predicted_type, our_type)
                    if resistance < 1.0:  # We resist their move type
                        strategies["type_resistant"] = 35
                
                # Counter special effects
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
            # This is handled in the counter strategy generation
            return True
        
        return False
    
    def _get_player_move_data(self, move_name):
        """Get move data for a player move (you'll need to implement this based on your game structure)"""
        # This would need to access the player's character data
        # For now, return None as placeholder
        return None
    
    def get_prediction_stats(self):
        """Get AI prediction statistics"""
        if self.prediction_accuracy['total'] == 0:
            return {"accuracy": 0.0, "predictions_made": 0}
        
        accuracy = self.prediction_accuracy['correct'] / self.prediction_accuracy['total']
        return {
            "accuracy": accuracy,
            "predictions_made": self.prediction_accuracy['total'],
            "player_aggression": self.player_patterns['aggression_level'],
            "repetition_tendency": self.player_patterns['repetition_tendency']
        }
    
    # Include all the existing methods from your current AI
    def choose_move(self, player_types, player_hp, max_player_hp, own_hp, max_own_hp, weather):
        """Enhanced move selection with prediction integration"""
        self.turn_count += 1
        
        # Get current game state
        player_hp_ratio = player_hp / max_player_hp
        player_energy_ratio = getattr(self, 'player_energy_ratio', 0.5)  # You'd need to pass this
        game_phase = "early" if self.turn_count < 5 else "mid" if self.turn_count < 10 else "late"
        
        # Try to predict player's next move
        predicted_move, confidence = self.predict_next_move(
            player_hp_ratio, player_energy_ratio, 
            self.move_history[-1] if self.move_history else None, 
            game_phase
        )
        
        # Use prediction-based strategy if confidence is high enough
        if predicted_move and confidence > 0.4:
            return self.choose_counter_move(
                predicted_move, confidence, player_types, 
                player_hp, max_player_hp, own_hp, max_own_hp, weather
            )
        else:
            # Fall back to existing AI logic
            moves = list(self.character["moves"].items())
            skip_turn_data = get_skip_turn_move(self.character)
            moves.append(("Skip Turn", skip_turn_data))
            
            current_energy = getattr(self, 'current_energy', self.character.get("max_energy", 100))
            max_energy = self.character.get("max_energy", 100)
            
            if self.difficulty == "Easy":
                available_moves = [(name, data) for name, data in moves 
                                 if current_energy >= data.get("energy_cost", 0)]
                return random.choice(available_moves) if available_moves else ("Skip Turn", skip_turn_data)
            
            move_scores = self._evaluate_all_moves(moves, player_types, player_hp, max_player_hp, 
                                                  own_hp, max_own_hp, weather, current_energy, max_energy)
            
            if not move_scores:
                return ("Skip Turn", skip_turn_data)
            
            strategy = self._determine_strategy(own_hp, max_own_hp, player_hp, max_player_hp, current_energy, max_energy)
            move_scores = self._apply_strategy_modifiers(move_scores, strategy, moves)
            
            randomness_factor = 5 if self.difficulty == "Hard" else 15
            for move_name in move_scores:
                move_scores[move_name] += random.uniform(-randomness_factor, randomness_factor)
            
            best_move = max(move_scores, key=move_scores.get)
            self._record_move(best_move)
            
            if best_move == "Skip Turn":
                return (best_move, skip_turn_data)
            else:
                return (best_move, self.character["moves"][best_move])

# Keep all your existing methods...
# (Include _evaluate_all_moves, _evaluate_skip_turn, _evaluate_attack_move, etc.)

def get_skip_turn_move(character_data):
    """Generate Skip Turn move data based on character's energy characteristics"""
    moves = character_data["moves"]
    energy_regen = character_data.get("energy_regen", 15)
    max_energy = character_data.get("max_energy", 100)
    
    base_regen = energy_regen
    
    if moves:
        min_cost = min(move["energy_cost"] for move in moves.values())
        bonus_regen = min(max_energy // 8, min_cost)
    else:
        bonus_regen = max_energy // 10
    
    total_regen = base_regen + bonus_regen
    
    return {
        "power": 0,
        "type": "Neutral", 
        "accuracy": 100,
        "effect": "skip_turn",
        "energy_cost": 0,
        "mp_regeneration": total_regen,
        "description": f"Skip turn to recover {total_regen} MP and plan next move"
    }