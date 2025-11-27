import time
from python.pygame1 import SCREEN, FONT

def draw_real_time_clock(show_clock=True):
    """Draw clock only if enabled in settings"""
    if not show_clock:
        return
    
    current_time_str = time.strftime("%H:%M:%S")
    clock_surface = FONT.render(current_time_str, True, (255, 255, 255))
    clock_rect = clock_surface.get_rect(topright=(SCREEN.get_width() - 20, 10))
    SCREEN.blit(clock_surface, clock_rect)