"""
Enhanced Day/Night Cycle System with Custom Graphics
Provides time-based bonuses with beautiful visual effects
Uses PIL, NumPy, and Pytweening for smooth animations
"""

import datetime
import pygame
import math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance
import pytweening
from python.color import YELLOW, ORANGE, PURPLE, DARK_BLUE, CYAN, PINK, WHITE, BLACK, RED

class TimeIconRenderer:
    """Renders custom time-of-day icons without using emojis"""
    
    def __init__(self):
        self.icon_cache = {}
    
    def create_sunrise_icon(self, size=40):
        """Create a sunrise icon (morning)"""
        if ('sunrise', size) in self.icon_cache:
            return self.icon_cache[('sunrise', size)]
        
        # Create PIL image
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Sun (half visible)
        sun_center = (size // 2, int(size * 0.7))
        sun_radius = int(size * 0.25)
        
        # Sun glow
        for i in range(5):
            glow_radius = sun_radius + i * 3
            alpha = int(100 - i * 15)
            draw.ellipse([sun_center[0] - glow_radius, sun_center[1] - glow_radius,
                         sun_center[0] + glow_radius, sun_center[1] + glow_radius],
                        fill=(255, 220, 100, alpha))
        
        # Sun core
        draw.ellipse([sun_center[0] - sun_radius, sun_center[1] - sun_radius,
                     sun_center[0] + sun_radius, sun_center[1] + sun_radius],
                    fill=(255, 200, 50, 255))
        
        # Sun rays
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            start_x = sun_center[0] + math.cos(rad) * (sun_radius + 2)
            start_y = sun_center[1] + math.sin(rad) * (sun_radius + 2)
            end_x = sun_center[0] + math.cos(rad) * (sun_radius + 10)
            end_y = sun_center[1] + math.sin(rad) * (sun_radius + 10)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 220, 100, 255), width=2)
        
        # Horizon line
        horizon_y = int(size * 0.7)
        draw.rectangle([0, horizon_y, size, size], fill=(255, 150, 50, 180))
        
        # Convert to pygame surface
        mode = img.mode
        surf_size = img.size
        data = img.tobytes()
        py_surface = pygame.image.fromstring(data, surf_size, mode)
        
        self.icon_cache[('sunrise', size)] = py_surface
        return py_surface
    
    def create_sun_icon(self, size=40):
        """Create a sun icon (afternoon)"""
        if ('sun', size) in self.icon_cache:
            return self.icon_cache[('sun', size)]
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center = (size // 2, size // 2)
        sun_radius = int(size * 0.3)
        
        # Outer glow
        for i in range(8):
            glow_radius = sun_radius + i * 2
            alpha = int(120 - i * 12)
            draw.ellipse([center[0] - glow_radius, center[1] - glow_radius,
                         center[0] + glow_radius, center[1] + glow_radius],
                        fill=(255, 240, 100, alpha))
        
        # Sun core with gradient effect
        draw.ellipse([center[0] - sun_radius, center[1] - sun_radius,
                     center[0] + sun_radius, center[1] + sun_radius],
                    fill=(255, 220, 0, 255))
        
        # Inner highlight
        highlight_radius = int(sun_radius * 0.5)
        highlight_offset = int(sun_radius * 0.3)
        draw.ellipse([center[0] - highlight_radius - highlight_offset, 
                     center[1] - highlight_radius - highlight_offset,
                     center[0] + highlight_radius - highlight_offset, 
                     center[1] + highlight_radius - highlight_offset],
                    fill=(255, 255, 200, 180))
        
        # Sun rays (longer and more prominent)
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            start_x = center[0] + math.cos(rad) * (sun_radius + 2)
            start_y = center[1] + math.sin(rad) * (sun_radius + 2)
            end_x = center[0] + math.cos(rad) * (sun_radius + 12)
            end_y = center[1] + math.sin(rad) * (sun_radius + 12)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 220, 0, 255), width=3)
        
        mode = img.mode
        surf_size = img.size
        data = img.tobytes()
        py_surface = pygame.image.fromstring(data, surf_size, mode)
        
        self.icon_cache[('sun', size)] = py_surface
        return py_surface
    
    def create_sunset_icon(self, size=40):
        """Create a sunset icon (evening)"""
        if ('sunset', size) in self.icon_cache:
            return self.icon_cache[('sunset', size)]
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Sun lower on horizon
        sun_center = (size // 2, int(size * 0.75))
        sun_radius = int(size * 0.28)
        
        # Purple/orange glow
        for i in range(6):
            glow_radius = sun_radius + i * 4
            alpha = int(100 - i * 12)
            # Gradient from orange to purple
            r = int(255 - i * 30)
            g = int(150 - i * 20)
            b = int(100 + i * 20)
            draw.ellipse([sun_center[0] - glow_radius, sun_center[1] - glow_radius,
                         sun_center[0] + glow_radius, sun_center[1] + glow_radius],
                        fill=(r, g, b, alpha))
        
        # Sun core (orange)
        draw.ellipse([sun_center[0] - sun_radius, sun_center[1] - sun_radius,
                     sun_center[0] + sun_radius, sun_center[1] + sun_radius],
                    fill=(255, 130, 50, 255))
        
        # Sunset rays (fewer, softer)
        for angle in range(0, 180, 40):
            rad = math.radians(angle - 90)
            start_x = sun_center[0] + math.cos(rad) * (sun_radius + 2)
            start_y = sun_center[1] + math.sin(rad) * (sun_radius + 2)
            end_x = sun_center[0] + math.cos(rad) * (sun_radius + 8)
            end_y = sun_center[1] + math.sin(rad) * (sun_radius + 8)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 150, 80, 200), width=2)
        
        # Horizon with purple tint
        horizon_y = int(size * 0.75)
        draw.rectangle([0, horizon_y, size, size], fill=(180, 100, 180, 150))
        
        mode = img.mode
        surf_size = img.size
        data = img.tobytes()
        py_surface = pygame.image.fromstring(data, surf_size, mode)
        
        self.icon_cache[('sunset', size)] = py_surface
        return py_surface
    
    def create_moon_icon(self, size=40):
        """Create a moon icon (night)"""
        if ('moon', size) in self.icon_cache:
            return self.icon_cache[('moon', size)]
        
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center = (size // 2, size // 2)
        moon_radius = int(size * 0.35)
        
        # Moon glow
        for i in range(8):
            glow_radius = moon_radius + i * 2
            alpha = int(80 - i * 8)
            draw.ellipse([center[0] - glow_radius, center[1] - glow_radius,
                         center[0] + glow_radius, center[1] + glow_radius],
                        fill=(200, 220, 255, alpha))
        
        # Moon body (crescent shape)
        draw.ellipse([center[0] - moon_radius, center[1] - moon_radius,
                     center[0] + moon_radius, center[1] + moon_radius],
                    fill=(240, 245, 255, 255))
        
        # Create crescent by overlapping darker circle
        shadow_offset = int(moon_radius * 0.4)
        draw.ellipse([center[0] - moon_radius + shadow_offset, 
                     center[1] - moon_radius,
                     center[0] + moon_radius + shadow_offset, 
                     center[1] + moon_radius],
                    fill=(30, 40, 80, 255))
        
        # Stars around moon
        star_positions = [(10, 10), (size - 10, 12), (8, size - 12), (size - 8, size - 10)]
        for star_x, star_y in star_positions:
            # 4-pointed star
            points = []
            for i in range(8):
                angle = i * math.pi / 4
                radius = 3 if i % 2 == 0 else 1.5
                px = star_x + radius * math.cos(angle)
                py = star_y + radius * math.sin(angle)
                points.append((px, py))
            draw.polygon(points, fill=(255, 255, 255, 255))
        
        mode = img.mode
        surf_size = img.size
        data = img.tobytes()
        py_surface = pygame.image.fromstring(data, surf_size, mode)
        
        self.icon_cache[('moon', size)] = py_surface
        return py_surface


class EnhancedDayNightCycle:
    """Enhanced day/night cycle with smooth transitions and visual effects"""
    
    def __init__(self):
        self.current_phase = None
        self.icon_renderer = TimeIconRenderer()
        self.animation_timer = 0
        self.phase_transition_progress = 0
        self.sky_overlay = None
        self.update_phase()
    
    def update_phase(self):
        """Update current time phase based on real-world time"""
        current_hour = datetime.datetime.now().hour
        
        if 6 <= current_hour < 12:
            self.current_phase = "Morning"
        elif 12 <= current_hour < 18:
            self.current_phase = "Afternoon"
        elif 18 <= current_hour < 22:
            self.current_phase = "Evening"
        else:
            self.current_phase = "Night"
    
    def get_phase_icon(self, size=40):
        """Get the appropriate icon for current phase"""
        if self.current_phase == "Morning":
            return self.icon_renderer.create_sunrise_icon(size)
        elif self.current_phase == "Afternoon":
            return self.icon_renderer.create_sun_icon(size)
        elif self.current_phase == "Evening":
            return self.icon_renderer.create_sunset_icon(size)
        else:  # Night
            return self.icon_renderer.create_moon_icon(size)
    
    def create_sky_overlay(self, width, height, phase, alpha=80):
        """Create atmospheric sky overlay using PIL"""
        phase_colors = {
            "Morning": [(255, 240, 200), (255, 220, 150)],
            "Afternoon": [(255, 250, 220), (255, 240, 180)],
            "Evening": [(200, 120, 180), (150, 80, 150)],
            "Night": [(20, 30, 80), (10, 20, 60)]
        }
        
        colors = phase_colors.get(phase, [(255, 255, 255), (200, 200, 200)])
        
        # Create gradient
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        for y in range(height):
            t = y / height
            # Use pytweening for smooth color transition
            eased_t = pytweening.easeInOutQuad(t)
            
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * eased_t)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * eased_t)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * eased_t)
            
            for x in range(width):
                img.putpixel((x, y), (r, g, b, alpha))
        
        # Apply subtle blur for atmospheric effect
        img = img.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Convert to pygame surface
        mode = img.mode
        size = img.size
        data = img.tobytes()
        return pygame.image.fromstring(data, size, mode)
    
    def get_phase_info(self):
        """Get information about current time phase"""
        self.update_phase()
        
        phase_data = {
            "Morning": {
                "name": "Morning",
                "description": "Fresh start! Speed and Accuracy boosted",
                "color": YELLOW,
                "icon": "[SUNRISE]",  # Text placeholder for backward compatibility
                "bonuses": {
                    "speed": 1.15,
                    "accuracy": 1.10
                },
                "boosted_types": ["Light", "Star", "Human"]
            },
            "Afternoon": {
                "name": "Afternoon", 
                "description": "Peak performance! Attack and Special Attack boosted",
                "color": ORANGE,
                "icon": "[SUN]",  # Text placeholder for backward compatibility
                "bonuses": {
                    "attack": 1.20,
                    "special_attack": 1.20
                },
                "boosted_types": ["Light", "Grass", "Car"]
            },
            "Evening": {
                "name": "Evening",
                "description": "Winding down. Defense and Special Defense boosted",
                "color": PURPLE,
                "icon": "[SUNSET]",  # Text placeholder for backward compatibility
                "bonuses": {
                    "defense": 1.15,
                    "special_defense": 1.15
                },
                "boosted_types": ["Imagination", "Catgirl", "Miwiwi"]
            },
            "Night": {
                "name": "Night",
                "description": "Darkness reigns. Special moves and evasion boosted",
                "color": DARK_BLUE,
                "icon": "[MOON]",  # Text placeholder for backward compatibility
                "bonuses": {
                    "special_attack": 1.25,
                    "speed": 1.10,
                    "dodge_chance": 1.5
                },
                "boosted_types": ["Star", "Mod", "Bonk", "Crude Oil"]
            }
        }
        
        return phase_data.get(self.current_phase, phase_data["Afternoon"])
    
    def apply_time_bonus(self, character_stats):
        """Apply time-based bonuses to character stats"""
        phase_info = self.get_phase_info()
        bonuses = phase_info["bonuses"]
        
        modified_stats = character_stats.copy()
        
        for stat, multiplier in bonuses.items():
            if stat in modified_stats:
                modified_stats[stat] = int(modified_stats[stat] * multiplier)
        
        return modified_stats, phase_info
    
    def get_type_time_bonus(self, character_types):
        """Get additional damage bonus if character type matches time"""
        phase_info = self.get_phase_info()
        boosted_types = phase_info["boosted_types"]
        
        for char_type in character_types:
            if char_type in boosted_types:
                return 1.15
        
        return 1.0
    
    def update_animation(self, dt):
        """Update animation timers for smooth effects"""
        self.animation_timer += dt
    
    def draw_sky_overlay(self, screen, alpha=80):
        """Draw atmospheric overlay on screen"""
        width, height = screen.get_size()
        
        # Create or update overlay
        if self.sky_overlay is None or self.sky_overlay.get_size() != (width, height):
            self.sky_overlay = self.create_sky_overlay(width, height, self.current_phase, alpha)
        
        # Pulsing effect using pytweening
        time_normalized = (self.animation_timer % 3000) / 3000.0
        pulse = pytweening.easeInOutSine(time_normalized)
        current_alpha = int(alpha * (0.8 + 0.2 * pulse))
        
        self.sky_overlay.set_alpha(current_alpha)
        screen.blit(self.sky_overlay, (0, 0))
    
    def draw_time_panel_enhanced(self, screen, x, y, width, height, font, small_font):
        """Draw enhanced time panel with custom icon and effects"""
        phase_info = self.get_phase_info()
        
        # Create gradient background
        panel_surface = pygame.Surface((width, height))
        base_color = phase_info["color"]
        
        for i in range(height):
            t = i / height
            # Smooth gradient using pytweening
            eased_t = pytweening.easeInOutQuad(t)
            color = tuple(int(base_color[j] * (0.7 + 0.3 * eased_t)) for j in range(3))
            pygame.draw.line(panel_surface, color, (0, i), (width, i))
        
        screen.blit(panel_surface, (x, y))
        
        # Animated border pulse
        time_normalized = (self.animation_timer % 2000) / 2000.0
        pulse = pytweening.easeInOutSine(time_normalized)
        border_width = int(3 + pulse * 2)
        pygame.draw.rect(screen, BLACK, (x, y, width, height), border_width)
        
        # Draw custom icon with bounce animation
        icon = self.get_phase_icon(size=45)
        bounce = int(3 * math.sin(self.animation_timer * 0.003))
        icon_x = x + 10
        icon_y = y + (height - icon.get_height()) // 2 + bounce
        screen.blit(icon, (icon_x, icon_y))
        
        # Time phase text with shadow
        text_x = icon_x + icon.get_width() + 15
        text_y = y + 8
        
        # Shadow
        shadow_text = font.render(f"Time: {phase_info['name']}", True, BLACK)
        screen.blit(shadow_text, (text_x + 2, text_y + 2))
        
        # Main text
        time_text = font.render(f"Time: {phase_info['name']}", True, BLACK)
        screen.blit(time_text, (text_x, text_y))
        
        # Description with shadow
        desc_y = text_y + 25
        desc_shadow = small_font.render(phase_info['description'], True, BLACK)
        screen.blit(desc_shadow, (text_x + 1, desc_y + 1))
        
        desc_text = small_font.render(phase_info['description'], True, BLACK)
        screen.blit(desc_text, (text_x, desc_y))


# Global enhanced day/night cycle instance
day_night_cycle = EnhancedDayNightCycle()

print("Enhanced Day/Night Cycle System Loaded!")
print(f"Current phase: {day_night_cycle.current_phase}")