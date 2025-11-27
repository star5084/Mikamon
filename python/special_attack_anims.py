"""
Special Attack Animation System
Enhanced animations for special and ultimate moves
Add this to your attack_animations.py or create as a new module
"""

import pygame
import random
import math
from python.color import *

class SpecialAttackAnimation:
    """Enhanced animation for special and ultimate attacks"""
    
    def __init__(self, move_name, move_data, start_x, start_y, target_x, target_y):
        self.move_name = move_name
        self.move_data = move_data
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.timer = 0
        self.max_duration = 2000  # 2 seconds
        self.particles = []
        self.is_ultimate = move_data.get("is_ultimate", False)
        self.is_special = move_data.get("is_special", False)
        self.done = False
        
        # Generate particles based on attack type
        self._generate_particles()
    
    def _generate_particles(self):
        """Generate particles for the animation"""
        particle_count = 50 if self.is_ultimate else 30 if self.is_special else 15
        
        # Color scheme based on attack type
        if self.is_ultimate:
            colors = [
                (255, 0, 255),    # Magenta
                (255, 100, 255),  # Pink
                (255, 215, 0),    # Gold
                (255, 255, 255),  # White
                (200, 0, 200)     # Purple
            ]
        elif self.is_special:
            colors = [
                (100, 150, 255),  # Blue
                (150, 200, 255),  # Light blue
                (255, 255, 100),  # Yellow
                (255, 255, 255),  # White
                (0, 200, 255)     # Cyan
            ]
        else:
            colors = [(255, 255, 255)]
        
        for i in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6) if self.is_ultimate else random.uniform(1, 4)
            size = random.randint(8, 20) if self.is_ultimate else random.randint(4, 12)
            color = random.choice(colors)
            
            self.particles.append({
                'x': self.start_x,
                'y': self.start_y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'life': 1.0,
                'decay': random.uniform(0.003, 0.008)
            })
    
    def update(self, dt):
        """Update animation state"""
        self.timer += dt
        
        if self.timer >= self.max_duration:
            self.done = True
            return False
        
        # Update particles
        for particle in self.particles:
            # Move toward target
            progress = self.timer / self.max_duration
            dx = self.target_x - particle['x']
            dy = self.target_y - particle['y']
            
            # Accelerate toward target over time
            particle['vx'] += dx * 0.0001 * progress
            particle['vy'] += dy * 0.0001 * progress
            
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= particle['decay']
            
            # Ultimate attacks have swirling motion
            if self.is_ultimate:
                swirl_angle = self.timer * 0.01
                swirl_radius = 30 * (1 - progress)
                particle['x'] += math.cos(swirl_angle + particle['vx']) * swirl_radius * 0.1
                particle['y'] += math.sin(swirl_angle + particle['vy']) * swirl_radius * 0.1
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        return True
    
    def draw(self, screen):
        """Draw the animation"""
        progress = self.timer / self.max_duration
        
        # Draw connecting beam for ultimate attacks
        if self.is_ultimate and progress > 0.3:
            beam_alpha = int(150 * math.sin(progress * math.pi))
            beam_width = int(20 + 30 * math.sin(progress * math.pi))
            
            # Multi-colored beam layers
            beam_colors = [
                (255, 0, 255, beam_alpha),
                (255, 100, 255, beam_alpha // 2),
                (255, 215, 0, beam_alpha // 3)
            ]
            
            for i, color in enumerate(beam_colors):
                beam_surface = pygame.Surface((abs(self.target_x - self.start_x) + beam_width * 2,
                                              abs(self.target_y - self.start_y) + beam_width * 2),
                                             pygame.SRCALPHA)
                
                offset = (i + 1) * 5
                pygame.draw.line(beam_surface, color,
                               (self.start_x, self.start_y),
                               (self.target_x, self.target_y),
                               beam_width - offset)
                screen.blit(beam_surface, (min(self.start_x, self.target_x) - beam_width,
                                          min(self.start_y, self.target_y) - beam_width))
        
        # Draw special attack lightning effect
        elif self.is_special and progress > 0.2:
            lightning_points = []
            num_segments = 10
            for i in range(num_segments + 1):
                t = i / num_segments
                x = self.start_x + (self.target_x - self.start_x) * t
                y = self.start_y + (self.target_y - self.start_y) * t
                
                # Add random offset for lightning effect
                if i > 0 and i < num_segments:
                    offset = random.randint(-20, 20)
                    x += offset
                    y += offset
                
                lightning_points.append((int(x), int(y)))
            
            # Draw lightning with glow
            if len(lightning_points) > 1:
                for thickness in range(8, 0, -2):
                    alpha = int(150 - thickness * 15)
                    color = (150, 200, 255, alpha)
                    pygame.draw.lines(screen, color, False, lightning_points, thickness)
        
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * particle['life'])
                size = int(particle['size'] * particle['life'])
                
                if size > 0:
                    # Draw particle with glow
                    particle_surface = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                    
                    # Outer glow
                    pygame.draw.circle(particle_surface, 
                                     (*particle['color'], alpha // 3),
                                     (size * 3 // 2, size * 3 // 2), 
                                     size * 2)
                    
                    # Inner bright core
                    pygame.draw.circle(particle_surface,
                                     (*particle['color'], alpha),
                                     (size * 3 // 2, size * 3 // 2),
                                     size)
                    
                    screen.blit(particle_surface, 
                              (int(particle['x'] - size * 1.5), 
                               int(particle['y'] - size * 1.5)))
        
        # Impact explosion at target
        if progress > 0.7:
            explosion_progress = (progress - 0.7) / 0.3
            explosion_size = int(100 * math.sin(explosion_progress * math.pi))
            
            if explosion_size > 0:
                explosion_surface = pygame.Surface((explosion_size * 2, explosion_size * 2), 
                                                  pygame.SRCALPHA)
                
                # Multiple explosion rings
                colors = [(255, 255, 255), (255, 215, 0), (255, 100, 0)] if self.is_ultimate else \
                         [(255, 255, 255), (100, 150, 255), (0, 200, 255)]
                
                for i, color in enumerate(colors):
                    ring_size = explosion_size - i * 15
                    if ring_size > 0:
                        alpha = int(200 * (1 - explosion_progress))
                        pygame.draw.circle(explosion_surface,
                                         (*color, alpha),
                                         (explosion_size, explosion_size),
                                         ring_size)
                
                screen.blit(explosion_surface,
                          (self.target_x - explosion_size, self.target_y - explosion_size))


def create_special_animation(move_name, move_data, start_x, start_y, target_x, target_y):
    """
    Factory function to create appropriate animation
    Returns SpecialAttackAnimation for special/ultimate moves, None for regular moves
    """
    if move_data.get("is_special") or move_data.get("is_ultimate"):
        return SpecialAttackAnimation(move_name, move_data, start_x, start_y, target_x, target_y)
    return None