import pygame, math
from python.pygame1 import SCREEN, SMALL_FONT
from python.color import BLACK, WHITE, CYAN, GREEN, YELLOW, RED, ORANGE, GRAY, PURPLE, PINK, BLUE
from python.shadowed_text_and_buttons import draw_text_with_shadow

def draw_energy_bar(x, y, current_energy, max_energy, width=200):
    """Enhanced energy bar with smooth animations and particle effects"""
    energy_percentage = current_energy / max_energy if max_energy > 0 else 0
    energy_width = int(energy_percentage * width)
    
    # Outer glow effect
    glow_surface = pygame.Surface((width + 8, 28), pygame.SRCALPHA)
    for glow_offset in range(3):
        alpha = 40 - (glow_offset * 10)
        glow_rect = pygame.Rect(glow_offset, glow_offset, width + 8 - (glow_offset * 2), 28 - (glow_offset * 2))
        pygame.draw.rect(glow_surface, (100, 150, 255, alpha), glow_rect, 2)
    SCREEN.blit(glow_surface, (x - 4, y - 4))
    
    # Dark background with depth
    bg_surface = pygame.Surface((width, 20))
    for i in range(20):
        progress = i / 20
        r = int(15 + progress * 10)
        g = int(15 + progress * 15)
        b = int(30 + progress * 20)
        pygame.draw.line(bg_surface, (r, g, b), (0, i), (width, i))
    SCREEN.blit(bg_surface, (x, y))
    
    # Inner shadow for depth
    shadow_surface = pygame.Surface((width, 20), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 80), (0, 0, width, 8))
    SCREEN.blit(shadow_surface, (x, y))
    
    # Energy fill with enhanced gradient
    if energy_width > 0:
        energy_surface = pygame.Surface((energy_width, 20))
        
        for i in range(20):
            progress = i / 20
            
            if energy_percentage > 0.6:
                # Bright cyan/blue for high energy
                r = int(40 + progress * 60)
                g = int(120 + progress * 80)
                b = int(200 + progress * 55)
            elif energy_percentage > 0.3:
                # Purple/blue for medium energy
                r = int(100 + progress * 80)
                g = int(80 + progress * 100)
                b = int(200 + progress * 55)
            else:
                # Dark purple for low energy
                r = int(120 + progress * 60)
                g = int(40 + progress * 40)
                b = int(180 + progress * 75)
            
            pygame.draw.line(energy_surface, (r, g, b), (0, i), (energy_width, i))
        
        SCREEN.blit(energy_surface, (x, y))
        
        # Animated shine effect
        time = pygame.time.get_ticks()
        shine_offset = (time * 0.1) % (width + 100) - 50
        
        if 0 < shine_offset < energy_width:
            shine_surface = pygame.Surface((30, 20), pygame.SRCALPHA)
            for i in range(30):
                alpha = int(100 * (1 - abs(i - 15) / 15))
                pygame.draw.line(shine_surface, (255, 255, 255, alpha), (i, 0), (i, 20))
            SCREEN.blit(shine_surface, (x + int(shine_offset) - 15, y))
        
        # Highlight at top
        highlight_surface = pygame.Surface((energy_width, 20), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, (255, 255, 255, 60), (0, 0, energy_width, 6))
        SCREEN.blit(highlight_surface, (x, y))
    
    # Segmented bars effect
    segment_count = 10
    for i in range(1, segment_count):
        seg_x = x + (width // segment_count) * i
        pygame.draw.line(SCREEN, (0, 0, 0, 100), (seg_x, y), (seg_x, y + 20), 1)
    
    # Strong border
    pygame.draw.rect(SCREEN, BLACK, (x, y, width, 20), 3)
    pygame.draw.rect(SCREEN, (100, 150, 200), (x, y, width, 20), 1)
    
    # Energy text with colored indicator
    if energy_percentage > 0.6:
        text_color = CYAN
    elif energy_percentage > 0.3:
        text_color = (150, 150, 255)
    else:
        text_color = PURPLE
    
    energy_text = f"MP: {int(current_energy)}/{int(max_energy)}"
    draw_text_with_shadow(energy_text, x + width + 10, y - 2, text_color, SMALL_FONT)
    
    # Percentage indicator
    percentage_text = f"{int(energy_percentage * 100)}%"
    draw_text_with_shadow(percentage_text, x + width // 2 - 15, y - 2, WHITE, SMALL_FONT, shadow_offset=1)


def draw_animated_health_bar(x, y, current_hp, max_hp, width=250, animate_time=0):
    """Enhanced animated health bar with smooth transitions and effects"""
    health_percentage = current_hp / max_hp if max_hp > 0 else 0
    health_width = int(health_percentage * width)
    
    # Pulsing outer glow
    pulse = math.sin(animate_time * 0.005) * 0.5 + 0.5
    glow_alpha = int(60 + pulse * 40)
    
    glow_surface = pygame.Surface((width + 10, 35), pygame.SRCALPHA)
    for glow_offset in range(4):
        alpha = glow_alpha - (glow_offset * 15)
        glow_rect = pygame.Rect(glow_offset, glow_offset, width + 10 - (glow_offset * 2), 35 - (glow_offset * 2))
        
        if health_percentage > 0.5:
            glow_color = (100, 255, 100, alpha)
        elif health_percentage > 0.25:
            glow_color = (255, 255, 100, alpha)
        else:
            glow_color = (255, 100, 100, alpha)
        
        pygame.draw.rect(glow_surface, glow_color, glow_rect, 2)
    
    SCREEN.blit(glow_surface, (x - 5, y - 5))
    
    # Background with gradient
    bg_surface = pygame.Surface((width, 25))
    for i in range(25):
        progress = i / 25
        r = int(30 + progress * 20)
        g = int(10 + progress * 10)
        b = int(10 + progress * 10)
        pygame.draw.line(bg_surface, (r, g, b), (0, i), (width, i))
    SCREEN.blit(bg_surface, (x, y))
    
    # Inner shadow
    shadow_surface = pygame.Surface((width, 25), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 100), (0, 0, width, 10))
    SCREEN.blit(shadow_surface, (x, y))
    
    # Animated health fill with enhanced gradients
    if health_width > 0:
        health_surface = pygame.Surface((health_width, 25))
        
        for i in range(25):
            progress = i / 25
            
            if health_percentage > 0.5:
                # Vibrant green for healthy
                r = int(50 + progress * 40)
                g = int(180 + progress * 75)
                b = int(50 + progress * 30)
            elif health_percentage > 0.25:
                # Orange/yellow for warning
                r = int(220 + progress * 35)
                g = int(180 + progress * 75)
                b = int(40 + progress * 20)
            else:
                # Red for critical
                r = int(220 + progress * 35)
                g = int(40 + progress * 30)
                b = int(40 + progress * 20)
            
            pygame.draw.line(health_surface, (r, g, b), (0, i), (health_width, i))
        
        SCREEN.blit(health_surface, (x, y))
        
        # Animated shine effect
        shine_offset = (animate_time * 0.15) % (width + 120) - 60
        
        if 0 < shine_offset < health_width:
            shine_surface = pygame.Surface((40, 25), pygame.SRCALPHA)
            for i in range(40):
                alpha = int(120 * (1 - abs(i - 20) / 20))
                pygame.draw.line(shine_surface, (255, 255, 255, alpha), (i, 0), (i, 25))
            SCREEN.blit(shine_surface, (x + int(shine_offset) - 20, y))
        
        # Top highlight
        highlight_surface = pygame.Surface((health_width, 25), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, (255, 255, 255, 80), (0, 0, health_width, 8))
        SCREEN.blit(highlight_surface, (x, y))
        
        # Pulse effect for low health
        if health_percentage < 0.25:
            pulse_intensity = math.sin(animate_time * 0.01) * 0.5 + 0.5
            pulse_surface = pygame.Surface((health_width, 25), pygame.SRCALPHA)
            pulse_alpha = int(pulse_intensity * 80)
            pygame.draw.rect(pulse_surface, (255, 0, 0, pulse_alpha), (0, 0, health_width, 25))
            SCREEN.blit(pulse_surface, (x, y))
    
    # Segmented bars for easier reading
    segment_count = 10
    for i in range(1, segment_count):
        seg_x = x + (width // segment_count) * i
        pygame.draw.line(SCREEN, (0, 0, 0, 120), (seg_x, y), (seg_x, y + 25), 2)
    
    # Animated border glow
    border_pulse = int(128 + 127 * math.sin(animate_time * 0.008))
    border_glow_surface = pygame.Surface((width + 6, 31), pygame.SRCALPHA)
    
    if health_percentage > 0.5:
        border_color = (100, 255, 100, border_pulse)
    elif health_percentage > 0.25:
        border_color = (255, 255, 100, border_pulse)
    else:
        border_color = (255, 100, 100, border_pulse)
    
    pygame.draw.rect(border_glow_surface, border_color, (0, 0, width + 6, 31), 3)
    SCREEN.blit(border_glow_surface, (x - 3, y - 3))
    
    # Strong border
    pygame.draw.rect(SCREEN, BLACK, (x, y, width, 25), 4)
    pygame.draw.rect(SCREEN, WHITE, (x, y, width, 25), 1)
    
    # HP text with dynamic color and shadow
    if health_percentage > 0.5:
        text_color = GREEN
    elif health_percentage > 0.25:
        text_color = YELLOW
    else:
        text_color = RED
    
    hp_text = f"{int(current_hp)}/{int(max_hp)}"
    draw_text_with_shadow(hp_text, x + width + 15, y + 3, text_color, SMALL_FONT, shadow_offset=2)
    
    # HP percentage
    percentage_text = f"{int(health_percentage * 100)}%"
    draw_text_with_shadow(percentage_text, x + width // 2 - 15, y + 1, WHITE, SMALL_FONT, shadow_offset=2)
    
    # Critical health warning
    if health_percentage < 0.25:
        warning_alpha = int(abs(math.sin(animate_time * 0.01)) * 255)
        warning_text = "!"
        warning_surface = SMALL_FONT.render(warning_text, True, RED)
        warning_alpha_surface = pygame.Surface(warning_surface.get_size(), pygame.SRCALPHA)
        warning_alpha_surface.fill((255, 255, 255, warning_alpha))
        warning_surface.blit(warning_alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        SCREEN.blit(warning_surface, (x - 25, y + 3))