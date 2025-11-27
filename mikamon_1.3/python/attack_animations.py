"""
Attack Animation System - Fixed and Enhanced
Adds the missing AttackAnimationManager class and create_animation_for_move function
"""

import pygame
import random
import math

# Simple particle class for animations
class AnimationParticle:
    """Simple particle for attack animations"""
    def __init__(self, x, y, color, vx, vy, life=1000):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
    
    def update(self, dt):
        self.x += self.vx * dt * 0.06
        self.y += self.vy * dt * 0.06
        self.vy += 0.2  # Gravity
        self.life -= dt
        return self.life > 0
    
    def draw(self, surface):
        alpha = int(255 * (self.life / self.max_life))
        size = max(2, int(5 * (self.life / self.max_life)))
        
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*self.color, alpha), (size, size), size)
        surface.blit(particle_surf, (int(self.x - size), int(self.y - size)))


class BaseAnimation:
    """Base class for all attack animations"""
    def __init__(self, start_x, start_y, target_x, target_y, duration=800):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.duration = duration
        self.elapsed = 0
        self.finished = False
        self.particles = []
    
    def update(self, dt):
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.finished = True
        
        # Update particles
        self.particles = [p for p in self.particles if p.update(dt)]
        
        return not self.finished
    
    def draw(self, surface):
        # Draw particles
        for particle in self.particles:
            particle.draw(surface)
    
    def get_progress(self):
        """Returns animation progress from 0.0 to 1.0"""
        return min(1.0, self.elapsed / self.duration)


class ProjectileAnimation(BaseAnimation):
    """Generic projectile animation"""
    def __init__(self, start_x, start_y, target_x, target_y, color, power=50):
        super().__init__(start_x, start_y, target_x, target_y, duration=600)
        self.color = color
        self.power = power
    
    def update(self, dt):
        result = super().update(dt)
        
        progress = self.get_progress()
        
        # Spawn trail particles
        if progress < 0.8 and random.random() < 0.5:
            current_x = self.start_x + (self.target_x - self.start_x) * progress
            current_y = self.start_y + (self.target_y - self.start_y) * progress
            
            self.particles.append(AnimationParticle(
                current_x + random.uniform(-10, 10),
                current_y + random.uniform(-10, 10),
                self.color,
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                400
            ))
        
        # Impact explosion
        if progress >= 0.8 and progress < 0.85:
            for _ in range(15):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 8)
                self.particles.append(AnimationParticle(
                    self.target_x,
                    self.target_y,
                    self.color,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    600
                ))
        
        return result
    
    def draw(self, surface):
        super().draw(surface)
        
        progress = self.get_progress()
        
        if progress < 0.8:
            # Draw projectile
            current_x = self.start_x + (self.target_x - self.start_x) * (progress / 0.8)
            current_y = self.start_y + (self.target_y - self.start_y) * (progress / 0.8)
            
            # Glow effect
            for i in range(3):
                size = 15 - i * 4
                alpha = 150 - i * 40
                glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, alpha), (size, size), size)
                surface.blit(glow_surf, (int(current_x - size), int(current_y - size)))
            
            # Core
            pygame.draw.circle(surface, self.color, (int(current_x), int(current_y)), 8)
            pygame.draw.circle(surface, (255, 255, 255), (int(current_x), int(current_y)), 4)


class MeleeAnimation(BaseAnimation):
    """Generic melee attack animation"""
    def __init__(self, x, y, direction='right', color=(255, 200, 100), power=50):
        super().__init__(x, y, x, y, duration=500)
        self.x = x
        self.y = y
        self.direction = direction
        self.color = color
        self.power = power
    
    def update(self, dt):
        result = super().update(dt)
        
        progress = self.get_progress()
        
        # Impact particles
        if 0.4 < progress < 0.6 and random.random() < 0.7:
            offset_x = 30 if self.direction == 'right' else -30
            self.particles.append(AnimationParticle(
                self.x + offset_x + random.uniform(-20, 20),
                self.y + random.uniform(-20, 20),
                self.color,
                random.uniform(-3, 3),
                random.uniform(-4, -1),
                500
            ))
        
        return result
    
    def draw(self, surface):
        super().draw(surface)
        
        progress = self.get_progress()
        
        if progress < 0.6:
            # Draw swing arc
            arc_progress = progress / 0.6
            start_angle = -0.8 if self.direction == 'right' else 2.4
            end_angle = 0.8 if self.direction == 'right' else 4.0
            current_angle = start_angle + (end_angle - start_angle) * arc_progress
            
            # Arc effect
            radius = 70
            for i in range(2):
                thickness = 8 - i * 3
                alpha = int(200 * (1 - arc_progress) * (1 - i * 0.3))
                
                arc_surf = pygame.Surface((radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA)
                center = (radius + 10, radius + 10)
                
                # Draw arc segments
                steps = 20
                for step in range(steps):
                    angle1 = start_angle + (current_angle - start_angle) * (step / steps)
                    angle2 = start_angle + (current_angle - start_angle) * ((step + 1) / steps)
                    
                    x1 = center[0] + radius * math.cos(angle1)
                    y1 = center[1] + radius * math.sin(angle1)
                    x2 = center[0] + radius * math.cos(angle2)
                    y2 = center[1] + radius * math.sin(angle2)
                    
                    pygame.draw.line(arc_surf, (*self.color, alpha), (x1, y1), (x2, y2), thickness)
                
                surface.blit(arc_surf, (int(self.x - radius - 10), int(self.y - radius - 10)))


class AttackAnimationManager:
    """Manages all active attack animations"""
    def __init__(self):
        self.animations = []
    
    def add_animation(self, animation):
        """Add a new animation"""
        self.animations.append(animation)
    
    def update(self, dt):
        """Update all animations"""
        self.animations = [anim for anim in self.animations if anim.update(dt)]
    
    def draw(self, surface):
        """Draw all animations"""
        for anim in self.animations:
            anim.draw(surface)
    
    def has_active_animations(self):
        """Check if any animations are still playing"""
        return len(self.animations) > 0
    
    def clear(self):
        """Clear all animations"""
        self.animations.clear()


def create_animation_for_move(move_name, move_data, start_x, start_y, target_x, target_y, character_name=None):
    """
    Create an animation based on move type
    
    Args:
        move_name: Name of the move
        move_data: Move data dictionary
        start_x, start_y: Starting position (attacker)
        target_x, target_y: Target position (defender)
        character_name: Name of the character (optional)
    
    Returns:
        Animation instance
    """
    move_type = move_data.get('type', 'Normal')
    power = move_data.get('power', 50)
    effect = move_data.get('effect', 'physical')
    
    # Type-based color mapping
    type_colors = {
        "Grass": (100, 200, 100),
        "Oil": (139, 69, 19),
        "Light": (255, 255, 150),
        "Star": (186, 85, 211),
        "Bonk": (220, 20, 60),
        "Mod": (70, 130, 180),
        "Imagination": (218, 112, 214),
        "Miwiwi": (255, 20, 147),
        "Crude Oil": (85, 85, 85),
        "Catgirl": (255, 182, 193),
        "Car": (255, 140, 0),
        "Miwawa": (255, 69, 0),
        "Human": (210, 180, 140)
    }
    
    color = type_colors.get(move_type, (200, 200, 200))
    
    # Physical effects = melee animations
    physical_effects = ["physical", "strong", "devastating", "stun", "combo", "pierce"]
    
    if effect in physical_effects:
        # Melee animation
        direction = 'right' if target_x > start_x else 'left'
        return MeleeAnimation(target_x, target_y, direction, color, power)
    else:
        # Ranged/special animation
        return ProjectileAnimation(start_x, start_y, target_x, target_y, color, power)