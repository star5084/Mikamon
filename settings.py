import pygame, sys, os
from python.color import LIGHT_GRAY, DARK_GRAY, BLACK, WHITE, GREEN, DARK_GREEN, RED, DARK_RED, BLUE, DARK_BLUE, PURPLE, PINK, GRAY
from python.music import (play_title_music, play_fight_music, stop_all_music, update_music_volumes, fight_music_loaded, title_music_loaded, current_music_type, test_fight_volume)
from python.pygame1 import FONT, SMALL_FONT, BIG_FONT, CLOCK
from python.clock import draw_real_time_clock
from python.shadowed_text_and_buttons import draw_text_with_shadow, draw_gradient_button
from python.fullscreen_toggle import (
    display_manager, handle_fullscreen_toggle, scale_background_for_resolution
)

# Game settings dictionary with clock toggle
game_settings = {
    "music_volume": 0.1,
    "fight_music_volume": 0.1,
    "difficulty": "Normal",
    "show_clock": True,
    "show_ai_predictions": False
}

# Test volume cooldown tracker
test_volume_cooldown = 0

def settings_menu(sprites, battle_sprites, background):
    """Settings menu with music controls, clock toggle, and fullscreen toggle"""
    global game_settings, test_volume_cooldown
    settings_running = True
    
    while settings_running:
        # Get current screen and scale background
        SCREEN = display_manager.get_screen()
        screen_width, screen_height = display_manager.get_size()
        scaled_background = scale_background_for_resolution(background)
        SCREEN.blit(scaled_background, (0, 0))
        
        # Settings overlay
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        SCREEN.blit(overlay, (0, 0))
        
        # Responsive panel sizing
        panel_width = int(screen_width * 0.625)
        panel_height = int(screen_height * 0.722)
        panel_x = (screen_width - panel_width) // 2
        panel_y = int(screen_height * 0.139)
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.fill(LIGHT_GRAY)
        SCREEN.blit(panel_surface, panel_rect.topleft)
        pygame.draw.rect(SCREEN, BLACK, panel_rect, 4)
        
        # Title
        title_x = panel_x + panel_width // 2 - 150
        title_y = panel_y + int(panel_height * 0.038)
        draw_text_with_shadow("GAME SETTINGS", title_x, title_y, BLACK, BIG_FONT, 3)
        
        # Content positioning
        content_x = panel_x + int(panel_width * 0.033)
        y_pos = panel_y + int(panel_height * 0.15)

        # Music control buttons
        button_width = int(panel_width * 0.125)
        button_height = int(panel_height * 0.051)
        button_spacing = int(panel_width * 0.014)
        
        play_title_btn = pygame.Rect(content_x, y_pos, button_width, button_height)
        play_fight_btn = pygame.Rect(content_x + button_width + button_spacing, y_pos, button_width, button_height)
        stop_music_btn = pygame.Rect(content_x + 2 * (button_width + button_spacing), y_pos, button_width, button_height)
        
        current_time = pygame.time.get_ticks()
        test_available = current_time >= test_volume_cooldown
        test_fight_btn = pygame.Rect(content_x + 3 * (button_width + button_spacing), y_pos, button_width, button_height)
        
        draw_gradient_button("Play Title", play_title_btn, DARK_GREEN, GREEN, 
                           play_title_btn.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        draw_gradient_button("Play Fight", play_fight_btn, DARK_BLUE, BLUE, 
                           play_fight_btn.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        draw_gradient_button("Stop Music", stop_music_btn, DARK_RED, RED, 
                           stop_music_btn.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        
        if test_available:
            draw_gradient_button("Test Fight Vol", test_fight_btn, PURPLE, PINK, 
                               test_fight_btn.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        else:
            cooldown_remaining = (test_volume_cooldown - current_time) / 1000.0
            draw_gradient_button(f"Wait {cooldown_remaining:.1f}s", test_fight_btn, DARK_GRAY, GRAY, 
                               False, SMALL_FONT)
        
        # Difficulty selection
        y_pos += int(panel_height * 0.15)
        draw_text_with_shadow("Difficulty:", content_x, y_pos, BLACK, FONT)
        
        difficulties = ["Easy", "Normal", "Hard"]
        diff_buttons = []
        diff_button_width = int(panel_width * 0.1)
        diff_button_height = int(panel_height * 0.064)
        
        for i, diff in enumerate(difficulties):
            diff_rect = pygame.Rect(content_x + 150 + i * int(panel_width * 0.117), 
                                   y_pos, 
                                   diff_button_width, diff_button_height)
            diff_buttons.append((diff_rect, diff))
            
            if diff == game_settings["difficulty"]:
                draw_gradient_button(diff, diff_rect, GREEN, DARK_GREEN, False, SMALL_FONT)
            else:
                draw_gradient_button(diff, diff_rect, GRAY, DARK_GRAY, 
                                   diff_rect.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        
        # Difficulty description
        diff_descriptions = {
            "Easy": "AI uses random moves - Great for beginners",
            "Normal": "AI considers type effectiveness and weather",
            "Hard": "AI uses advanced strategy and adapts to battle conditions"
        }
        description_y = y_pos + int(panel_height * 0.1)
        draw_text_with_shadow(diff_descriptions[game_settings["difficulty"]], content_x, description_y, DARK_GRAY, SMALL_FONT)
        
        # Toggle options section
        y_pos += int(panel_height * 0.2)
        draw_text_with_shadow("Display Options:", content_x, y_pos, BLACK, FONT)
        
        # Clock toggle
        clock_toggle_y = y_pos + 35
        clock_toggle_rect = pygame.Rect(content_x + 150, clock_toggle_y, 200, 40)
        clock_enabled = game_settings.get("show_clock", True)
        clock_text = "Clock: ON" if clock_enabled else "Clock: OFF"
        clock_color1 = GREEN if clock_enabled else GRAY
        clock_color2 = DARK_GREEN if clock_enabled else DARK_GRAY
        draw_gradient_button(clock_text, clock_toggle_rect, clock_color1, clock_color2, 
                           clock_toggle_rect.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        
        # AI predictions toggle
        ai_toggle_y = clock_toggle_y + 50
        ai_toggle_rect = pygame.Rect(content_x + 150, ai_toggle_y, 200, 40)
        ai_enabled = game_settings.get("show_ai_predictions", False)
        ai_text = "AI Info: ON" if ai_enabled else "AI Info: OFF"
        ai_color1 = PURPLE if ai_enabled else GRAY
        ai_color2 = PINK if ai_enabled else DARK_GRAY
        draw_gradient_button(ai_text, ai_toggle_rect, ai_color1, ai_color2, 
                           ai_toggle_rect.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        
        # Music status indicators
        status_y = ai_toggle_y + 80
        draw_text_with_shadow("Music System Status:", content_x, status_y, BLACK, FONT)
        
        title_status = "Loaded & Ready" if title_music_loaded else "Not Found"
        fight_status = "Loaded & Ready" if fight_music_loaded else "Not Found"
        current_status = f"Currently Playing: {current_music_type.title() if current_music_type else 'None'}"
        
        title_color = GREEN if title_music_loaded else RED
        fight_color = GREEN if fight_music_loaded else RED
        current_color = BLUE if current_music_type else GRAY
        
        draw_text_with_shadow(f"Title Music (Title_Screen_music.*): {title_status}", content_x, status_y + 35, title_color, SMALL_FONT)
        draw_text_with_shadow(f"Fight Music (fight_music.wav): {fight_status}", content_x, status_y + 60, fight_color, SMALL_FONT)
        draw_text_with_shadow(current_status, content_x, status_y + 85, current_color, SMALL_FONT)
        
        # Back button
        back_button_width = int(panel_width * 0.167)
        back_button_height = int(panel_height * 0.077)
        back_x = panel_x + (panel_width - back_button_width) // 2
        back_y = panel_y + panel_height - back_button_height - int(panel_height * 0.026)
        
        back_rect = pygame.Rect(back_x, back_y, back_button_width, back_button_height)
        draw_gradient_button("BACK TO MENU", back_rect, DARK_BLUE, BLUE, 
                           back_rect.collidepoint(pygame.mouse.get_pos()), FONT)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.USEREVENT + 1:
                pygame.mixer.stop()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            elif handle_fullscreen_toggle(event):
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Save settings when exiting
                    try:
                        from python.save_system import save_system
                        if save_system.save_data:
                            save_system.update_settings(game_settings)
                    except:
                        pass
                    settings_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                if back_rect.collidepoint((mx, my)):
                    # Save settings when exiting
                    try:
                        from python.save_system import save_system
                        if save_system.save_data:
                            save_system.update_settings(game_settings)
                    except:
                        pass
                    settings_running = False
                
                elif play_title_btn.collidepoint((mx, my)):
                    if title_music_loaded:
                        play_title_music()
                elif play_fight_btn.collidepoint((mx, my)):
                    if fight_music_loaded:
                        play_fight_music()
                elif stop_music_btn.collidepoint((mx, my)):
                    stop_all_music()
                elif test_fight_btn.collidepoint((mx, my)) and test_available:
                    test_fight_volume()
                    test_volume_cooldown = current_time + 3000
                
                # Clock toggle
                elif clock_toggle_rect.collidepoint((mx, my)):
                    game_settings["show_clock"] = not game_settings.get("show_clock", True)
                    print(f"Clock display: {'ON' if game_settings['show_clock'] else 'OFF'}")
                
                # AI toggle
                elif ai_toggle_rect.collidepoint((mx, my)):
                    game_settings["show_ai_predictions"] = not game_settings.get("show_ai_predictions", False)
                    print(f"AI predictions: {'ON' if game_settings['show_ai_predictions'] else 'OFF'}")
                
                # Difficulty buttons
                for diff_rect, diff in diff_buttons:
                    if diff_rect.collidepoint((mx, my)):
                        game_settings["difficulty"] = diff
                        try:
                            from python.save_system import save_system
                            if save_system.save_data:
                                save_system.update_difficulty(diff)
                        except:
                            pass
        
        # Draw clock with toggle support
        draw_real_time_clock(game_settings.get("show_clock", True))
        pygame.display.flip()
        CLOCK.tick(60)