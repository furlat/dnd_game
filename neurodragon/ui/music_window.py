import pygame
import pygame_gui
from pygame_gui.elements import UIButton, UIWindow

class MusicWindow(UIWindow):
    def __init__(self, rect, manager):
        super().__init__(rect, manager, window_display_title='Music Control')
        
        self.is_playing = False
        
        self.play_pause_button = UIButton(
            relative_rect=pygame.Rect((0, 0), (200, 50)),
            text='Play',
            manager=manager,
            container=self
        )
        
        self.play_pause_button.set_position((rect.width // 2 - 100, rect.height // 2 - 25))
        
    def process_event(self, event):
        super().process_event(event)
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.play_pause_button:
                    self.toggle_music()

    def toggle_music(self):
        if self.is_playing:
            pygame.mixer.music.pause()
            self.play_pause_button.set_text('Play')
        else:
            pygame.mixer.music.unpause()
            self.play_pause_button.set_text('Pause')
        self.is_playing = not self.is_playing

def create_music_window(manager):
    window_rect = pygame.Rect(1200, 0, 200, 100)
    return MusicWindow(window_rect, manager)
