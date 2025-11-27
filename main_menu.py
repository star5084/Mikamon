"""
Enhanced Main Menu System with New Game/Continue functionality
"""

import pygame
import sys
import math
import random
from python.color import (WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY, GREEN, 
                          DARK_GREEN, BLUE, DARK_BLUE, GOLD, RED, DARK_RED, 
                          YELLOW, ORANGE, CYAN, PINK, PURPLE)
from python.pygame1 import FONT, SMALL_FONT, BIG_FONT, CLOCK
from python.shadowed_text_and_buttons import draw_text_with_shadow, draw_gradient_button
from python.save_system import save_system
from python.clock import draw_real_time_clock
from python.settings import game_settings
from python.fullscreen_toggle import (
    display_manager, handle_fullscreen_toggle, scale_background_for_resolution,
    create_fullscreen_button, draw_fullscreen_button
)

class MenuParticle:
    """Floating particles for background atmosphere"""
    def __init__(self, x, y, color, speed):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.size = random.randint(2, 5)
        self.alpha = random.randint(100, 255)
        self.lifetime = random.randint(3000, 6000)
        self.angle = random.uniform(0, math.pi * 2)
        
    def update(self, dt):
        self.lifetime -= dt
        self.x += math.cos(self.angle) * self.speed * dt * 0.05
        self.y += math.sin(self.angle) * self.speed * dt * 0.05
        self.alpha = max(0, self.alpha - dt * 0.05)
        return self.lifetime > 0
    
    def draw(self, screen):
        if self.alpha > 0:
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color[:3], int(self.alpha))
            pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(surf, (int(self.x), int(self.y)))

def draw_enhanced_credits(screen, screen_width, screen_height, timer):
    """Draw enhanced credits with animations"""
    # AE Logo with glow effect
    logo_y = 30
    ae_font = pygame.font.Font(None, 96)
    
    # Animated glow
    glow_intensity = int(30 + 20 * math.sin(timer * 0.003))
    for offset in range(8, 0, -2):
        glow_alpha = int(glow_intensity - offset * 3)
        glow_surface = ae_font.render("AE", True, GOLD)
        glow_surface.set_alpha(glow_alpha)
        glow_rect = glow_surface.get_rect(center=(screen_width // 2 + offset//2, logo_y + offset//2))
        screen.blit(glow_surface, glow_rect)
    
    # Main AE text
    ae_surface = ae_font.render("AE", True, GOLD)
    ae_rect = ae_surface.get_rect(center=(screen_width // 2, logo_y))
    
    # Shadow
    shadow_surface = ae_font.render("AE", True, BLACK)
    screen.blit(shadow_surface, (ae_rect.x + 4, ae_rect.y + 4))
    screen.blit(ae_surface, ae_rect)
    
    # Actual Entertainment with fade effect
    subtitle_y = logo_y + 65
    subtitle_alpha = int(200 + 55 * math.sin(timer * 0.002))
    subtitle_font = pygame.font.Font(None, 32)
    subtitle_surf = subtitle_font.render("(Actual Entertainment)", True, WHITE)
    subtitle_rect = subtitle_surf.get_rect(center=(screen_width // 2, subtitle_y))
    
    temp_surf = pygame.Surface(subtitle_surf.get_size(), pygame.SRCALPHA)
    temp_surf.blit(subtitle_surf, (0, 0))
    temp_surf.set_alpha(subtitle_alpha)
    screen.blit(temp_surf, subtitle_rect)
    
    # Idea credit with subtle movement
    idea_y = subtitle_y + 30
    idea_offset = int(3 * math.sin(timer * 0.001))
    draw_text_with_shadow("[idea from Luna]", screen_width // 2 - 60, idea_y + idea_offset, GRAY, SMALL_FONT, 1)
    
    # Made by credits with color cycling
    credits_y = idea_y + 50
    credit_hue = (timer * 0.0005) % 1.0
    # Cycle between cyan, gold, and pink
    if credit_hue < 0.33:
        credit_color = CYAN
    elif credit_hue < 0.66:
        credit_color = GOLD
    else:
        credit_color = PINK
    
    draw_text_with_shadow("Made by: star5084", screen_width // 2 - 90, credits_y, credit_color, FONT, 2)
    
    playtester_y = credits_y + 35
    draw_text_with_shadow("Play tested by: Автомобильный стол (Car Table)", 
                         screen_width // 2 - 220, playtester_y, PINK, SMALL_FONT, 1)

def draw_animated_title(screen, screen_width, screen_height, timer):
    """Draw title with equal letter spacing and multiple animation effects"""
    title_y = int(screen_height * 0.3)
    
    # Rainbow wave effect on letters with EQUAL spacing
    title_text = "MIKAMON: CATGIRL CHRONICLES"
    
    # Calculate equal spacing by measuring each character
    char_width = BIG_FONT.size("M")[0]  # Use a standard character width
    letter_spacing = char_width + 2  # Add small padding for equal spacing
    total_width = len(title_text) * letter_spacing
    start_x = (screen_width - total_width) // 2
    
    for i, char in enumerate(title_text):
        # Wave animation
        wave_offset = int(10 * math.sin(timer * 0.005 + i * 0.3))
        
        # Color cycle per letter
        hue = (timer * 0.0003 + i * 0.05) % 1.0
        if hue < 0.5:
            t = hue * 2
            color = (
                int(255 * (1 - t) + 255 * t),  # Red to Yellow
                int(215 * (1 - t) + 255 * t),
                int(0 * (1 - t) + 0 * t)
            )
        else:
            t = (hue - 0.5) * 2
            color = (
                int(255 * (1 - t) + 255 * t),  # Yellow to Gold
                int(255 * (1 - t) + 215 * t),
                int(0 * (1 - t) + 0 * t)
            )
        
        # Glow effect
        for offset in range(6, 0, -1):
            glow_alpha = int(80 - offset * 10)
            glow_surf = BIG_FONT.render(char, True, color)
            glow_surf.set_alpha(glow_alpha)
            screen.blit(glow_surf, (start_x + i * letter_spacing + offset, title_y + wave_offset + offset))
        
        # Main letter with shadow
        shadow_surf = BIG_FONT.render(char, True, BLACK)
        screen.blit(shadow_surf, (start_x + i * letter_spacing + 3, title_y + wave_offset + 3))
        
        char_surf = BIG_FONT.render(char, True, color)
        screen.blit(char_surf, (start_x + i * letter_spacing, title_y + wave_offset))

def draw_save_info_panel(screen, save_info, button_x, button_y, button_width, timer):
    """Draw enhanced save info panel - NO last played text"""
    if not save_info:
        return
    
    panel_width = button_width + 200
    panel_height = 80
    panel_x = button_x - 100
    panel_y = button_y + 90
    
    # Animated background
    panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    alpha = int(200 + 30 * math.sin(timer * 0.003))
    
    # Gradient background
    for i in range(panel_height):
        t = i / panel_height
        color = (
            int(DARK_BLUE[0] * (1 - t) + BLUE[0] * t),
            int(DARK_BLUE[1] * (1 - t) + BLUE[1] * t),
            int(DARK_BLUE[2] * (1 - t) + BLUE[2] * t),
            alpha
        )
        pygame.draw.line(panel_surface, color, (0, i), (panel_width, i))
    
    screen.blit(panel_surface, (panel_x, panel_y))
    pygame.draw.rect(screen, GOLD, (panel_x, panel_y, panel_width, panel_height), 3)
    
    # Save info text - REMOVED last played
    info_y = panel_y + 15
    stats_text = f"Difficulty: {save_info['difficulty']} | Battles: {save_info['total_battles']} ({save_info['battles_won']}W / {save_info['battles_lost']}L)"
    draw_text_with_shadow(stats_text, panel_x + 20, info_y, CYAN, SMALL_FONT, 1)
    
    # Win rate bar
    if save_info['total_battles'] > 0:
        win_rate = save_info['battles_won'] / save_info['total_battles']
        bar_y = info_y + 30
        bar_width = panel_width - 40
        bar_height = 15
        
        # Background bar
        pygame.draw.rect(screen, DARK_GRAY, (panel_x + 20, bar_y, bar_width, bar_height))
        
        # Win rate fill
        fill_width = int(bar_width * win_rate)
        if win_rate > 0.7:
            fill_color = GREEN
        elif win_rate > 0.4:
            fill_color = YELLOW
        else:
            fill_color = RED
        
        pygame.draw.rect(screen, fill_color, (panel_x + 20, bar_y, fill_width, bar_height))
        pygame.draw.rect(screen, BLACK, (panel_x + 20, bar_y, bar_width, bar_height), 2)
        
        # Win rate text
        rate_text = f"{int(win_rate * 100)}% Win Rate"
        draw_text_with_shadow(rate_text, panel_x + 25, bar_y + 1, WHITE, SMALL_FONT, 1)

def draw_menu_button_enhanced(screen, rect, text, color1, color2, hover, font, timer, enabled=True):
    """Draw enhanced menu button with SOLID colors and rounded edges"""
    if not enabled:
        color1, color2 = DARK_GRAY, GRAY
    
    # Ensure colors are tuples of 3 values (RGB)
    if len(color1) > 3:
        color1 = color1[:3]
    if len(color2) > 3:
        color2 = color2[:3]
    
    # Use color1 as the SOLID button color (no gradient)
    button_color = color1
    
    # Hover animation - brighten the solid color
    if hover and enabled:
        pulse = int(15 * math.sin(timer * 0.01))
        button_color = tuple(max(0, min(255, c + pulse + 20)) for c in color1)
        
        # Glow effect
        for i in range(4, 0, -1):
            glow_rect = rect.inflate(i * 4, i * 4)
            glow_alpha = int(60 - i * 12)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*button_color, glow_alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=10)
            screen.blit(glow_surface, glow_rect.topleft)
    
    # Draw SOLID color button with rounded corners
    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    
    # Border with rounded corners
    border_color = GOLD if hover and enabled else BLACK
    border_width = 4 if hover and enabled else 3
    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=10)
    
    # Text with shadow
    text_surface = font.render(text, True, WHITE if enabled else DARK_GRAY)
    text_rect = text_surface.get_rect(center=rect.center)
    
    shadow_surface = font.render(text, True, BLACK)
    screen.blit(shadow_surface, (text_rect.x + 2, text_rect.y + 2))
    screen.blit(text_surface, text_rect)

def main_menu(sprites, battle_sprites, background):
    """
    Enhanced main menu with New Game/Continue options
    Returns: 'new_game', 'continue', or 'quit'
    """
    menu_timer = 0
    show_confirmation = False
    confirmation_type = None
    particles = []
    
    # Check if save exists and LOAD SETTINGS
    has_save = save_system.has_save()
    save_info = save_system.get_save_info() if has_save else None
    
    # CRITICAL FIX: Load settings from save file into game_settings
    if has_save and save_system.save_data:
        saved_settings = save_system.save_data.get("settings", {})
        game_settings.update(saved_settings)
        print(f"Main menu loaded settings from save: {game_settings}")
    
    # Initialize particles
    screen_width, screen_height = display_manager.get_size()
    for _ in range(30):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        color = random.choice([GOLD, CYAN, PINK, PURPLE, YELLOW])
        speed = random.uniform(0.5, 2.0)
        particles.append(MenuParticle(x, y, color, speed))
    
    while True:
        dt = CLOCK.get_time()
        menu_timer += dt
        
        # Get current screen
        SCREEN = display_manager.get_screen()
        screen_width, screen_height = display_manager.get_size()
        
        # Scale and draw background
        scaled_background = scale_background_for_resolution(background)
        SCREEN.blit(scaled_background, (0, 0))
        
        # Animated overlay with breathing effect
        overlay_alpha = int(100 + 40 * math.sin(menu_timer * 0.002))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((*BLACK[:3], overlay_alpha))
        SCREEN.blit(overlay, (0, 0))
        
        # Update and draw particles
        particles = [p for p in particles if p.update(dt)]
        
        # Add new particles
        if len(particles) < 30 and random.random() < 0.3:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            color = random.choice([GOLD, CYAN, PINK, PURPLE, YELLOW])
            speed = random.uniform(0.5, 2.0)
            particles.append(MenuParticle(x, y, color, speed))
        
        for particle in particles:
            particle.draw(SCREEN)
        
        # Draw enhanced credits
        draw_enhanced_credits(SCREEN, screen_width, screen_height, menu_timer)
        
        # Draw animated title
        draw_animated_title(SCREEN, screen_width, screen_height, menu_timer)
        
        # Menu buttons
        button_width = int(screen_width * 0.25)
        button_height = int(screen_height * 0.09)
        button_x = (screen_width - button_width) // 2
        button_y_start = int(screen_height * 0.5)
        button_spacing = int(screen_height * 0.11)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Continue button (only if save exists)
        continue_rect = None
        if has_save:
            continue_rect = pygame.Rect(button_x, button_y_start, button_width, button_height)
            continue_hover = continue_rect.collidepoint(mouse_pos)
            
            pulse = int(25 * math.sin(menu_timer * 0.006))
            continue_color1 = tuple(min(255, c + pulse) for c in GREEN)
            continue_color2 = tuple(max(0, c - 30 + pulse) for c in DARK_GREEN)
            
            draw_menu_button_enhanced(SCREEN, continue_rect, "CONTINUE ADVENTURE", 
                                    continue_color1, continue_color2, continue_hover, BIG_FONT, menu_timer)
        
        # New Game button
        new_game_y = button_y_start + button_spacing if has_save else button_y_start
        new_game_rect = pygame.Rect(button_x, new_game_y, button_width, button_height)
        new_game_hover = new_game_rect.collidepoint(mouse_pos)
        
        if has_save:
            draw_menu_button_enhanced(SCREEN, new_game_rect, "NEW GAME", 
                                    ORANGE, (200, 100, 0), new_game_hover, BIG_FONT, menu_timer)
        else:
            draw_menu_button_enhanced(SCREEN, new_game_rect, "START ADVENTURE", 
                                    GREEN, DARK_GREEN, new_game_hover, BIG_FONT, menu_timer)
        
        # Settings button
        settings_y = new_game_y + button_spacing
        settings_rect = pygame.Rect(button_x, settings_y, button_width, button_height)
        settings_hover = settings_rect.collidepoint(mouse_pos)
        draw_menu_button_enhanced(SCREEN, settings_rect, "SETTINGS", 
                                DARK_BLUE, BLUE, settings_hover, BIG_FONT, menu_timer)
        
        # Quit button
        quit_y = settings_y + button_spacing
        quit_rect = pygame.Rect(button_x, quit_y, button_width, button_height)
        quit_hover = quit_rect.collidepoint(mouse_pos)
        draw_menu_button_enhanced(SCREEN, quit_rect, "EXIT GAME", 
                                DARK_RED, RED, quit_hover, BIG_FONT, menu_timer)
        
        # Delete save button (small, bottom left) - using text instead of emoji
        if has_save:
            delete_width = int(screen_width * 0.12)
            delete_height = int(screen_height * 0.05)
            delete_rect = pygame.Rect(25, screen_height - delete_height - 25, delete_width, delete_height)
            delete_hover = delete_rect.collidepoint(mouse_pos)
            draw_menu_button_enhanced(SCREEN, delete_rect, "Delete Save", 
                                    DARK_RED, RED, delete_hover, FONT, menu_timer)
        
        # Fullscreen button (top right)
        fs_button_x = screen_width - int(screen_width * 0.115)
        fs_button_y = int(screen_height * 0.046)
        fs_button_width = int(screen_width * 0.09)
        fs_button_height = int(screen_height * 0.038)
        fullscreen_button = create_fullscreen_button(fs_button_x, fs_button_y, fs_button_width, fs_button_height)
        draw_fullscreen_button(SCREEN, fullscreen_button, SMALL_FONT, mouse_pos)
        
        # Version info (bottom right)
        version_text = "v1.3.0 - Enhanced Edition"
        version_color = tuple(int(200 + 55 * math.sin(menu_timer * 0.002 + i * 0.1)) for i in range(3))
        draw_text_with_shadow(version_text, screen_width - 230, screen_height - 30, version_color, SMALL_FONT, 1)
        
        # Draw confirmation dialog
        if show_confirmation:
            # Darken background more
            confirm_overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            confirm_overlay.fill((0, 0, 0, 200))
            SCREEN.blit(confirm_overlay, (0, 0))
            
            # Animated confirmation panel
            panel_width = int(screen_width * 0.45)
            panel_height = int(screen_height * 0.35)
            panel_x = (screen_width - panel_width) // 2
            panel_y = (screen_height - panel_height) // 2
            
            # Panel with glow
            for i in range(6, 0, -1):
                glow_rect = pygame.Rect(panel_x - i*2, panel_y - i*2, panel_width + i*4, panel_height + i*4)
                glow_alpha = int(40 - i * 5)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*RED[:3], glow_alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=15)
                SCREEN.blit(glow_surf, glow_rect.topleft)
            
            panel_surface = pygame.Surface((panel_width, panel_height))
            panel_surface.fill(LIGHT_GRAY)
            SCREEN.blit(panel_surface, (panel_x, panel_y))
            pygame.draw.rect(SCREEN, RED, (panel_x, panel_y, panel_width, panel_height), 5, border_radius=15)
            
            # Warning icon animation (using text instead of emoji)
            icon_y = panel_y + 50
            icon_scale = 1.0 + 0.1 * math.sin(menu_timer * 0.008)
            icon_font = pygame.font.Font(None, int(64 * icon_scale))
            icon_surf = icon_font.render("!", True, BLACK)  # BLACK exclamation mark
            
            # Draw warning triangle manually
            triangle_size = 50
            triangle_x = panel_x + panel_width // 2
            triangle_y = icon_y
            
            # Draw red triangle
            triangle_points = [
                (triangle_x, triangle_y - triangle_size // 2),
                (triangle_x - triangle_size // 2, triangle_y + triangle_size // 2),
                (triangle_x + triangle_size // 2, triangle_y + triangle_size // 2)
            ]
            pygame.draw.polygon(SCREEN, RED, triangle_points)
            pygame.draw.polygon(SCREEN, BLACK, triangle_points, 3)
            
            # Draw BLACK exclamation mark in center
            icon_rect = icon_surf.get_rect(center=(triangle_x, triangle_y))
            SCREEN.blit(icon_surf, icon_rect)
            
            # Confirmation text
            if confirmation_type == 'new_game':
                title_text = "START NEW GAME?"
                warning_text = "This will permanently delete your current save!"
                confirm_text = "All progress will be lost forever."
            else:
                title_text = "DELETE SAVE FILE?"
                warning_text = "This will permanently delete all save data!"
                confirm_text = "This action cannot be undone."
            
            draw_text_with_shadow(title_text, panel_x + panel_width // 2 - 180, icon_y + 60, RED, BIG_FONT, 3)
            draw_text_with_shadow(warning_text, panel_x + 50, icon_y + 120, BLACK, FONT, 2)
            draw_text_with_shadow(confirm_text, panel_x + 80, icon_y + 150, DARK_GRAY, FONT, 1)
            
            # Yes/No buttons
            yes_width = int(panel_width * 0.35)
            yes_height = int(panel_height * 0.22)
            yes_rect = pygame.Rect(panel_x + 60, panel_y + panel_height - yes_height - 40, yes_width, yes_height)
            no_rect = pygame.Rect(panel_x + panel_width - yes_width - 60, panel_y + panel_height - yes_height - 40, yes_width, yes_height)
            
            yes_hover = yes_rect.collidepoint(mouse_pos)
            no_hover = no_rect.collidepoint(mouse_pos)
            
            draw_menu_button_enhanced(SCREEN, yes_rect, "YES", DARK_RED, RED, yes_hover, BIG_FONT, menu_timer)
            draw_menu_button_enhanced(SCREEN, no_rect, "NO", DARK_GREEN, GREEN, no_hover, BIG_FONT, menu_timer)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            
            elif handle_fullscreen_toggle(event):
                # Recreate particles for new resolution
                screen_width, screen_height = display_manager.get_size()
                particles.clear()
                for _ in range(30):
                    x = random.randint(0, screen_width)
                    y = random.randint(0, screen_height)
                    color = random.choice([GOLD, CYAN, PINK, PURPLE, YELLOW])
                    speed = random.uniform(0.5, 2.0)
                    particles.append(MenuParticle(x, y, color, speed))
                continue
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_confirmation:
                        show_confirmation = False
                    else:
                        return 'quit'
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                if show_confirmation:
                    if yes_rect.collidepoint((mx, my)):
                        if confirmation_type == 'new_game':
                            save_system.delete_save()
                            return 'new_game'
                        else:
                            save_system.delete_save()
                            show_confirmation = False
                            has_save = False
                            save_info = None
                    elif no_rect.collidepoint((mx, my)):
                        show_confirmation = False
                else:
                    if fullscreen_button.collidepoint((mx, my)):
                        display_manager.toggle_fullscreen()
                    
                    elif has_save and continue_rect and continue_rect.collidepoint((mx, my)):
                        return 'continue'
                    
                    elif new_game_rect.collidepoint((mx, my)):
                        if has_save:
                            show_confirmation = True
                            confirmation_type = 'new_game'
                        else:
                            return 'new_game'
                    
                    elif settings_rect.collidepoint((mx, my)):
                        from python.settings import settings_menu
                        settings_menu(sprites, battle_sprites, background)
                        # CRITICAL: Reload settings after returning from settings menu
                        if save_system.save_data:
                            saved_settings = save_system.save_data.get("settings", {})
                            game_settings.update(saved_settings)
                            print(f"Settings reloaded after settings menu: {game_settings}")
                    
                    elif quit_rect.collidepoint((mx, my)):
                        return 'quit'
                    
                    elif has_save and delete_rect.collidepoint((mx, my)):
                        show_confirmation = True
                        confirmation_type = 'delete_save'
        
        # Draw clock if enabled - NOW USES LOADED SETTING
        draw_real_time_clock(game_settings.get("show_clock", True))
        
        pygame.display.flip()
        CLOCK.tick(60)