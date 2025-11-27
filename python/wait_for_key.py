from python.pygame1 import SCREEN, FONT, CLOCK
from python.clock import draw_real_time_clock
from python.shadowed_text_and_buttons import draw_text_with_shadow
from python.color import YELLOW
import pygame, sys
def wait_for_key():
    """Wait for ESC key with visual feedback"""
    waiting = True
    blink_timer = 0
    
    while waiting:
        blink_timer += CLOCK.get_time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    break
        
        # Blinking prompt
        if (blink_timer // 500) % 2:
            screen_width, screen_height = SCREEN.get_size()
            center_x = screen_width // 2
            draw_text_with_shadow("Press ESC to continue...", center_x - 120, 500, YELLOW, FONT, 2)
        
        draw_real_time_clock()
        pygame.display.flip()
        CLOCK.tick(60)