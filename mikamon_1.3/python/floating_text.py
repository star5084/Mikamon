from python.pygame1 import FONT
from python.color import BLACK
class FloatingText:
    def __init__(self, text, x, y, color=BLACK, duration=2000):
        self.text = text
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.duration = duration
        self.timer = 0
        self.alpha = 255
        
    def update(self, dt):
        self.timer += dt
        progress = self.timer / self.duration
        if progress >= 1:
            return False
        
        self.y = self.start_y - (progress * 50)
        self.alpha = int(255 * (1 - progress))
        return True
    
    def draw(self, screen):
        text_surface = FONT.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        screen.blit(text_surface, (self.x, self.y))