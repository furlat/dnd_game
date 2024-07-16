import pygame
import pygame_gui
from pygame_gui.elements import UIButton
import os 

class MusicManager:
    def __init__(self, manager, width, height):
        self.manager = manager
        self.music_playing = True
        self.music_files = [
            'background_music.mp3',
            'gear_up.mp3',
            'fast.mp3'
            # Add more music files here as needed
        ]
        self.current_track_index = 0
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load the first music file
        self.load_music(self.music_files[self.current_track_index])
        pygame.mixer.music.play(-1)  # Play the music in a loop

        # Create the play/pause button
        button_rect = pygame.Rect(int(width) - 210, int(height) - 60, 200, 50)
        self.play_pause_button = pygame_gui.elements.UIButton(
            relative_rect=button_rect,
            text='Pause',
            manager=self.manager
        )
        
        # Add a skip button (optional for future extension)
        skip_button_rect = pygame.Rect(int(width) - 210, int(height) - 120, 200, 50)
        self.skip_button = pygame_gui.elements.UIButton(
            relative_rect=skip_button_rect,
            text='Skip',
            manager=self.manager
        )

    def load_music(self, file_name):
        music_path = os.path.join('assets', file_name)
        if not os.path.exists(music_path):
            raise FileNotFoundError(f"Music file not found: {music_path}")
        pygame.mixer.music.load(music_path)

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play_pause_button:
                    if self.music_playing:
                        pygame.mixer.music.pause()
                        self.play_pause_button.set_text('Play')
                    else:
                        pygame.mixer.music.unpause()
                        self.play_pause_button.set_text('Pause')
                    self.music_playing = not self.music_playing
                elif event.ui_element == self.skip_button:
                    self.skip_track()

    def skip_track(self):
        self.current_track_index = (self.current_track_index + 1) % len(self.music_files)
        self.load_music(self.music_files[self.current_track_index])
        pygame.mixer.music.play(-1)  # Play the new track in a loop
        if not self.music_playing:
            pygame.mixer.music.pause()

# Function to create and return a MusicManager instance
def create_music_manager(manager, width, height):
    return MusicManager(manager, width, height)
