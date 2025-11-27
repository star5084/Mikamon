from python.color import DARK_GRAY, BLACK, WHITE
from python.pygame1 import SCREEN, FONT
import pygame
def draw_text_with_shadow(text, x, y, color=BLACK, font=None, shadow_offset=2):
    if font is None:
        font = FONT
    # Draw shadow
    shadow = font.render(text, True, DARK_GRAY)
    SCREEN.blit(shadow, (x + shadow_offset, y + shadow_offset))
    # Draw text
    render = font.render(text, True, color)
    SCREEN.blit(render, (x, y))
    return render.get_rect(topleft=(x, y))

def draw_gradient_button(text, rect, color1, color2, hover=False, font=None):
    if font is None:
        font = FONT
    
    # Create gradient surface
    gradient = pygame.Surface((rect.width, rect.height))
    
    if hover:
        color1 = tuple(min(255, c + 30) for c in color1)
        color2 = tuple(min(255, c + 30) for c in color2)
    
    for y in range(rect.height):
        t = y / rect.height
        r = int(color1[0] * (1-t) + color2[0] * t)
        g = int(color1[1] * (1-t) + color2[1] * t)
        b = int(color1[2] * (1-t) + color2[2] * t)
        pygame.draw.line(gradient, (r, g, b), (0, y), (rect.width, y))
    
    SCREEN.blit(gradient, rect.topleft)
    pygame.draw.rect(SCREEN, BLACK, rect, 2)
    
    text_render = font.render(text, True, WHITE)
    shadow_render = font.render(text, True, DARK_GRAY)
    text_rect = text_render.get_rect()
    text_x = rect.x + (rect.width - text_rect.width) // 2
    text_y = rect.y + (rect.height - text_rect.height) // 2
    
    SCREEN.blit(shadow_render, (text_x + 1, text_y + 1))
    SCREEN.blit(text_render, (text_x, text_y))