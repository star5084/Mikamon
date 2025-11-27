import pygame
from python.color import WHITE, BLACK, GRAY, DARK_GRAY, RED, DARK_RED, GOLD, BLUE, DARK_BLUE
from python.pygame1 import SCREEN, FONT, SMALL_FONT, BIG_FONT
from python.shadowed_text_and_buttons import draw_text_with_shadow, draw_gradient_button

# Global scroll position for item menu
item_scroll_position = 0

def draw_item_menu(inventory, current_category="All"):
    """Draw the item selection menu with scrolling support"""
    global item_scroll_position
    
    menu_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
    menu_surface.fill((0, 0, 0, 200))
    menu_x = (1920 - 800) // 2
    menu_y = (1080 - 600) // 2
    SCREEN.blit(menu_surface, (menu_x, menu_y))
    
    # Border
    pygame.draw.rect(SCREEN, GOLD, (menu_x, menu_y, 800, 600), 4)
    
    # Title
    draw_text_with_shadow("BATTLE ITEMS", menu_x + 300, menu_y + 20, GOLD, BIG_FONT, 2)
    
    # Category tabs
    categories = ["All", "Healing", "MP", "Stat", "Special"]
    tab_width = 140
    tab_y = menu_y + 70
    category_buttons = []
    
    for i, category in enumerate(categories):
        tab_x = menu_x + 40 + i * tab_width
        tab_rect = pygame.Rect(tab_x, tab_y, tab_width - 10, 40)
        category_buttons.append((tab_rect, category))
        
        if category == current_category:
            color1, color2 = GOLD, (200, 150, 0)
        else:
            color1, color2 = GRAY, DARK_GRAY
        
        hover = tab_rect.collidepoint(pygame.mouse.get_pos())
        draw_gradient_button(category, tab_rect, color1, color2, hover, SMALL_FONT)
    
    # Item list area
    items_area = pygame.Rect(menu_x + 20, menu_y + 120, 740, 380)  # Made slightly smaller for scroll bar
    pygame.draw.rect(SCREEN, (50, 50, 50, 180), items_area)
    pygame.draw.rect(SCREEN, WHITE, items_area, 2)
    
    # Get items for current category
    if current_category == "All":
        items = inventory.get_items_by_category()
    else:
        items = inventory.get_items_by_category(current_category)
    
    # Calculate scrolling parameters
    items_per_row = 2
    item_height = 80
    item_spacing = 10
    row_height = item_height + item_spacing
    visible_rows = items_area.height // row_height
    total_rows = (len(items) + items_per_row - 1) // items_per_row if items else 0
    max_scroll = max(0, total_rows - visible_rows)
    
    # Clamp scroll position
    item_scroll_position = max(0, min(item_scroll_position, max_scroll))
    
    # Display items with scrolling
    item_buttons = []
    if items:
        item_width = 350
        start_x = items_area.x + 10
        start_y = items_area.y + 10
        
        # Calculate which items to show based on scroll position
        start_item = item_scroll_position * items_per_row
        end_item = min(len(items), start_item + (visible_rows + 1) * items_per_row)  # Show one extra row for smooth scrolling
        
        for i in range(start_item, end_item):
            if i >= len(items):
                break
                
            item, quantity = items[i]
            display_index = i - start_item
            row = display_index // items_per_row
            col = display_index % items_per_row
            
            item_x = start_x + col * (item_width + 10)
            item_y = start_y + row * row_height
            
            # Only draw if within visible area
            if item_y < items_area.bottom - item_height:
                item_rect = pygame.Rect(item_x, item_y, item_width, item_height)
                
                # Check if item rect is actually visible in the clipping area
                if item_rect.bottom > items_area.y and item_rect.top < items_area.bottom:
                    item_buttons.append((item_rect, item))
                    
                    # Item background based on rarity
                    hover = item_rect.collidepoint(pygame.mouse.get_pos())
                    base_color = item.color
                    if hover:
                        base_color = tuple(min(255, c + 40) for c in base_color)
                    
                    darker_color = tuple(max(0, c - 60) for c in base_color)
                    draw_gradient_button("", item_rect, base_color, darker_color, False)
                    
                    # Item info
                    name_text = f"{item.name} x{quantity}"
                    draw_text_with_shadow(name_text, item_x + 10, item_y + 5, BLACK, SMALL_FONT)
                    
                    # Description
                    desc_lines = []
                    if len(item.description) > 40:
                        words = item.description.split()
                        current_line = ""
                        for word in words:
                            if len(current_line + word) > 40:
                                desc_lines.append(current_line.strip())
                                current_line = word + " "
                            else:
                                current_line += word + " "
                        if current_line.strip():
                            desc_lines.append(current_line.strip())
                    else:
                        desc_lines = [item.description]
                    
                    for j, line in enumerate(desc_lines[:2]):  # Max 2 lines
                        draw_text_with_shadow(line, item_x + 10, item_y + 25 + j * 15, DARK_GRAY, SMALL_FONT)
                    
                    # Rarity indicator
                    rarity_color = item.color
                    draw_text_with_shadow(f"[{item.rarity}]", item_x + 250, item_y + 55, rarity_color, SMALL_FONT)
        
        # Draw scroll bar if needed
        if max_scroll > 0:
            scroll_bar_x = menu_x + 760
            scroll_bar_y = items_area.y + 5
            scroll_bar_height = items_area.height - 10
            scroll_bar_width = 15
            
            # Scroll track
            pygame.draw.rect(SCREEN, DARK_GRAY, 
                           (scroll_bar_x, scroll_bar_y, scroll_bar_width, scroll_bar_height))
            
            # Scroll thumb
            if max_scroll > 0:
                thumb_height = max(20, int(scroll_bar_height * visible_rows / total_rows))
                thumb_y = scroll_bar_y + int((scroll_bar_height - thumb_height) * (item_scroll_position / max_scroll))
                pygame.draw.rect(SCREEN, WHITE, 
                               (scroll_bar_x, thumb_y, scroll_bar_width, thumb_height))
            
            # Scroll instructions
            draw_text_with_shadow("Use Mouse Wheel to Scroll", menu_x + 500, menu_y + 510, WHITE, SMALL_FONT)
    else:
        # No items message
        no_items_text = f"No {current_category.lower()} items available"
        draw_text_with_shadow(no_items_text, items_area.centerx - 100, items_area.centery, WHITE, FONT)
    
    # Close button
    close_rect = pygame.Rect(menu_x + 350, menu_y + 540, 100, 40)
    draw_gradient_button("CLOSE", close_rect, DARK_RED, RED, 
                        close_rect.collidepoint(pygame.mouse.get_pos()), FONT)
    
    return category_buttons, item_buttons, close_rect

def handle_item_menu_scroll(direction):
    """Handle scrolling in the item menu - direction: 1 for up, -1 for down"""
    global item_scroll_position
    
    if direction > 0:  # Scroll up
        item_scroll_position = max(0, item_scroll_position - 1)
    else:  # Scroll down
        item_scroll_position += 1

def reset_item_scroll():
    """Reset scroll position when changing categories or opening menu"""
    global item_scroll_position
    item_scroll_position = 0