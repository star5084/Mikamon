import os, sys, pygame

# Global variables
title_music = None
fight_music = None
title_music_loaded = False
fight_music_loaded = False
current_music_type = None
test_volume_cooldown = 0

# Import game settings - DON'T create fallback that overrides user settings
try:
    from python.settings import game_settings
    print(f"Successfully imported game_settings: {game_settings}")
except ImportError:
    print("WARNING: Could not import game_settings from python.settings")
    # Create minimal fallback, but this should not happen in normal operation
    game_settings = {
        "music_volume": 0.1,
        "fight_music_volume": 0.1
    }

def find_music_directories():
    possible_dirs = []

    cwd = os.getcwd()
    possible_dirs.append(cwd)
    possible_dirs.append(os.path.join(cwd, "music"))

    music_py_dir = os.path.dirname(os.path.abspath(__file__))
    possible_dirs.append(music_py_dir)
    possible_dirs.append(os.path.join(music_py_dir, "music"))

    parent_dir = os.path.dirname(music_py_dir)
    possible_dirs.append(parent_dir)
    possible_dirs.append(os.path.join(parent_dir, "music"))

    if os.path.basename(music_py_dir).lower() == "python":
        grandparent_dir = os.path.dirname(parent_dir)
        possible_dirs.append(grandparent_dir)
        possible_dirs.append(os.path.join(grandparent_dir, "music"))
        music_sibling_path = os.path.join(parent_dir, "music")
        possible_dirs.insert(0, music_sibling_path)

    if hasattr(sys, 'argv') and sys.argv:
        main_file = sys.argv[0]
        if main_file:
            main_dir = os.path.dirname(os.path.abspath(main_file))
            possible_dirs.append(main_dir)
            possible_dirs.append(os.path.join(main_dir, "music"))

    if '__main__' in sys.modules:
        main_module = sys.modules['__main__']
        if hasattr(main_module, '__file__') and main_module.__file__:
            main_script_dir = os.path.dirname(os.path.abspath(main_module.__file__))
            possible_dirs.append(main_script_dir)
            possible_dirs.append(os.path.join(main_script_dir, "music"))

    seen = set()
    unique_dirs = []
    for d in possible_dirs:
        if d not in seen:
            seen.add(d)
            unique_dirs.append(d)

    return unique_dirs

def find_music_files():
    directories = find_music_directories()

    title_names = [
        "Title_Screen_music.wav",
        "Title_Screen_music.ogg",
        "Title_Screen_music.mp3",
        "title_music.ogg", "title_music.wav", "title_music.mp3",
        "title.ogg", "title.wav", "title.mp3"
    ]

    fight_names = [
        "fight_music.wav",
        "fight_music.ogg",
        "fight_music.mp3",
        "battle_music.wav", "battle_music.ogg", "battle_music.mp3",
        "battle.wav", "battle.ogg", "battle.mp3",
        "fight.wav", "fight.ogg", "fight.mp3"
    ]

    title_files = []
    fight_files = []

    print("=== SEARCHING FOR MUSIC FILES ===")
    print(f"music.py is located at: {os.path.abspath(__file__)}")
    print(f"Looking for your specific files: Title_Screen_music.wav and fight_music.wav")

    for i, directory in enumerate(directories):
        print(f"{i+1}. Checking directory: {directory}")
        if os.path.exists(directory):
            try:
                files_in_dir = os.listdir(directory)
                audio_files = [f for f in files_in_dir if f.lower().endswith(('.wav', '.ogg', '.mp3'))]
                if audio_files:
                    print(f"   Found audio files: {audio_files}")
                else:
                    print(f"   No audio files found")

                for name in title_names:
                    full_path = os.path.join(directory, name)
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                        title_files.append(full_path)
                        print(f"    Found title music: {full_path}")

                for name in fight_names:
                    full_path = os.path.join(directory, name)
                    if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                        fight_files.append(full_path)
                        print(f"    Found fight music: {full_path}")

            except Exception as e:
                print(f"   Error reading directory: {e}")
        else:
            print(f"   Directory does not exist")

    print(f"\n=== SEARCH RESULTS ===")
    print(f"Title music files found: {len(title_files)}")
    for f in title_files:
        print(f"  - {f}")
    print(f"Fight music files found: {len(fight_files)}")
    for f in fight_files:
        print(f"  - {f}")
    print("=== END SEARCH ===\n")

    return title_files, fight_files

title_audio_files = []
fight_audio_files = []

def initialize_music_system():
    global title_audio_files, fight_audio_files
    print("Initializing music system...")

    if not pygame.mixer.get_init():
        print("WARNING: pygame.mixer not initialized! Music will not work.")
        return False

    title_audio_files, fight_audio_files = find_music_files()
    return True

def load_title_music():
    global title_music, title_music_loaded
    print("Loading title music...")

    if not title_audio_files and not fight_audio_files:
        initialize_music_system()

    if not title_audio_files:
        print("No title music files found!")
        return False

    for audio_file in title_audio_files:
        try:
            title_music = pygame.mixer.Sound(audio_file)
            # Use current volume from game_settings when loading
            current_volume = game_settings.get("music_volume", 0.7)
            title_music.set_volume(current_volume)
            title_music_loaded = True
            print(f"Loaded title music from {audio_file} with volume {current_volume}")
            return True
        except Exception as e:
            print(f"Error loading title music {audio_file}: {e}")

    title_music_loaded = False
    return False

def load_fight_music():
    global fight_music, fight_music_loaded
    print("Loading fight music...")

    if not title_audio_files and not fight_audio_files:
        initialize_music_system()

    if not fight_audio_files:
        print("No fight music files found!")
        return False

    for audio_file in fight_audio_files:
        try:
            fight_music = pygame.mixer.Sound(audio_file)
            # Use current volume from game_settings when loading
            current_volume = game_settings.get("fight_music_volume", 0.8)
            fight_music.set_volume(current_volume)
            fight_music_loaded = True
            print(f"Loaded fight music from {audio_file} with volume {current_volume}")
            return True
        except Exception as e:
            print(f"Error loading fight music {audio_file}: {e}")

    fight_music_loaded = False
    return False

def stop_all_music():
    global current_music_type
    try:
        if title_music:
            title_music.stop()
        if fight_music:
            fight_music.stop()
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        print("All music stopped")
    except Exception as e:
        print(f"Error stopping music: {e}")

    current_music_type = None

def play_title_music():
    global current_music_type
    print("Attempting to play title music...")

    try:
        if fight_music:
            fight_music.stop()
        pygame.mixer.stop()
    except Exception as e:
        print(f"Error stopping previous music: {e}")

    if not title_music_loaded:
        if not load_title_music():
            return False

    if title_music_loaded and title_music:
        try:
            # Always set volume to current setting before playing
            current_volume = game_settings.get("music_volume", 0.7)
            title_music.set_volume(current_volume)
            print(f"Setting title music volume to: {current_volume}")
            title_music.play(-1)
            current_music_type = "title"
            print("Title music is now playing")
            return True
        except Exception as e:
            print(f"Error playing title music: {e}")
            return False
    return False

def play_fight_music():
    global current_music_type
    print("Attempting to play fight music...")

    try:
        if title_music:
            title_music.stop()
        pygame.mixer.stop()
    except Exception as e:
        print(f"Error stopping previous music: {e}")

    if not fight_music_loaded:
        if not load_fight_music():
            return False

    if fight_music_loaded and fight_music:
        try:
            # Always set volume to current setting before playing
            current_volume = game_settings.get("fight_music_volume", 0.8)
            fight_music.set_volume(current_volume)
            print(f"Setting fight music volume to: {current_volume}")
            channel = fight_music.play(-1)
            if channel is not None:
                current_music_type = "fight"
                print("Fight music is now playing")
                return True
            else:
                print("Could not start fight music")
                return False
        except Exception as e:
            print(f"Error playing fight music: {e}")
            return False
    return False

def update_music_volumes():
    """Update music volumes based on settings"""
    try:
        title_volume = game_settings.get("music_volume", 0.7)
        fight_volume = game_settings.get("fight_music_volume", 0.8)
        
        print(f"Updating volumes: title={title_volume}, fight={fight_volume}")
        
        if title_music and title_music_loaded:
            title_music.set_volume(title_volume)
            if current_music_type == "title":
                print(f"Updated playing title music volume to: {title_volume}")

        if fight_music and fight_music_loaded:
            fight_music.set_volume(fight_volume)
            if current_music_type == "fight":
                print(f"Updated playing fight music volume to: {fight_volume}")

        # Update pygame.mixer.music volume as well
        pygame.mixer.music.set_volume(title_volume)

        # Also update active channels so changes apply immediately
        for i in range(pygame.mixer.get_num_channels()):
            ch = pygame.mixer.Channel(i)
            if ch.get_busy():
                if current_music_type == "fight":
                    ch.set_volume(fight_volume)
                elif current_music_type == "title":
                    ch.set_volume(title_volume)

    except Exception as e:
        print(f"Error updating volumes: {e}")

def test_fight_volume():
    global test_volume_cooldown
    current_time = pygame.time.get_ticks()
    if current_time < test_volume_cooldown:
        print("Test volume still in cooldown")
        return

    print("Testing fight music volume...")

    if not fight_music_loaded and not load_fight_music():
        print("Cannot test - fight music failed to load")
        return

    if fight_music_loaded and fight_music:
        try:
            pygame.mixer.stop()
            # Use current volume setting for test
            current_volume = game_settings.get("fight_music_volume", 0.8)
            fight_music.set_volume(current_volume)
            print(f"Testing fight music at volume: {current_volume}")
            channel = fight_music.play()
            if channel is not None:
                print("Fight music test started")
                test_volume_cooldown = current_time + 3000
                pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
        except Exception as e:
            print(f"Could not test fight music volume: {e}")

def get_music_status():
    mixer_init = pygame.mixer.get_init()
    return {
        "title_loaded": title_music_loaded,
        "fight_loaded": fight_music_loaded,
        "current_type": current_music_type,
        "mixer_initialized": mixer_init is not None,
        "mixer_settings": mixer_init if mixer_init else "Not initialized",
        "num_channels": pygame.mixer.get_num_channels() if mixer_init else 0
    }

def debug_fight_music():
    print("=== FIGHT MUSIC DEBUG INFO ===")
    status = get_music_status()
    print(f"Fight music loaded: {status['fight_loaded']}")
    print(f"Fight music object exists: {fight_music is not None}")
    print(f"Current music type: {status['current_type']}")
    print(f"Mixer initialized: {status['mixer_initialized']}")
    print(f"Mixer settings: {status['mixer_settings']}")
    print(f"Number of channels: {status['num_channels']}")
    if fight_music:
        try:
            print(f"Fight music volume: {fight_music.get_volume()}")
            print(f"Settings fight volume: {game_settings.get('fight_music_volume', 'NOT SET')}")
        except:
            print("Could not get fight music volume")
    print("Fight audio files found:")
    for f in fight_audio_files:
        print(f"  - {f}")
    print("=== END DEBUG INFO ===")