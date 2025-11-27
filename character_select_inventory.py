import pygame
from python.color import WHITE, BLACK, GRAY, DARK_GRAY, RED, DARK_RED, GOLD, BLUE, DARK_BLUE, GREEN, PURPLE, CYAN
from python.shadowed_text_and_buttons import draw_text_with_shadow, draw_gradient_button
from python.pygame1 import FONT, SMALL_FONT, BIG_FONT

# Global scroll position for character select inventory
char_select_inv_scroll = 0

def draw_character_select_inventory(player_inventory, screen_width, screen_height):
    """Draw the inventory display in character select with scrolling support"""
    global char_select_inv_scroll
    
    inv_width = int(screen_width * 0.3125)  # About 600px at 1920px
    inv_height = int(screen_height * 0.463)  # About 500px at 1080px
    inv_surface = pygame.Surface((inv_width, inv_height), pygame.SRCALPHA)
    inv_surface.fill((0, 0, 0, 200))
    inv_x = (screen_width - inv_width) // 2
    inv_y = (screen_height - inv_height) // 2
    
    from python.pygame1 import SCREEN
    SCREEN.blit(inv_surface, (inv_x, inv_y))
    pygame.draw.rect(SCREEN, GOLD, (inv_x, inv_y, inv_width, inv_height), 4)
    
    # Title
    title_text = "BATTLE INVENTORY"
    title_width = BIG_FONT.size(title_text)[0]
    title_x = inv_x + (inv_width - title_width) // 2
    draw_text_with_shadow(title_text, title_x, inv_y + 20, GOLD, BIG_FONT, 2)
    
    # Close button at top right
    close_inv_rect = pygame.Rect(inv_x + inv_width - 120, inv_y + 15, 100, 40)
    mouse_pos = pygame.mouse.get_pos()
    draw_gradient_button("CLOSE", close_inv_rect, DARK_RED, RED, 
                        close_inv_rect.collidepoint(mouse_pos), FONT)
    
    # Items display area
    items_area = pygame.Rect(inv_x + 20, inv_y + 70, inv_width - 60, inv_height - 130)
    pygame.draw.rect(SCREEN, (30, 30, 30, 180), items_area)
    pygame.draw.rect(SCREEN, GOLD, items_area, 2)
    
    if player_inventory.items:
        # Get all items with quantities > 0
        items_list = [(item_name, quantity) for item_name, quantity in player_inventory.items.items() if quantity > 0]
        
        if items_list:
            # Calculate scrolling parameters
            item_height = 65
            item_spacing = 5
            total_item_height = item_height + item_spacing
            visible_items = items_area.height // total_item_height
            total_items = len(items_list)
            max_scroll = max(0, total_items - visible_items)
            
            # Clamp scroll position
            char_select_inv_scroll = max(0, min(char_select_inv_scroll, max_scroll))
            
            # Display items with scrolling
            start_item = char_select_inv_scroll
            end_item = min(total_items, start_item + visible_items + 1)  # Show one extra for smooth scrolling
            
            from python.items import get_item_by_name
            
            for i in range(start_item, end_item):
                if i >= total_items:
                    break
                
                item_name, quantity = items_list[i]
                item = get_item_by_name(item_name)
                if not item:
                    continue
                
                display_index = i - start_item
                item_y = items_area.y + 10 + display_index * total_item_height
                
                # Only draw if within visible area
                if item_y < items_area.bottom - item_height and item_y + item_height > items_area.y:
                    # Item background
                    item_rect = pygame.Rect(items_area.x + 10, item_y, items_area.width - 40, item_height)
                    
                    # Gradient background based on rarity
                    base_color = item.color
                    darker_color = tuple(max(0, c - 50) for c in base_color)
                    
                    for y in range(item_height):
                        t = y / item_height
                        color = tuple(int(base_color[j] * (1 - t * 0.3)) for j in range(3))
                        pygame.draw.line(SCREEN, color, 
                                       (item_rect.x, item_rect.y + y), 
                                       (item_rect.right, item_rect.y + y))
                    
                    pygame.draw.rect(SCREEN, BLACK, item_rect, 2)
                    
                    # Item name and quantity
                    item_text = f"{item_name} x{quantity}"
                    draw_text_with_shadow(item_text, item_rect.x + 10, item_rect.y + 5, BLACK, FONT)
                    
                    # Description (truncated if too long)
                    desc = item.description
                    if len(desc) > 45:
                        desc = desc[:42] + "..."
                    draw_text_with_shadow(desc, item_rect.x + 15, item_rect.y + 28, BLACK, SMALL_FONT)
                    
                    # Rarity indicator
                    rarity_text = f"[{item.rarity}]"
                    rarity_width = SMALL_FONT.size(rarity_text)[0]
                    draw_text_with_shadow(rarity_text, item_rect.right - rarity_width - 10, 
                                        item_rect.y + 8, item.color, SMALL_FONT)
            
            # Draw scroll bar if needed
            if max_scroll > 0:
                scroll_bar_x = inv_x + inv_width - 35
                scroll_bar_y = items_area.y + 5
                scroll_bar_height = items_area.height - 10
                scroll_bar_width = 12
                
                # Scroll track
                pygame.draw.rect(SCREEN, DARK_GRAY, 
                               (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
                pygame.draw.rect(SCREEN, BLACK, 
                               (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height), 1)
                
                # Scroll thumb
                if max_scroll > 0:
                    thumb_height = max(30, int(scroll_bar_height * visible_items / total_items))
                    thumb_y = scroll_bar_y + int((scroll_bar_height - thumb_height) * (char_select_inv_scroll / max_scroll))
                    pygame.draw.rect(SCREEN, GOLD, 
                                   (scroll_bar_x, thumb_y, scroll_bar_width, thumb_height))
                    pygame.draw.rect(SCREEN, BLACK, 
                                   (scroll_bar_x, thumb_y, scroll_bar_width, thumb_height), 1)
                
                # Scroll instructions
                scroll_text = "Scroll: Mouse Wheel"
                scroll_width = SMALL_FONT.size(scroll_text)[0]
                draw_text_with_shadow(scroll_text, inv_x + (inv_width - scroll_width) // 2, 
                                    inv_y + inv_height - 45, WHITE, SMALL_FONT)
        else:
            # No items with quantity > 0
            no_items_text = "Inventory is empty"
            text_width = FONT.size(no_items_text)[0]
            draw_text_with_shadow(no_items_text, 
                                inv_x + (inv_width - text_width) // 2, 
                                inv_y + inv_height // 2, 
                                WHITE, FONT)
    else:
        # No items at all
        no_items_text = "No items in inventory"
        text_width = FONT.size(no_items_text)[0]
        draw_text_with_shadow(no_items_text, 
                            inv_x + (inv_width - text_width) // 2, 
                            inv_y + inv_height // 2, 
                            WHITE, FONT)
    
    return close_inv_rect

def handle_char_select_inv_scroll(direction):
    """Handle scrolling in character select inventory - direction: 1 for up, -1 for down"""
    global char_select_inv_scroll
    
    if direction > 0:  # Scroll up
        char_select_inv_scroll = max(0, char_select_inv_scroll - 1)
    else:  # Scroll down
        char_select_inv_scroll += 1

def reset_char_select_inv_scroll():
    """Reset scroll position when opening inventory"""
    global char_select_inv_scroll
    char_select_inv_scroll = 0