import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton
from typing import List, Optional

class ActionsWindow(UIWindow):
    def __init__(self, rect, manager):
        super().__init__(rect, manager, window_display_title='Available Actions')

        self.active_entity = None
        self.actions = []
        self.action_buttons = []

        self.actions_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, rect.width, rect.height),
            manager=manager,
            container=self
        )

    def update_actions(self, entity):
        if entity != self.active_entity:
            self.active_entity = entity
            if entity:
                entity.update_available_actions()
                self.actions = entity.actions
            else:
                self.actions = []
            self._create_action_buttons()

    def _create_action_buttons(self):
        # Clear existing buttons
        for button in self.action_buttons:
            button.kill()
        self.action_buttons.clear()

        # Create new buttons
        button_height = 50
        total_height = len(self.actions) * (button_height + 5)
        self.actions_container.set_scrollable_area_dimensions((self.actions_container.rect.width, total_height))

        for i, action in enumerate(self.actions):
            button = UIButton(
                relative_rect=pygame.Rect(5, i * (button_height + 5), self.actions_container.rect.width - 10, button_height),
                text=action.name,
                manager=self.ui_manager,
                container=self.actions_container
            )
            self.action_buttons.append(button)

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for i, button in enumerate(self.action_buttons):
                if event.ui_element == button:
                    self._handle_action_click(i)
                    break
        super().process_event(event)

    def _handle_action_click(self, action_index):
        if 0 <= action_index < len(self.actions):
            action = self.actions[action_index]
            print(f"Action clicked: {action.name}")
            # Here you can implement the logic for executing the action

def create_actions_window(manager, width, height):
    window_rect = pygame.Rect(int(width) - 300, 0, 300, int(height) - 150)
    return ActionsWindow(window_rect, manager)