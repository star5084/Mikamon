import pygame
import sys

class DisplayManager:
    """Manages display settings and fullscreen toggling"""
    def __init__(self, default_width=1920, default_height=1020):
        self.default_width = default_width
        self.default_height = default_height
        self.is_fullscreen = False
        self.screen = None
        self.fullscreen_size = None
        self.windowed_size = (default_width, default_height)
        
        # Initialize display
        self.initialize_display()
    
    def initialize_display(self):
        """Initialize the display with default windowed mode"""
        pygame.display.init()
        
        # Get available fullscreen resolutions
        modes = pygame.display.list_modes()
        if modes and modes != -1:
            self.fullscreen_size = modes[0]  # Largest available resolution
        else:
            self.fullscreen_size = (1920, 1080)  # Fallback
        
        # Start in windowed mode
        self.screen = pygame.display.set_mode(self.windowed_size)
        pygame.display.set_caption("Mikamon: Catgirl Chronicles")
        
        return self.screen
    
    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode"""
        if self.is_fullscreen:
            # Switch to windowed
            self.screen = pygame.display.set_mode(self.windowed_size)
            self.is_fullscreen = False
            pygame.display.set_caption("Mikamon: Catgirl Chronicles")
            print(f"Switched to windowed mode: {self.windowed_size}")
        else:
            # Switch to fullscreen
            self.screen = pygame.display.set_mode(self.fullscreen_size, pygame.FULLSCREEN)
            self.is_fullscreen = True
            print(f"Switched to fullscreen mode: {self.fullscreen_size}")
        
        return self.screen
    
    def get_screen(self):
        """Get current screen surface"""
        return self.screen
    
    def get_size(self):
        """Get current screen size"""
        return self.screen.get_size() if self.screen else self.windowed_size
    
    def get_display_info(self):
        """Get information about current display mode"""
        return {
            'is_fullscreen': self.is_fullscreen,
            'current_size': self.get_size(),
            'windowed_size': self.windowed_size,
            'fullscreen_size': self.fullscreen_size
        }

# Global display manager instance
display_manager = DisplayManager()

def handle_fullscreen_toggle(event):
    """
    Handle fullscreen toggle key events
    Call this in your main event loop
    
    Supports:
    - F11 key
    - Alt + Enter
    - Ctrl + F (alternative)
    """
    if event.type == pygame.KEYDOWN:
        # F11 key
        if event.key == pygame.K_F11:
            display_manager.toggle_fullscreen()
            return True
        
        # Alt + Enter
        elif event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT):
            display_manager.toggle_fullscreen()
            return True
        
        # Ctrl + F as alternative
        elif event.key == pygame.K_f and (event.mod & pygame.KMOD_CTRL):
            display_manager.toggle_fullscreen()
            return True
    
    return False

def create_fullscreen_button(x, y, width=200, height=40):
    """Create a fullscreen toggle button rect"""
    return pygame.Rect(x, y, width, height)

def draw_fullscreen_button(screen, button_rect, font, mouse_pos=None):
    """
    Draw the fullscreen toggle button
    Returns the button rect for click detection
    """
    # Import colors with fallback
    try:
        from python.color import DARK_BLUE, BLUE, WHITE, BLACK
        from python.shadowed_text_and_buttons import draw_gradient_button
    except ImportError:
        # Fallback colors if imports fail
        DARK_BLUE = (0, 0, 139)
        BLUE = (0, 0, 255)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        
        def draw_gradient_button(text, rect, color1, color2, hover, font):
            color = color2 if hover else color1
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            
            text_surface = font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
    
    # Determine button text and hover state
    button_text = "EXIT FULLSCREEN" if display_manager.is_fullscreen else "FULLSCREEN"
    is_hover = mouse_pos and button_rect.collidepoint(mouse_pos)
    
    # Draw the button
    draw_gradient_button(button_text, button_rect, DARK_BLUE, BLUE, is_hover, font)
    
    return button_rect

def get_scaled_coordinates(original_coords, original_size=(1920, 1080)):
    """
    Scale coordinates from original design resolution to current screen size
    Useful for maintaining UI layout across different resolutions
    
    Args:
        original_coords: (x, y) tuple of coordinates in original resolution
        original_size: (width, height) of original design resolution
    
    Returns:
        (x, y) tuple scaled to current resolution
    """
    current_size = display_manager.get_size()
    scale_x = current_size[0] / original_size[0]
    scale_y = current_size[1] / original_size[1]
    
    return (
        int(original_coords[0] * scale_x),
        int(original_coords[1] * scale_y)
    )

def get_scaled_rect(original_rect, original_size=(1920, 1080)):
    """
    Scale a pygame.Rect from original design resolution to current screen size
    
    Args:
        original_rect: pygame.Rect in original resolution
        original_size: (width, height) of original design resolution
    
    Returns:
        pygame.Rect scaled to current resolution
    """
    current_size = display_manager.get_size()
    scale_x = current_size[0] / original_size[0]
    scale_y = current_size[1] / original_size[1]
    
    return pygame.Rect(
        int(original_rect.x * scale_x),
        int(original_rect.y * scale_y),
        int(original_rect.width * scale_x),
        int(original_rect.height * scale_y)
    )

def scale_surface(surface, original_size=(1920, 1080)):
    """
    Scale a surface to current screen resolution
    
    Args:
        surface: pygame.Surface to scale
        original_size: (width, height) of original design resolution
    
    Returns:
        Scaled pygame.Surface
    """
    current_size = display_manager.get_size()
    if current_size == original_size:
        return surface
    
    return pygame.transform.scale(surface, current_size)

def scale_background_for_resolution(background_surface, original_size=(1920, 1080)):
    """
    Scale background image to current resolution
    
    Args:
        background_surface: Original background surface
        original_size: Original design resolution
    
    Returns:
        Scaled background surface
    """
    current_size = display_manager.get_size()
    if current_size != original_size:
        return pygame.transform.scale(background_surface, current_size)
    return background_surface

def create_responsive_layout():
    """
    Example of creating a responsive layout that works in both windowed and fullscreen
    """
    current_size = display_manager.get_size()
    
    # Calculate responsive dimensions
    margin_ratio = 0.03  # 3% margins
    button_width_ratio = 0.18  # 18% of screen width
    button_height_ratio = 0.26  # 26% of screen height
    
    margin_x = int(current_size[0] * margin_ratio)
    margin_y = int(current_size[1] * margin_ratio)
    button_width = int(current_size[0] * button_width_ratio)
    button_height = int(current_size[1] * button_height_ratio)
    
    return {
        'margin_x': margin_x,
        'margin_y': margin_y,
        'button_width': button_width,
        'button_height': button_height,
        'screen_width': current_size[0],
        'screen_height': current_size[1]
    }

def draw_display_debug_info(screen, font, x=10, y=10):
    """
    Draw debug information about current display mode
    Useful for development and troubleshooting
    """
    try:
        from python.color import WHITE, BLACK
        from python.shadowed_text_and_buttons import draw_text_with_shadow
    except ImportError:
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        def draw_text_with_shadow(text, x, y, color, font, shadow=1):
            text_surface = font.render(text, True, color)
            screen.blit(text_surface, (x, y))
    
    info = display_manager.get_display_info()
    debug_lines = [
        f"Display Mode: {'Fullscreen' if info['is_fullscreen'] else 'Windowed'}",
        f"Current: {info['current_size'][0]}x{info['current_size'][1]}",
        f"Windowed: {info['windowed_size'][0]}x{info['windowed_size'][1]}",
        f"Fullscreen: {info['fullscreen_size'][0]}x{info['fullscreen_size'][1]}",
        "Toggle: F11, Alt+Enter, Ctrl+F"
    ]
    
    for i, line in enumerate(debug_lines):
        draw_text_with_shadow(line, x, y + i * 20, WHITE, font, 1)