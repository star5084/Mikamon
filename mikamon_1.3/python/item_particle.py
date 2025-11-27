import pygame, random
from python.color import GREEN, CYAN, GOLD
class ItemParticle:
    def __init__(self, x, y, color, effect_type):
        self.x = x
        self.y = y
        self.color = color
        self.effect_type = effect_type
        self.life = 2000
        self.max_life = 2000
        
        if effect_type == "heal":
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-3, -1)
            self.size = random.uniform(3, 6)
        elif effect_type == "mp_restore":
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-2, 2)
            self.size = random.uniform(2, 4)
        elif effect_type == "stat_boost":
            self.vx = random.uniform(-0.5, 0.5)
            self.vy = random.uniform(-4, -2)
            self.size = random.uniform(4, 8)
        else:  # Other effects
            self.vx = random.uniform(-1.5, 1.5)
            self.vy = random.uniform(-2, -0.5)
            self.size = random.uniform(3, 5)
    
    def update(self, dt):
        self.x += self.vx * dt / 16.67
        self.y += self.vy * dt / 16.67
        self.life -= dt
        
        # Add some floating motion
        self.vx *= 0.98
        self.vy *= 0.98
        
        return self.life > 0
    
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = max(1, int(self.size * (self.life / self.max_life)))
            
            if self.effect_type == "heal":
                # Draw plus sign for healing
                pygame.draw.circle(screen, (*GREEN, alpha), (int(self.x), int(self.y)), size)
                pygame.draw.line(screen, (255, 255, 255), 
                               (self.x - size//2, self.y), (self.x + size//2, self.y), 2)
                pygame.draw.line(screen, (255, 255, 255), 
                               (self.x, self.y - size//2), (self.x, self.y + size//2), 2)
            elif self.effect_type == "mp_restore":
                # Draw sparkle for MP
                pygame.draw.circle(screen, (*CYAN, alpha), (int(self.x), int(self.y)), size)
            elif self.effect_type == "stat_boost":
                # Draw arrow up for stat boost
                pygame.draw.circle(screen, (*GOLD, alpha), (int(self.x), int(self.y)), size)
            else:
                # Generic sparkle
                pygame.draw.circle(screen, (*self.color, alpha), (int(self.x), int(self.y)), size)