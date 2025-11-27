import pygame
from python.fullscreen_toggle import display_manager
pygame.init()
SCREEN = display_manager.get_screen()
pygame.display.set_caption("Mikamon: Catgirl Chronicles")
FONT = pygame.font.SysFont("Arial", 24)
SMALL_FONT = pygame.font.SysFont("Arial", 18)
BIG_FONT = pygame.font.SysFont("Arial", 36, bold=True)
CLOCK = pygame.time.Clock()