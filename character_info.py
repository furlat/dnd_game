import pygame
import pygame_gui
from pygame_gui.elements import UIImage, UITextBox

class CharacterInfoWindow(pygame_gui.elements.UIWindow):
    def __init__(self, manager, character):
        super().__init__(pygame.Rect((900, 50), (400, 300)),
                         manager,
                         window_display_title=f'{character.name} Info',
                         object_id="#character_info_window")

        self.character = character

        self.info_text = self._generate_character_info()
        self.info_textbox = UITextBox(
            html_text=self.info_text,
            relative_rect=pygame.Rect((10, 10), (380, 280)),
            manager=manager,
            container=self,
            parent_element=self
        )

    def _generate_character_info(self):
        return (
            f"<b>Name:</b> {self.character.name}<br>"
            f"<b>HP:</b> {self.character.health.current_hit_points}/{self.character.health.max_hit_points}<br>"
            f"<b>AC:</b> {self.character.armor_class.total_ac}<br>"
            f"<b>STR:</b> {self.character.ability_scores.strength.apply().total_bonus} "
            f"<b>DEX:</b> {self.character.ability_scores.dexterity.apply().total_bonus} "
            f"<b>CON:</b> {self.character.ability_scores.constitution.apply().total_bonus}<br>"
            f"<b>INT:</b> {self.character.ability_scores.intelligence.apply().total_bonus} "
            f"<b>WIS:</b> {self.character.ability_scores.wisdom.apply().total_bonus} "
            f"<b>CHA:</b> {self.character.ability_scores.charisma.apply().total_bonus}<br>"
        )
    
    def update_character_info(self, character):
        self.character = character
        self.info_text = self._generate_character_info()
        self.info_textbox.html_text = self.info_text