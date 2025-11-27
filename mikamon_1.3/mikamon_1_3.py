import sys, random, os, math
os.environ['SDL_VIDEO_ALLOW_SCREENSAVER'] = '1'
os.environ['SDL_VIDEO_WINDOW_POS'] = 'centered'
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass
import pygame
from python.clock import draw_real_time_clock
from python.save_system import save_system
from python.main_menu import main_menu

# Initialize Pygame
from python.pygame1 import FONT, SMALL_FONT, BIG_FONT, CLOCK

# Initialize mixer BEFORE importing music functions
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
pygame.mixer.init()

# Verify mixer initialization
if not pygame.mixer.get_init():
    print("CRITICAL: Audio mixer not initialized properly!")
    print("Music will not work. Check your audio drivers.")
else:
    print("Audio mixer initialized successfully")

from python.music import (
    initialize_music_system, load_title_music, load_fight_music,
    play_title_music, play_fight_music, update_music_volumes,
    get_music_status, current_music_type
)

# Import fullscreen system
from python.fullscreen_toggle import (
    display_manager, handle_fullscreen_toggle, create_fullscreen_button,
    draw_fullscreen_button, get_scaled_coordinates, scale_background_for_resolution
)

def setup_music_system():
    """Setup the music system with proper initialization order"""
    print("Setting up music system...")
    
    # Step 1: Initialize the music file search system
    if not initialize_music_system():
        print("Failed to initialize music system")
        return False
    
    # Step 2: Load music files
    title_loaded = load_title_music()
    fight_loaded = load_fight_music()
    
    # Step 3: Get status
    status = get_music_status()
    
    print(f"Music system status:")
    print(f"  Mixer initialized: {status['mixer_initialized']}")
    print(f"  Title music loaded: {status['title_loaded']}")
    print(f"  Fight music loaded: {status['fight_loaded']}")
    
    # Step 4: Start title music if available
    if title_loaded:
        if play_title_music():
            print("Title music started successfully")
        else:
            print("Failed to start title music")
    else:
        print("Could not load title music - check file location")
        print("Expected location: music/Title_Screen_music.wav")
    
    if not fight_loaded:
        print("Could not load fight music - check file location")
        print("Expected location: music/fight_music.wav")
    
    return title_loaded or fight_loaded

# Call the setup function instead of individual calls
music_system_working = setup_music_system()

script_dir = os.path.dirname(os.path.abspath(__file__))

# Global game settings
game_settings = {
    "music_volume": 0.1,
    "fight_music_volume": 0.1,
    "difficulty": "Normal"
}

# Colors
from python.color import (WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY, GREEN, DARK_GREEN, BLUE,PURPLE, DARK_BLUE, GOLD, RED, DARK_RED, YELLOW, ORANGE, CYAN, PINK)
# Items system
from python.items import (get_item_by_name, player_inventory)
# AI system
from python.ai import get_skip_turn_move
from python.character_select_inventory import (
    draw_character_select_inventory, 
    handle_char_select_inv_scroll, 
    reset_char_select_inv_scroll
)
def load_sprite(filename, size=(80, 80), fallback_color=GRAY):
    """Load sprite image with fallback to colored rectangle with border"""
    try:
        if os.path.exists(filename):
            image = pygame.image.load(filename)
            return pygame.transform.scale(image, size)
    except:
        pass
    
    # Fallback with gradient effect
    surface = pygame.Surface(size)
    # Simple gradient
    for y in range(size[1]):
        shade = int(fallback_color[0] * (0.7 + 0.3 * y / size[1]))
        color = (shade, shade, shade) if fallback_color == GRAY else fallback_color
        pygame.draw.line(surface, color, (0, y), (size[0], y))
    
    pygame.draw.rect(surface, BLACK, (0, 0, size[0], size[1]), 2)
    return surface

def load_background():
    """Load background image with animated fallback"""
    try:
        if os.path.exists("mikamon_background.png"):
            image = pygame.image.load("mikamon_background.png")
            return pygame.transform.scale(image, (1920, 1080))
    except:
        pass
    
    # Animated background
    background = pygame.Surface((1920, 1080))
    
    for y in range(1080):
        # Blue to purple gradient with some variation
        t = y / 1080
        r = int(135 + math.sin(t * math.pi) * 50)
        g = int(206 - t * 50)
        b = int(250 - t * 50)
        color = (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))
        pygame.draw.line(background, color, (0, y), (1920, y))

    for i in range(20):
        x = random.randint(0, 1920)
        y = random.randint(0, 1080)
        size = random.randint(5, 15)
        alpha = random.randint(30, 80)
        color = (255, 255, 255, alpha)
        # Draw stars
        star_surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(star_surface, (255, 255, 255, alpha), (size, size), size)
        background.blit(star_surface, (x, y))
    
    return background

# Character data
from python.character_data import characters

def load_all_assets():
    sprites = {}
    battle_sprites = {}
    for name, char in characters.items():
        # Character button box
        sprites[name] = load_sprite(char["sprite_file"], (120, 120), char["color"])
        battle_sprites[name] = load_sprite(char["sprite_file"], (80, 80), char["color"])
    
    background = load_background()
    return sprites, battle_sprites, background   

# Shadowed text and buttons
from python.shadowed_text_and_buttons import draw_text_with_shadow, draw_gradient_button

def settings_menu(background):
    """Settings menu for volume and difficulty"""
    global game_settings
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
        
        # Responsive settings panel
        panel_width = int(screen_width * 0.521)  # About 1000px at 1920px
        panel_height = int(screen_height * 0.63)  # About 680px at 1080px
        panel_x = (screen_width - panel_width) // 2
        panel_y = int(screen_height * 0.185)  # About 200px at 1080px
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.fill(LIGHT_GRAY)
        SCREEN.blit(panel_surface, panel_rect.topleft)
        pygame.draw.rect(SCREEN, BLACK, panel_rect, 4)
        
        # Title
        title_x = panel_x + panel_width // 2 - 120
        title_y = panel_y + int(panel_height * 0.044)
        draw_text_with_shadow("GAME SETTINGS", title_x, title_y, BLACK, BIG_FONT, 3)
        
        # Volume sliders - responsive positioning
        content_x = panel_x + int(panel_width * 0.04)  # Left margin
        slider_x = panel_x + int(panel_width * 0.24)   # Slider position
        value_x = panel_x + int(panel_width * 0.82)    # Value display
        
        y_pos = panel_y + int(panel_height * 0.176)

        # Music Volume (Title Screen)
        draw_text_with_shadow("Title Music Volume:", content_x, y_pos, BLACK, FONT)
        slider_width = int(panel_width * 0.3)
        music_slider = pygame.Rect(slider_x, y_pos + 5, slider_width, 20)
        pygame.draw.rect(SCREEN, DARK_GRAY, music_slider)
        music_pos = int(game_settings["music_volume"] * slider_width)
        pygame.draw.circle(SCREEN, WHITE, (slider_x + music_pos, y_pos + 15), 12)
        pygame.draw.circle(SCREEN, BLACK, (slider_x + music_pos, y_pos + 15), 12, 2)
        draw_text_with_shadow(f"{int(game_settings['music_volume'] * 100)}%", value_x, y_pos, BLACK, FONT)
        
        # Fight Music Volume
        y_pos += int(panel_height * 0.118)
        draw_text_with_shadow("Fight Music Volume:", content_x, y_pos, BLACK, FONT)
        fight_music_slider = pygame.Rect(slider_x, y_pos + 5, slider_width, 20)
        pygame.draw.rect(SCREEN, DARK_GRAY, fight_music_slider)
        fight_music_pos = int(game_settings["fight_music_volume"] * slider_width)
        pygame.draw.circle(SCREEN, WHITE, (slider_x + fight_music_pos, y_pos + 15), 12)
        pygame.draw.circle(SCREEN, BLACK, (slider_x + fight_music_pos, y_pos + 15), 12, 2)
        draw_text_with_shadow(f"{int(game_settings['fight_music_volume'] * 100)}%", value_x, y_pos, BLACK, FONT)
        
        # Difficulty selection
        y_pos += int(panel_height * 0.176)
        draw_text_with_shadow("Difficulty:", content_x, y_pos, BLACK, FONT)
        
        difficulties = ["Easy", "Normal", "Hard"]
        diff_buttons = []
        diff_width = int(panel_width * 0.1)
        diff_height = int(panel_height * 0.074)
        
        for i, diff in enumerate(difficulties):
            diff_rect = pygame.Rect(slider_x + i * int(panel_width * 0.12), 
                                   y_pos + int(panel_height * 0.059), 
                                   diff_width, diff_height)
            diff_buttons.append((diff_rect, diff))
            
            if diff == game_settings["difficulty"]:
                draw_gradient_button(diff, diff_rect, GREEN, DARK_GREEN, False, SMALL_FONT)
            else:
                draw_gradient_button(diff, diff_rect, GRAY, DARK_GRAY, 
                                   diff_rect.collidepoint(pygame.mouse.get_pos()), SMALL_FONT)
        
        # Difficulty description
        diff_descriptions = {
            "Easy": "AI uses random moves",
            "Normal": "AI considers type effectiveness",
            "Hard": "AI uses advanced strategy"
        }
        desc_y = y_pos + int(panel_height * 0.162)
        draw_text_with_shadow(diff_descriptions[game_settings["difficulty"]], content_x, desc_y, DARK_GRAY, SMALL_FONT)
        
        # Music status indicators
        status_y = y_pos + int(panel_height * 0.265)
        draw_text_with_shadow("Music Status:", content_x, status_y, BLACK, FONT)
        title_status = "Loaded" if title_music_loaded else "Not Found"
        fight_status = "Loaded" if fight_music_loaded else "Not Found"
        title_color = GREEN if title_music_loaded else RED
        fight_color = GREEN if fight_music_loaded else RED
        
        draw_text_with_shadow(f"Title Music: {title_status}", content_x, status_y + 30, title_color, SMALL_FONT)
        draw_text_with_shadow(f"Fight Music: {fight_status}", content_x, status_y + 50, fight_color, SMALL_FONT)
        
        # Back button
        back_width = int(panel_width * 0.2)
        back_height = int(panel_height * 0.088)
        back_x = panel_x + (panel_width - back_width) // 2
        back_y = panel_y + panel_height - back_height - int(panel_height * 0.044)
        back_rect = pygame.Rect(back_x, back_y, back_width, back_height)
        draw_gradient_button("BACK", back_rect, DARK_BLUE, BLUE, 
                           back_rect.collidepoint(pygame.mouse.get_pos()), FONT)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle fullscreen toggle
            elif handle_fullscreen_toggle(event):
                continue
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    settings_running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if back_rect.collidepoint((mx, my)):
                    settings_running = False
                
                # Difficulty buttons
                for diff_rect, diff in diff_buttons:
                    if diff_rect.collidepoint((mx, my)):
                        game_settings["difficulty"] = diff
            elif event.type == pygame.MOUSEMOTION:
                mx, my = pygame.mouse.get_pos()
                if pygame.mouse.get_pressed()[0]:
                    # Title Music volume slider
                    if music_slider.colliderect(pygame.Rect(mx-10, my-10, 20, 20)):
                        relative_x = mx - music_slider.x
                        if 0 <= relative_x <= music_slider.width:
                            game_settings["music_volume"] = relative_x / music_slider.width
                            update_music_volumes()
                    # Fight Music volume slider
                    elif fight_music_slider.colliderect(pygame.Rect(mx-10, my-10, 20, 20)):
                        relative_x = mx - fight_music_slider.x
                        if 0 <= relative_x <= fight_music_slider.width:
                            game_settings["fight_music_volume"] = relative_x / fight_music_slider.width
                            update_music_volumes()
        if game_settings.get("show_clock", True):
            draw_real_time_clock(game_settings.get("show_clock", True))
        pygame.display.flip()
        CLOCK.tick(60)

# Battle system
from python.battle_system import battle

# Settings menu with fight music controls
from python.settings import game_settings, title_music_loaded, fight_music_loaded, update_music_volumes, settings_menu

# Character select with inventory display and fullscreen support
def character_select(sprites, battle_sprites, background):
    """Character select screen with animations, inventory display, and fullscreen support"""
    selected_char = None
    show_exit_menu = False
    show_inventory = False
    select_timer = 0
    hover_effects = {}
    # Auto-save inventory and settings when entering character select
    try:
        if save_system.save_data:
            save_system.update_inventory(player_inventory.items)
            save_system.update_settings(game_settings)
    except Exception as e:
        print(f"Auto-save error: {e}")
    while True:
        dt = CLOCK.get_time()
        select_timer += dt
        
        # Get current screen and dimensions
        SCREEN = display_manager.get_screen()
        screen_width, screen_height = display_manager.get_size()
        
        # Scale background to current resolution
        scaled_background = scale_background_for_resolution(background)
        SCREEN.blit(scaled_background, (0, 0))

        # Calculate responsive layout based on current resolution
        margin_x = int(screen_width * 0.03)  # 3% margin
        margin_y = int(screen_height * 0.04)  # 4% margin
        button_width = int(screen_width * 0.1875)  # 18.75% of screen width
        button_height = int(screen_height * 0.259)  # 25.9% of screen height
        padding = int(screen_width * 0.031)  # 3.1% padding

        # Dynamic overlay with breathing effect
        overlay_alpha = int(120 + 30 * math.sin(select_timer * 0.002))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((*WHITE[:3], overlay_alpha))
        SCREEN.blit(overlay, (0, 0))

        # Responsive title positioning
        title_x = int(screen_width * 0.0365)  # About 70px at 1920px width
        title_y = int(screen_height * 0.037)  # About 40px at 1080px height
        
        # Title with glow effect
        title_glow = int(50 + 30 * math.sin(select_timer * 0.003))
        for offset in range(5, 0, -1):
            title_color = (*GOLD[:3], title_glow)
            title_surface = BIG_FONT.render("MIKAMON: CATGIRL CHRONICLES", True, title_color)
            SCREEN.blit(title_surface, (title_x + offset, title_y + offset))
        
        draw_text_with_shadow("MIKAMON: CATGIRL CHRONICLES", title_x, title_y, BLACK, BIG_FONT, 3)
        
        subtitle_y = int(screen_height * 0.12)  # About 130px at 1080px height
        draw_text_with_shadow("Choose your fighter and enter the arena!", title_x, subtitle_y, DARK_GRAY, FONT, 1)

        # Fullscreen toggle button (top right corner)
        fs_button_x = screen_width - int(screen_width * 0.125)  # 12.5% from right edge
        fs_button_y = int(screen_height * 0.046)  # About 50px from top
        fs_button_width = int(screen_width * 0.094)  # About 180px at 1920px
        fs_button_height = int(screen_height * 0.032)  # About 35px at 1080px
        fullscreen_button = create_fullscreen_button(fs_button_x, fs_button_y, fs_button_width, fs_button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        draw_fullscreen_button(SCREEN, fullscreen_button, SMALL_FONT, mouse_pos)

        # Character grid with responsive positioning
        buttons = []
        x = margin_x
        y = int(screen_height * 0.185)  # About 200px at 1080px height
        col = 0
        chars_per_row = max(3, min(5, screen_width // (button_width + padding)))  # Responsive grid

        for name, char in characters.items():
            if col >= chars_per_row:
                x = margin_x
                y += button_height + padding
                col = 0

            rect = pygame.Rect(x, y, button_width, button_height)
            buttons.append((rect, name))

            hover = rect.collidepoint(mouse_pos)
            selected = (selected_char == name)
            
            # Initialize hover effect
            if name not in hover_effects:
                hover_effects[name] = 0
                
            # Update hover animation
            if hover:
                hover_effects[name] = min(hover_effects[name] + dt * 0.01, 1.0)
            else:
                hover_effects[name] = max(hover_effects[name] - dt * 0.008, 0.0)

            # Calculate colors with hover effects
            base_color = char["color"]
            hover_boost = int(hover_effects[name] * 40)
            button_color = tuple(min(255, max(0, c + hover_boost)) for c in base_color)
            
            if selected:
                pulse = int(40 * math.sin(select_timer * 0.008))
                button_color = tuple(min(255, c + 60 + pulse) for c in base_color)

            # Draw character card with gradient
            card_surface = pygame.Surface((button_width, button_height))
            for i in range(button_height):
                t = i / button_height
                color = tuple(int(button_color[j] * (0.7 + 0.3 * t)) for j in range(3))
                pygame.draw.line(card_surface, color, (0, i), (button_width, i))
            
            SCREEN.blit(card_surface, (x, y))
            
            # Border with selection glow
            border_width = 4 if selected else 2
            border_color = GOLD if selected else BLACK
            if selected:
                for thickness in range(8, 0, -2):
                    alpha = int(100 - thickness * 10)
                    glow_surface = pygame.Surface((button_width + thickness*2, button_height + thickness*2), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (*GOLD[:3], alpha), (0, 0, button_width + thickness*2, button_height + thickness*2), thickness)
                    SCREEN.blit(glow_surface, (x - thickness, y - thickness))
            pygame.draw.rect(SCREEN, border_color, rect, border_width)

            # Character sprite with bounce animation (scale sprite for resolution)
            if name in sprites:
                bounce = int(hover_effects[name] * 8 * math.sin(select_timer * 0.01))
                # Scale sprite size based on button size
                sprite_scale = min(button_width // 3, button_height // 4)
                scaled_sprite = pygame.transform.scale(sprites[name], (sprite_scale, sprite_scale))
                sprite_rect = scaled_sprite.get_rect()
                sprite_x = x + (button_width - sprite_rect.width) // 2
                sprite_y = y + int(button_height * 0.06) - bounce  # 6% from top of button
                SCREEN.blit(scaled_sprite, (sprite_x, sprite_y))

            # Character info with responsive sizing
            info_y = y + int(button_height * 0.5)
            text_x = x + int(button_width * 0.035)
            
            draw_text_with_shadow(name, text_x, info_y, BLACK, FONT, 1)
            
            # Type display with responsive sizing
            type_x = text_x
            type_width = max(60, button_width // 6)
            for i, char_type in enumerate(char["types"]):
                if type_x + type_width > x + button_width - 10:  # Wrap to next line
                    break
                    
                type_rect = pygame.Rect(type_x, info_y + 25, type_width, 20)
                type_color = {
                    "Grass": GREEN, "Oil": (139, 69, 19), "Light": YELLOW, "Star": PURPLE,
                    "Bonk": RED, "Mod": BLUE, "Imagination": PINK, "Miwiwi": CYAN,
                    "Crude Oil": DARK_GRAY, "Catgirl": PINK, "Car": ORANGE, 
                    "Miwawa": (255, 69, 0), "Human": (210, 180, 140)
                }.get(char_type, GRAY)
                
                pygame.draw.rect(SCREEN, type_color, type_rect)
                pygame.draw.rect(SCREEN, BLACK, type_rect, 1)
                
                type_text = SMALL_FONT.render(char_type[:6], True, BLACK)
                text_rect = type_text.get_rect(center=type_rect.center)
                SCREEN.blit(type_text, text_rect)
                type_x += type_width + 5
            
            # Stats display (condensed for smaller buttons)
            stats_y = info_y + 50
            line_height = int(button_height * 0.06)
            
            if button_height > 200:  # Full stats for large buttons
                stats_text = f"HP:{char['hp']} ATK:{char['attack']} DEF:{char['defense']}"
                draw_text_with_shadow(stats_text, text_x, stats_y, BLACK, SMALL_FONT)
                stats_text2 = f"SP.A:{char['special_attack']} SP.D:{char['special_defense']} SPD:{char['speed']}"
                draw_text_with_shadow(stats_text2, text_x, stats_y + line_height, BLACK, SMALL_FONT)
                energy_text = f"MAX MP:{char.get('max_energy', 100)} REGEN:{char.get('energy_regen', 15)}"
                draw_text_with_shadow(energy_text, text_x, stats_y + line_height * 2, BLACK, SMALL_FONT)
                
                # Show Skip Turn regeneration info
                skip_data = get_skip_turn_move(char)
                skip_regen = skip_data.get("mp_regeneration", 0)
                skip_text = f"Skip Turn: +{skip_regen} MP"
                draw_text_with_shadow(skip_text, text_x, stats_y + line_height * 3, BLACK, SMALL_FONT)
            else:  # Condensed stats for smaller buttons
                stats_text = f"HP:{char['hp']} ATK:{char['attack']}"
                draw_text_with_shadow(stats_text, text_x, stats_y, BLACK, SMALL_FONT)
                stats_text2 = f"DEF:{char['defense']} SPD:{char['speed']}"
                draw_text_with_shadow(stats_text2, text_x, stats_y + line_height, BLACK, SMALL_FONT)
            
            x += button_width + padding
            col += 1
        
        # Responsive Start button
        battle_width = int(screen_width * 0.208)  # About 400px at 1920px
        battle_height = int(screen_height * 0.056)  # About 60px at 1080px
        battle_rect = pygame.Rect((screen_width - battle_width) // 2, 
                                screen_height - int(screen_height * 0.13), 
                                battle_width, battle_height)
        
        if selected_char:
            pulse_color = int(30 * math.sin(select_timer * 0.01))
            start_color1 = tuple(min(255, c + pulse_color) for c in GREEN)
            start_color2 = tuple(max(0, c - 30 + pulse_color) for c in GREEN)
            draw_gradient_button("START EPIC BATTLE!", battle_rect, start_color1, start_color2, 
                               battle_rect.collidepoint(mouse_pos), BIG_FONT)
        else:
            draw_gradient_button("Select a Character First", battle_rect, GRAY, DARK_GRAY, False, FONT)

        # Responsive menu buttons (left side)
        menu_width = int(screen_width * 0.104)  # About 200px at 1920px
        menu_height = int(screen_height * 0.046)  # About 50px at 1080px
        menu_x = int(screen_width * 0.026)  # About 50px at 1920px
        
        menu_rect = pygame.Rect(menu_x, screen_height - int(screen_height * 0.194), menu_width, menu_height)
        settings_rect = pygame.Rect(menu_x, screen_height - int(screen_height * 0.139), menu_width, menu_height)
        inventory_rect = pygame.Rect(menu_x, screen_height - int(screen_height * 0.083), menu_width, menu_height)
        
        draw_gradient_button("MENU", menu_rect, DARK_GRAY, GRAY, menu_rect.collidepoint(mouse_pos), FONT)
        draw_gradient_button("SETTINGS", settings_rect, DARK_BLUE, BLUE, settings_rect.collidepoint(mouse_pos), FONT)
        
        # Inventory button with item count
        inventory_count = len([item for item, qty in player_inventory.items.items() if qty > 0])
        inventory_text = f"ITEMS ({inventory_count})" if inventory_count > 0 else "ITEMS (Empty)"
        inventory_color = GOLD if inventory_count > 0 else DARK_GRAY
        inventory_color2 = tuple(max(0, c - 40) for c in inventory_color)
        draw_gradient_button(inventory_text, inventory_rect, inventory_color, inventory_color2, 
                           inventory_rect.collidepoint(mouse_pos), FONT)
        
        # Responsive music/system info (bottom right)
        info_x = screen_width - int(screen_width * 0.156)  # About 300px from right
        info_y = screen_height - int(screen_height * 0.148)  # About 160px from bottom
        
        music_info = f"Music: {current_music_type.title() if current_music_type else 'None'}"
        draw_text_with_shadow(music_info, info_x, info_y, CYAN, SMALL_FONT)
        
        audio_status = "Audio: OK" if (title_music_loaded or fight_music_loaded) else "Audio: Check Files"
        audio_color = GREEN if (title_music_loaded or fight_music_loaded) else RED
        draw_text_with_shadow(audio_status, info_x, info_y + 20, audio_color, SMALL_FONT)
        
        # Difficulty indicator
        diff_rect = pygame.Rect(info_x, screen_height - int(screen_height * 0.083), 
                               int(screen_width * 0.13), int(screen_height * 0.037))
        diff_color = {"Easy": GREEN, "Normal": YELLOW, "Hard": RED}[game_settings["difficulty"]]
        draw_gradient_button(f"Difficulty: {game_settings['difficulty']}", diff_rect, 
                           diff_color, tuple(max(0, c - 40) for c in diff_color), False, SMALL_FONT)
        
        # Handle inventory display with scrolling
        if show_inventory:
            close_inv_rect = draw_character_select_inventory(player_inventory, screen_width, screen_height)
        
        # Exit menu with responsive sizing
        if show_exit_menu:
            menu_width = int(screen_width * 0.3125)  # About 600px at 1920px
            menu_height = int(screen_height * 0.37)   # About 400px at 1080px
            menu_surface = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            menu_surface.fill((0, 0, 0, 220))
            menu_x = (screen_width - menu_width) // 2
            menu_y = (screen_height - menu_height) // 2
            SCREEN.blit(menu_surface, (menu_x, menu_y))
            
            pygame.draw.rect(SCREEN, GOLD, (menu_x, menu_y, menu_width, menu_height), 4)
            draw_text_with_shadow("MAIN MENU", menu_x + menu_width//3, menu_y + 40, GOLD, BIG_FONT, 2)
            
            # Menu options with responsive sizing
            button_width = int(menu_width * 0.33)  # 1/3 of menu width
            button_height = int(menu_height * 0.2)  # 1/5 of menu height
            
            quit_game = pygame.Rect(menu_x + menu_width//2 - button_width//2, 
                                   menu_y + int(menu_height * 0.375), 
                                   button_width, button_height)
            resume_game = pygame.Rect(menu_x + menu_width//2 - button_width//2, 
                                     menu_y + int(menu_height * 0.625), 
                                     button_width, button_height)
            
            draw_gradient_button("QUIT GAME", quit_game, DARK_RED, RED, 
                               quit_game.collidepoint(mouse_pos), FONT)
            draw_gradient_button("RESUME", resume_game, DARK_GREEN, GREEN, 
                               resume_game.collidepoint(mouse_pos), FONT)
        
        # Event handling with fullscreen support
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Handle fullscreen toggle (F11, Alt+Enter, Ctrl+F) - PRIORITY
            elif handle_fullscreen_toggle(event):
                continue  # Screen reference will be updated in next loop iteration
                
            elif event.type == pygame.USEREVENT + 1:
                # Stop test music after 1 second
                pygame.mixer.stop()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel timer
                
            elif event.type == pygame.MOUSEWHEEL:
                # Handle inventory scrolling
                if show_inventory:
                    handle_char_select_inv_scroll(event.y)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_inventory:
                        show_inventory = False
                    else:
                        show_exit_menu = not show_exit_menu
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                # Fullscreen button click
                if fullscreen_button.collidepoint((mx, my)):
                    display_manager.toggle_fullscreen()
                    
                elif show_inventory:
                    if close_inv_rect.collidepoint((mx, my)):
                        show_inventory = False
                        
                elif show_exit_menu:
                    if quit_game.collidepoint((mx, my)):
                        pygame.quit()
                        sys.exit()
                    elif resume_game.collidepoint((mx, my)):
                        show_exit_menu = False
                        
                elif menu_rect.collidepoint((mx, my)):
                    show_exit_menu = not show_exit_menu
                    
                elif settings_rect.collidepoint((mx, my)):
                    settings_menu(sprites, battle_sprites, background)
                    
                elif inventory_rect.collidepoint((mx, my)):
                    show_inventory = True
                    reset_char_select_inv_scroll()
                    
                elif not show_exit_menu:
                    # Character selection
                    for rect, name in buttons:
                        if rect.collidepoint((mx, my)):
                            selected_char = name
                            break
                    
                    # Start battle
                    if selected_char and battle_rect.collidepoint((mx, my)):
                        battle(selected_char, sprites, battle_sprites, background)
        
        if game_settings.get("show_clock", True):
            draw_real_time_clock(game_settings.get("show_clock", True))
        pygame.display.flip()
        CLOCK.tick(60)

def main():
    """Main game function with save system and main menu"""
    print("Loading Mikamon...")
    print("Initializing audio systems...")
    
    # Display music system status
    status = get_music_status()
    if status['mixer_initialized']:
        print("Audio mixer: OK")
    else:
        print("Audio mixer: FAILED")
    
    if status['title_loaded']:
        print("Title music: Loaded")
    else:
        print("Title music: Missing")
    
    if status['fight_loaded']:
        print("Fight music: Loaded") 
    else:
        print("Fight music: Missing")
    
    print("Loading sprites and assets...")
    sprites, battle_sprites, background = load_all_assets()
    
    # Show loading screen
    SCREEN = display_manager.get_screen()
    screen_width, screen_height = display_manager.get_size()
    
    SCREEN.fill(BLACK)
    loading_text = BIG_FONT.render("MIKAMON: CATGIRL CHRONICLES", True, GOLD)
    loading_rect = loading_text.get_rect(center=(screen_width//2, screen_height//2 - 50))
    SCREEN.blit(loading_text, loading_rect)
    
    if music_system_working:
        subtitle_text = FONT.render("Loading Mikamon", True, WHITE)
    else:
        subtitle_text = FONT.render("Loading Mikamon (Music files not found)", True, ORANGE)
    subtitle_rect = subtitle_text.get_rect(center=(screen_width//2, screen_height//2))
    SCREEN.blit(subtitle_text, subtitle_rect)

    if game_settings.get("show_clock", True):
        draw_real_time_clock(game_settings.get("show_clock", True))
    pygame.display.flip()
    pygame.time.wait(2000)
    
    # Main menu loop
    while True:
        menu_choice = main_menu(sprites, battle_sprites, background)
        
        if menu_choice == 'quit':
            pygame.quit()
            sys.exit()
        
        elif menu_choice == 'new_game':
            print("Starting new game...")
            # Create new save with default difficulty
            save_data = save_system.create_new_save(game_settings["difficulty"])
            
            # Load settings from save
            game_settings.update(save_data["settings"])
            
            # Reset inventory
            player_inventory.items = save_data["inventory"].copy()
            
            # Clear permanent character stats
            from python.permanent_hp_system import permanent_character_stats
            permanent_character_stats.reset_all()
            
            print("New game created!")
            character_select(sprites, battle_sprites, background)
        
        elif menu_choice == 'continue':
            print("Loading saved game...")
            save_data = save_system.load_game()
            
            if save_data:
                # Load all saved data
                game_settings["difficulty"] = save_data.get("difficulty", "Normal")
                game_settings.update(save_data.get("settings", {}))
                
                # Restore inventory
                player_inventory.items = save_data.get("inventory", {}).copy()
                
                print(f"Game loaded! Difficulty: {game_settings['difficulty']}")
                print(f"Items: {len(player_inventory.items)}")
                character_select(sprites, battle_sprites, background)
            else:
                print("Failed to load save, starting new game...")
                save_system.create_new_save(game_settings["difficulty"])
                character_select(sprites, battle_sprites, background)

if __name__ == "__main__":
    main()