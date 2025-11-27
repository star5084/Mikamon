"""
Enhanced Move Display System
Add this code to your battle_system.py to replace the move button rendering section
This adds visual distinction for regular, special, and ultimate attacks
"""

import pygame
from python.shadowed_text_and_buttons import draw_gradient_button
from python.color import *

def get_move_display_colors(move_data):
    """
    Get appropriate colors for move button based on move type
    Returns: (color1, color2, border_color, text_color, glow_color)
    """
    # Check if it's an ultimate move (most powerful)
    if move_data.get("is_ultimate", False):
        return (
            (255, 0, 255),      # Magenta base
            (150, 0, 150),      # Dark magenta
            (255, 215, 0),      # Gold border
            (255, 255, 255),    # White text
            (255, 100, 255)     # Pink glow
        )
    
    # Check if it's a special move
    elif move_data.get("is_special", False):
        return (
            (100, 150, 255),    # Bright blue base
            (50, 80, 200),      # Dark blue
            (255, 255, 100),    # Yellow border
            (255, 255, 255),    # White text
            (150, 200, 255)     # Light blue glow
        )
    
    # Regular move - use type colors
    else:
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
        move_type = move_data.get("type", "Normal")
        color1 = type_colors.get(move_type, (160, 160, 160))
        color2 = tuple(max(0, c - 40) for c in color1)
        return (
            color1,
            color2,
            (0, 0, 0),          # Black border
            (0, 0, 0),          # Black text
            None                # No glow
        )

def draw_enhanced_move_button(text, rect, move_data, can_use, hover, font, screen, battle_timer=0):
    """
    Draw a move button with enhanced visuals for special/ultimate attacks
    
    Parameters:
    - text: Button text to display
    - rect: pygame.Rect for button position/size
    - move_data: Dictionary containing move information
    - can_use: Boolean if player has enough MP
    - hover: Boolean if mouse is hovering
    - font: Pygame font to use
    - screen: Pygame surface to draw on
    - battle_timer: Animation timer for effects
    """
    import math
    
    if not can_use:
        # Grayed out button
        color1 = (80, 80, 80)
        color2 = (60, 60, 60)
        border_color = (40, 40, 40)
        text_color = (120, 120, 120)
        glow_color = None
    else:
        color1, color2, border_color, text_color, glow_color = get_move_display_colors(move_data)
    
    # Gradient background
    button_surface = pygame.Surface((rect.width, rect.height))
    for i in range(rect.height):
        t = i / rect.height
        if hover and can_use:
            # Brighten on hover
            color = tuple(min(255, int(color1[j] * (1-t) + color2[j] * t + 20)) for j in range(3))
        else:
            color = tuple(int(color1[j] * (1-t) + color2[j] * t) for j in range(3))
        pygame.draw.line(button_surface, color, (0, i), (rect.width, i))
    
    screen.blit(button_surface, rect.topleft)
    
    # Animated glow for special/ultimate moves
    if glow_color and can_use:
        pulse = math.sin(battle_timer * 0.005) * 0.5 + 0.5  # 0 to 1
        glow_alpha = int(100 + pulse * 80)
        
        # Draw glow layers
        for thickness in range(8, 0, -2):
            alpha = int((glow_alpha * thickness) / 8)
            glow_surface = pygame.Surface((rect.width + thickness*2, rect.height + thickness*2), pygame.SRCALPHA)
            glow_color_alpha = (*glow_color, alpha)
            pygame.draw.rect(glow_surface, glow_color_alpha, 
                           (0, 0, rect.width + thickness*2, rect.height + thickness*2), 
                           thickness)
            screen.blit(glow_surface, (rect.x - thickness, rect.y - thickness))
    
    # Border
    border_width = 3 if (move_data.get("is_ultimate") or move_data.get("is_special")) else 2
    pygame.draw.rect(screen, border_color, rect, border_width)
    
    # Special/Ultimate indicator badge
    if move_data.get("is_ultimate", False):
        badge_text = "★ULTIMATE★"
        badge_color = (255, 215, 0)  # Gold
    elif move_data.get("is_special", False):
        badge_text = "⚡SPECIAL⚡"
        badge_color = (255, 255, 100)  # Yellow
    else:
        badge_text = None
    
    if badge_text:
        badge_font = pygame.font.Font(None, 18)
        badge_surface = badge_font.render(badge_text, True, badge_color)
        badge_rect = badge_surface.get_rect()
        badge_x = rect.x + rect.width - badge_rect.width - 5
        badge_y = rect.y + 3
        
        # Badge shadow
        shadow_surface = badge_font.render(badge_text, True, (0, 0, 0))
        screen.blit(shadow_surface, (badge_x + 1, badge_y + 1))
        screen.blit(badge_surface, (badge_x, badge_y))
    
    # Main text with shadow
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(rect.centerx + 1, rect.centery + 1))
    screen.blit(text_surface, text_rect)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)