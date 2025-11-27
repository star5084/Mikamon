import random
import pygame
import math
import numpy as np
from numba import jit, prange
import pymunk
import pymunk.pygame_util
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import pytweening
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    
from python.color import GRAY, BLUE, PURPLE, LIGHT_GRAY, YELLOW, CYAN, ORANGE, WHITE, GREEN

# ============= NUMBA-ACCELERATED PARTICLE PHYSICS =============
@jit(nopython=True, parallel=True)
def update_particles_batch(positions, velocities, lifetimes, dt, wind_x, wind_y, gravity):
    """Ultra-fast batch particle update with Numba JIT compilation"""
    dt_factor = dt / 16.67
    alive_count = 0
    
    for i in prange(len(positions)):
        if lifetimes[i] > 0:
            # Apply physics
            velocities[i, 1] += gravity * dt_factor
            positions[i, 0] += (velocities[i, 0] + wind_x) * dt_factor
            positions[i, 1] += (velocities[i, 1] + wind_y) * dt_factor
            lifetimes[i] -= dt
            
            # Wrap around screen edges
            if positions[i, 0] < -100:
                positions[i, 0] = 2020
            elif positions[i, 0] > 2020:
                positions[i, 0] = -100
            
            if lifetimes[i] > 0:
                alive_count += 1
    
    return alive_count

@jit(nopython=True)
def calculate_lightning_segment(start_x, start_y, target_y, num_segments):
    """Generate lightning path with Numba optimization"""
    segments = np.zeros((num_segments, 4), dtype=np.float32)
    
    current_x = start_x
    current_y = start_y
    segment_height = (target_y - start_y) / num_segments
    
    for i in range(num_segments):
        next_x = current_x + np.random.uniform(-40, 40)
        next_y = current_y + segment_height + np.random.uniform(-20, 20)
        
        segments[i, 0] = current_x
        segments[i, 1] = current_y
        segments[i, 2] = next_x
        segments[i, 3] = next_y
        
        current_x = next_x
        current_y = next_y
    
    return segments


# ============= ADVANCED PARTICLE SYSTEM =============
class PhysicsParticle:
    """Particle with Pymunk physics integration"""
    def __init__(self, space, x, y, color, mass=1, radius=5, particle_type="default"):
        self.body = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius))
        self.body.position = x, y
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.5
        space.add(self.body, self.shape)
        
        self.color = color
        self.life = 2000
        self.max_life = 2000
        self.particle_type = particle_type
        self.radius = radius
        self.glow = particle_type in ["lightning", "fire", "magic"]
        
    def update(self, dt):
        self.life -= dt
        return self.life > 0
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        pos = (int(self.body.position.x), int(self.body.position.y))
        
        if self.glow:
            # Draw glow effect
            for i in range(3):
                glow_radius = self.radius + (3 - i) * 8
                glow_alpha = alpha // (i + 2)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*self.color, glow_alpha), 
                                 (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (pos[0] - glow_radius, pos[1] - glow_radius))
        
        # Draw particle core
        particle_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*self.color, alpha), 
                         (self.radius, self.radius), self.radius)
        screen.blit(particle_surf, (pos[0] - self.radius, pos[1] - self.radius))


class BatchParticleSystem:
    """High-performance batch particle system using NumPy and Numba"""
    def __init__(self, max_particles=10000):
        self.max_particles = max_particles
        self.positions = np.zeros((max_particles, 2), dtype=np.float32)
        self.velocities = np.zeros((max_particles, 2), dtype=np.float32)
        self.lifetimes = np.zeros(max_particles, dtype=np.float32)
        self.colors = np.zeros((max_particles, 3), dtype=np.uint8)
        self.sizes = np.zeros(max_particles, dtype=np.float32)
        self.max_lifetimes = np.zeros(max_particles, dtype=np.float32)
        self.active_count = 0
    
    def add_particle(self, x, y, vx, vy, color, size, lifetime):
        """Add a particle to the batch system"""
        if self.active_count < self.max_particles:
            idx = self.active_count
            self.positions[idx] = [x, y]
            self.velocities[idx] = [vx, vy]
            self.colors[idx] = color
            self.sizes[idx] = size
            self.lifetimes[idx] = lifetime
            self.max_lifetimes[idx] = lifetime
            self.active_count += 1
    
    def update(self, dt, wind_x=0, wind_y=0, gravity=0.5):
        """Update all particles using Numba-accelerated batch processing"""
        if self.active_count > 0:
            alive = update_particles_batch(
                self.positions[:self.active_count],
                self.velocities[:self.active_count],
                self.lifetimes[:self.active_count],
                dt, wind_x, wind_y, gravity
            )
            
            # Compact dead particles
            if alive < self.active_count:
                alive_mask = self.lifetimes[:self.active_count] > 0
                self.positions[:alive] = self.positions[:self.active_count][alive_mask]
                self.velocities[:alive] = self.velocities[:self.active_count][alive_mask]
                self.lifetimes[:alive] = self.lifetimes[:self.active_count][alive_mask]
                self.colors[:alive] = self.colors[:self.active_count][alive_mask]
                self.sizes[:alive] = self.sizes[:self.active_count][alive_mask]
                self.max_lifetimes[:alive] = self.max_lifetimes[:self.active_count][alive_mask]
                self.active_count = alive
    
    def draw(self, screen):
        """Draw all particles efficiently"""
        for i in range(self.active_count):
            alpha = int(255 * (self.lifetimes[i] / self.max_lifetimes[i]))
            size = max(1, int(self.sizes[i] * (self.lifetimes[i] / self.max_lifetimes[i])))
            pos = (int(self.positions[i, 0]), int(self.positions[i, 1]))
            
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = (*self.colors[i], alpha)
            pygame.draw.circle(particle_surf, color, (size, size), size)
            screen.blit(particle_surf, (pos[0] - size, pos[1] - size))


# ============= PIL-ENHANCED EFFECTS =============
class PILWeatherEffects:
    """Advanced weather effects using PIL for image processing"""
    def __init__(self):
        self.blur_cache = {}
        self.glow_cache = {}
    
    def create_glow_surface(self, size, color, intensity=1.0):
        """Create a glowing effect using PIL"""
        cache_key = (size, color, intensity)
        if cache_key in self.glow_cache:
            return self.glow_cache[cache_key]
        
        # Create PIL image
        img = Image.new('RGBA', (size * 2, size * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient circles
        for i in range(10):
            radius = size * (1 - i * 0.1)
            alpha = int(255 * intensity * (1 - i * 0.1))
            draw.ellipse([size - radius, size - radius, size + radius, size + radius],
                        fill=(*color, alpha))
        
        # Apply Gaussian blur
        img = img.filter(ImageFilter.GaussianBlur(radius=size // 4))
        
        # Convert to pygame surface
        mode = img.mode
        size = img.size
        data = img.tobytes()
        py_surface = pygame.image.fromstring(data, size, mode)
        
        self.glow_cache[cache_key] = py_surface
        return py_surface
    
    def create_fog_layer(self, width, height, density=0.5, color=(200, 200, 220)):
        """Create realistic fog using PIL"""
        # Create base fog
        img = Image.new('RGBA', (width, height), (*color, 0))
        
        # Add Perlin-like noise using multiple scales
        for scale in [50, 100, 200]:
            noise = Image.new('L', (width // scale, height // scale))
            pixels = np.random.randint(0, 256, (height // scale, width // scale), dtype=np.uint8)
            noise.putdata(pixels.flatten().tolist())
            noise = noise.resize((width, height), Image.BILINEAR)
            noise = noise.filter(ImageFilter.GaussianBlur(radius=20))
            
            # Blend with fog
            fog_alpha = ImageEnhance.Brightness(noise).enhance(density)
            img.paste(color, (0, 0), fog_alpha)
        
        # Convert to pygame
        mode = img.mode
        size = img.size
        data = img.tobytes()
        return pygame.image.fromstring(data, size, mode)


# ============= OPENCV LIGHTNING EFFECTS =============
class CVLightningGenerator:
    """Advanced lightning using OpenCV for realistic electrical arcs"""
    def __init__(self):
        self.cv2_available = CV2_AVAILABLE
    
    def generate_lightning_texture(self, width, height, branches=3):
        """Generate lightning texture using OpenCV"""
        if not self.cv2_available:
            return None
        
        # Create black image
        img = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Main bolt path
        start_x = width // 2
        segments = calculate_lightning_segment(start_x, 0, height, 30)
        
        # Draw main bolt with glow
        for segment in segments:
            x1, y1, x2, y2 = segment
            # Outer glow
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), 
                    (200, 220, 255, 60), thickness=20)
            # Middle glow
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), 
                    (220, 230, 255, 120), thickness=10)
            # Core
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), 
                    (255, 255, 255, 255), thickness=3)
        
        # Add branches
        for _ in range(branches):
            branch_start = int(np.random.uniform(5, 25))
            if branch_start < len(segments):
                start_seg = segments[branch_start]
                branch_x = start_seg[2]
                branch_y = start_seg[3]
                
                for i in range(5):
                    end_x = branch_x + np.random.uniform(-100, 100)
                    end_y = branch_y + i * 30 + np.random.uniform(-20, 20)
                    cv2.line(img, (int(branch_x), int(branch_y)), 
                            (int(end_x), int(end_y)), 
                            (200, 220, 255, 180), thickness=4)
                    cv2.line(img, (int(branch_x), int(branch_y)), 
                            (int(end_x), int(end_y)), 
                            (255, 255, 255, 255), thickness=2)
                    branch_x, branch_y = end_x, end_y
        
        # Apply Gaussian blur for glow
        img = cv2.GaussianBlur(img, (15, 15), 0)
        
        # Convert to pygame surface
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        return pygame.image.frombuffer(img_rgb.tobytes(), (width, height), 'RGBA')


# ============= ENHANCED WEATHER EFFECTS CLASS =============
class EnhancedWeatherEffects:
    """Next-gen weather effects with all advanced libraries"""
    def __init__(self):
        self.batch_particles = BatchParticleSystem(max_particles=15000)
        self.physics_space = pymunk.Space()
        self.physics_space.gravity = (0, 200)
        self.physics_particles = []
        
        self.pil_effects = PILWeatherEffects()
        self.cv_lightning = CVLightningGenerator()
        
        self.current_weather = None
        self.fog_alpha = 0
        self.fog_target = 0
        self.fog_surface = None
        self.spawn_timer = 0
        self.lightning_timer = 0
        self.lightning_surfaces = []
        
        # Rain system
        self.raindrops = []
        self.rain_intensity = 0
        
        # Animation timers
        self.animation_time = 0
    
    @property
    def particles(self):
        """
        Compatibility property that returns all active particles.
        This allows battle_system.py to access len(weather_effects.particles)
        """
        total_count = (self.batch_particles.active_count + 
                      len(self.physics_particles) + 
                      len(self.raindrops) + 
                      len(self.lightning_surfaces))
        return [None] * total_count
    
    def get_particle_count(self):
        """Get total number of active particles across all systems"""
        return (self.batch_particles.active_count + 
                len(self.physics_particles) + 
                len(self.raindrops) + 
                len(self.lightning_surfaces))
        
    def set_weather(self, weather_type):
        """Set weather with smooth transitions using pytweening"""
        self.current_weather = weather_type
        
        fog_levels = {
            "Clear": 0, "Sunny": 0, "Rainy": 80,
            "Windy": 40, "Stormy": 150, "Misty": 200
        }
        self.fog_target = fog_levels.get(weather_type, 0)
        
        if weather_type in ["Rainy", "Stormy"]:
            self.rain_intensity = 1.0 if weather_type == "Rainy" else 2.0
        else:
            self.rain_intensity = 0
        
        # Pre-generate fog layer with PIL
        if self.fog_target > 0:
            density = self.fog_target / 255.0
            self.fog_surface = self.pil_effects.create_fog_layer(1920, 1080, density)
    
    def spawn_advanced_rain(self, count):
        """Spawn rain with physics simulation"""
        for _ in range(count):
            x = random.uniform(-200, 2120)
            y = random.uniform(-400, 0)
            
            # Add to physics simulation
            particle = PhysicsParticle(
                self.physics_space, x, y,
                (150, 180, 220), mass=0.1, radius=2,
                particle_type="rain"
            )
            particle.body.velocity = (random.uniform(-50, 50), random.uniform(400, 600))
            self.physics_particles.append(particle)
    
    def create_advanced_lightning(self):
        """Create lightning using OpenCV"""
        if self.cv_lightning.cv2_available:
            lightning_surf = self.cv_lightning.generate_lightning_texture(400, 1080, branches=5)
            if lightning_surf:
                x_pos = random.randint(200, 1520)
                self.lightning_surfaces.append({
                    'surface': lightning_surf,
                    'x': x_pos,
                    'life': 300,
                    'max_life': 300
                })
        
        # Add explosion particles at strike point
        strike_x = random.randint(300, 1620)
        strike_y = random.randint(800, 1000)
        
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 400)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 200
            
            self.batch_particles.add_particle(
                strike_x, strike_y, vx, vy,
                (255, 255, 255), random.uniform(4, 10), 800
            )
    
    def spawn_sunny_particles(self):
        """Spawn sun rays and sparkles"""
        for _ in range(10):
            x = random.randint(0, 1920)
            y = random.randint(0, 600)
            self.batch_particles.add_particle(
                x, y,
                random.uniform(-20, 20),
                random.uniform(-20, 20),
                (255, 240, 100),
                random.uniform(6, 12),
                4000
            )
    
    def spawn_wind_leaves(self):
        """Spawn wind-blown leaves with physics"""
        edge = random.choice(['left', 'right'])
        if edge == 'left':
            x, y = -50, random.randint(200, 800)
            vx = random.uniform(400, 600)
        else:
            x, y = 1970, random.randint(200, 800)
            vx = random.uniform(-600, -400)
        
        particle = PhysicsParticle(
            self.physics_space, x, y,
            random.choice([(255, 200, 0), (255, 150, 0), (200, 100, 0)]),
            mass=0.5, radius=8, particle_type="leaf"
        )
        particle.body.velocity = (vx, random.uniform(-100, 100))
        particle.body.angular_velocity = random.uniform(-10, 10)
        self.physics_particles.append(particle)
    
    def update(self, dt):
        """Update all weather effects"""
        self.animation_time += dt
        self.spawn_timer += dt
        
        # Smooth fog transition with pytweening
        if abs(self.fog_alpha - self.fog_target) > 1:
            progress = min(1.0, dt / 1000.0)
            eased_progress = pytweening.easeInOutQuad(progress)
            self.fog_alpha += (self.fog_target - self.fog_alpha) * eased_progress * 0.1
        
        # Calculate wind using pytweening for smooth oscillation
        time_normalized = (self.animation_time % 5000) / 5000.0
        wind_strength = pytweening.easeInOutSine(time_normalized) * 2 - 1
        
        wind_x = wind_y = 0
        if self.current_weather == "Windy":
            wind_x = wind_strength * 150
            wind_y = wind_strength * 50
        elif self.current_weather == "Stormy":
            wind_x = wind_strength * 250
            wind_y = wind_strength * 100
        
        # Update batch particle system
        gravity = 0.5 if self.current_weather != "Sunny" else 0.05
        self.batch_particles.update(dt, wind_x, wind_y, gravity)
        
        # Update physics particles
        self.physics_space.step(dt / 1000.0)
        self.physics_particles = [p for p in self.physics_particles if p.update(dt)]
        
        # Remove off-screen physics particles
        self.physics_particles = [
            p for p in self.physics_particles
            if -100 < p.body.position.x < 2020 and -100 < p.body.position.y < 1200
        ]
        
        # Weather-specific spawning
        if self.current_weather == "Rainy" and self.spawn_timer > 30:
            self.spawn_advanced_rain(50)
            self.spawn_timer = 0
        elif self.current_weather == "Stormy":
            if self.spawn_timer > 20:
                self.spawn_advanced_rain(80)
                self.spawn_timer = 0
            
            self.lightning_timer += dt
            if self.lightning_timer > random.randint(1000, 2500):
                self.create_advanced_lightning()
                self.lightning_timer = 0
        elif self.current_weather == "Sunny" and self.spawn_timer > 80:
            self.spawn_sunny_particles()
            self.spawn_timer = 0
        elif self.current_weather == "Windy" and self.spawn_timer > 150:
            self.spawn_wind_leaves()
            self.spawn_timer = 0
        elif self.current_weather == "Clear" and self.spawn_timer > 200:
            for _ in range(5):
                self.batch_particles.add_particle(
                    random.randint(0, 1920),
                    random.randint(0, 1080),
                    random.uniform(-1, 1),
                    random.uniform(-1, 1),
                    (240, 240, 255),
                    random.uniform(2, 4),
                    3000
                )
            self.spawn_timer = 0
        elif self.current_weather == "Misty" and self.spawn_timer > 100:
            for _ in range(10):
                self.batch_particles.add_particle(
                    random.randint(-100, 2020),
                    random.randint(300, 1080),
                    random.uniform(-10, 10),
                    random.uniform(-5, 5),
                    (220, 230, 240),
                    random.uniform(30, 60),
                    8000
                )
            self.spawn_timer = 0
        
        # Update lightning surfaces
        for lightning in self.lightning_surfaces:
            lightning['life'] -= dt
        self.lightning_surfaces = [l for l in self.lightning_surfaces if l['life'] > 0]
    
    def draw(self, screen):
        """Draw all advanced weather effects"""
        # Draw batch particles
        self.batch_particles.draw(screen)
        
        # Draw physics particles
        for particle in self.physics_particles:
            particle.draw(screen)
        
        # Draw lightning
        for lightning in self.lightning_surfaces:
            alpha = int(255 * (lightning['life'] / lightning['max_life']))
            lightning['surface'].set_alpha(alpha)
            screen.blit(lightning['surface'], (lightning['x'], 0))
            
            # Flash effect
            if lightning['life'] > lightning['max_life'] * 0.8:
                flash_alpha = int(150 * (lightning['life'] / lightning['max_life']))
                flash_surf = pygame.Surface((1920, 1080), pygame.SRCALPHA)
                flash_surf.fill((240, 245, 255, flash_alpha))
                screen.blit(flash_surf, (0, 0))
        
        # Draw fog layer
        if self.fog_alpha > 0 and self.fog_surface:
            self.fog_surface.set_alpha(int(self.fog_alpha))
            screen.blit(self.fog_surface, (0, 0))


# ============= WEATHER CLASS (UNCHANGED INTERFACE) =============
class Weather:
    """Weather system class - maintains same interface"""
    def __init__(self):
        self.current_weather = None
        self.duration = 0
        self.weather_types = {
            "Clear": {
                "boost_types": ["Human"], 
                "boost_percentage": 15,
                "message": "The weather is clear and calm.",
                "color": LIGHT_GRAY
            },
            "Sunny": {
                "boost_types": ["Light", "Star"], 
                "boost_percentage": 30,
                "message": "Brilliant sunshine floods the battlefield!",
                "color": YELLOW
            },
            "Rainy": {
                "boost_types": ["Oil", "Crude Oil", "Grass"], 
                "boost_percentage": 35,
                "message": "Torrential rain pounds the battlefield!",
                "color": BLUE
            },
            "Windy": {
                "boost_types": ["Imagination", "Catgirl"], 
                "boost_percentage": 20,
                "message": "Fierce winds howl across the battlefield!",
                "color": CYAN
            },
            "Stormy": {
                "boost_types": ["Bonk", "Mod"], 
                "boost_percentage": 40,
                "message": "A violent storm rages with thunder and lightning!",
                "color": PURPLE
            },
            "Misty": {
                "boost_types": ["Miwiwi", "Miwawa"], 
                "boost_percentage": 28,
                "message": "Dense mist shrouds the battlefield!",
                "color": GRAY
            }
        }
        self.change_weather()
    
    def change_weather(self):
        """Change weather with time-of-day restrictions"""
        import datetime
        
        old_weather = self.current_weather
        
        # Get current hour to determine if it's night
        current_hour = datetime.datetime.now().hour
        is_night = current_hour >= 22 or current_hour < 6
        
        # Create list of available weather types
        available_weather = list(self.weather_types.keys())
        
        # Remove Sunny from options during night time (10 PM - 6 AM)
        if is_night and "Sunny" in available_weather:
            available_weather.remove("Sunny")
            print("Night time detected - Sunny weather excluded")
        
        # Choose random weather from available options
        self.current_weather = random.choice(available_weather)
        self.duration = random.randint(3, 6)
        
        return old_weather != self.current_weather
    
    def get_boost_multiplier(self, move_type):
        if move_type in self.weather_types[self.current_weather]["boost_types"]:
            boost_percentage = self.weather_types[self.current_weather]["boost_percentage"]
            return 1.0 + (boost_percentage / 100.0)
        return 1.0
    
    def get_weather_info(self):
        weather_data = self.weather_types[self.current_weather]
        boosted_types = ", ".join(weather_data["boost_types"])
        boost_percent = weather_data["boost_percentage"]
        return {
            "name": self.current_weather,
            "duration": self.duration,
            "boosted_types": boosted_types,
            "boost_percent": boost_percent,
            "message": weather_data["message"],
            "color": weather_data["color"]
        }
    
    def update_turn(self):
        if self.duration > 0:
            self.duration -= 1
            if self.duration <= 0:
                return self.change_weather()
        return False


# ============= LIGHTWEIGHT PARTICLE FOR BACKWARD COMPATIBILITY =============
class Particle:
    """Lightweight particle for general use (backward compatible)"""
    def __init__(self, x, y, color, velocity_x, velocity_y, life=1000, particle_type="default"):
        self.pos = np.array([x, y], dtype=np.float32)
        self.vel = np.array([velocity_x, velocity_y], dtype=np.float32)
        self.color = color
        self.life = life
        self.max_life = life
        self.particle_type = particle_type
        self.size = 3.0
        self.rotation = 0.0
        self.rotation_speed = random.uniform(-5, 5)
        
        self.x = x
        self.y = y
        self.vx = velocity_x
        self.vy = velocity_y
        
    def update(self, dt, wind=None, gravity=0.5):
        """Update particle position"""
        dt_factor = dt / 16.67
        
        if wind is None:
            wind = np.array([0, 0], dtype=np.float32)
        elif not isinstance(wind, np.ndarray):
            wind = np.array([0, 0], dtype=np.float32)
        
        self.vel[1] += gravity * dt_factor
        self.pos += (self.vel + wind) * dt_factor
        self.rotation += self.rotation_speed * dt_factor
        
        self.x, self.y = self.pos[0], self.pos[1]
        self.vx, self.vy = self.vel[0], self.vel[1]
        
        self.life -= dt
        return self.life > 0
    
    def draw(self, screen):
        """Draw the particle"""
        alpha = int(255 * (self.life / self.max_life))
        size = max(1, int(self.size * (self.life / self.max_life)))
        
        particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*self.color, alpha), (size, size), size)
        screen.blit(particle_surf, (int(self.x - size), int(self.y - size)))
    
    def get_alpha(self):
        return int(255 * (self.life / self.max_life))
    
    def get_size(self):
        return max(1, int(self.size * (self.life / self.max_life)))


WeatherEffects = EnhancedWeatherEffects

print("=" * 60)
print("Enhanced Weather System Loaded Successfully!")
print("- Numba JIT: Available" if 'jit' in dir() else "- Numba JIT: NOT AVAILABLE")
print("- Pymunk: Available" if 'pymunk' in dir() else "- Pymunk: NOT AVAILABLE")
print("- PIL: Available" if 'Image' in dir() else "- PIL: NOT AVAILABLE")
print("- OpenCV: Available" if CV2_AVAILABLE else "- OpenCV: NOT AVAILABLE")
print("- Pytweening: Available" if 'pytweening' in dir() else "- Pytweening: NOT AVAILABLE")
print("=" * 60)