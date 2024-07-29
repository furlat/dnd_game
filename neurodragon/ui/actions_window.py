import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton
from pygame_gui.core import ObjectID
from typing import List, Optional
from dnd.actions import Attack, MovementAction, Action
from dnd.battlemap  import Entity
# At the top of your file, after other imports
ACTION_COMPLETED = pygame.USEREVENT + 777

class ActionsWindow(UIWindow):
    def __init__(self, rect, manager):
        super().__init__(rect, manager, window_display_title='Available Actions')

        self.active_entity = None
        self.target_entity = None
        self.actions = []
        self.action_buttons = []
        self.handled_action=None

        self.actions_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=pygame.Rect(0, 0, rect.width, rect.height),
            manager=manager,
            container=self
        )

    def update_actions(self, entity, target_entity=None, force_update=False):
        if force_update or entity != self.active_entity or target_entity != self.target_entity:
            self.active_entity = entity
            self.target_entity = target_entity
            if entity:
                print(f"Updating actions for entity: {entity.name}")
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
            button_theme = self._get_button_theme(action)
            button = UIButton(
                relative_rect=pygame.Rect(5, i * (button_height + 5), self.actions_container.rect.width - 10, button_height),
                text=action.name,
                manager=self.ui_manager,
                container=self.actions_container,
                object_id=ObjectID(class_id=button_theme, object_id=f"#action_button_{i}")
            )
            self.action_buttons.append(button)

    def _get_button_theme(self, action: Action):
        if isinstance(action, (Attack)) and self.target_entity:
            print(f"Checking check_prerequisitess for action: {action.name}")
            context = {"action": action}
            can_perform, failed_conditions = action.check_prerequisites(self.active_entity, self.target_entity, context)
            if can_perform:
                print(f"Prerequisites passed for action: {action.name}")
                return "@action_button_green"
            else:
                print(f"Prerequisites failed for action: {action.name}")
                print(f"Failed conditions: {failed_conditions}")
                return "@action_button_red"
        return "@action_button_gray"  # Default color for non-attack actions or when no target is selected

    def _process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            for i, button in enumerate(self.action_buttons):
                if event.ui_element == button:
                    self._handle_action_click(i)
                    break
        # elif event.type == pygame.USEREVENT:
        #     if hasattr(event, 'user_type'):
        #         if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
        #             for i, button in enumerate(self.action_buttons):
        #                 if event.ui_element == button:
        #                     self._handle_action_click(i)
        #                     break
        
        # super().process_event(event)

    def _handle_action_click(self, action_index):
        if 0 <= action_index < len(self.actions):
            action : Action = self.actions[action_index]
            context = {"action": action}
            print(f"Action clicked: {action.name}")
            if isinstance(action, (Attack)) and self.target_entity:
                can_perform, failed_conditions = action.check_prerequisites(self.active_entity, self.target_entity, context)
                if can_perform:
                    print(f"Performing action: {action.name}")
                    result = action.apply(self.target_entity, context)
                    self.handled_action = result
                    print(f"Action result: {result}")
                    pygame.event.post(pygame.event.Event(ACTION_COMPLETED))
                else:
                    print(f"Cannot perform action: {action.name}")
                    print(f"Failed conditions: {failed_conditions}")
            else:
                print(f"Performing action: {action.name}")
                result = action.apply(self.active_entity, context=context)
                print(f"Action result: {result}")
                self.handled_action = result
                pygame.event.post(pygame.event.Event(ACTION_COMPLETED))
        self.update_actions(self.active_entity, self.target_entity)

def create_actions_window(manager, width, height):
    window_rect = pygame.Rect(int(width) - 300, 0, 300, int(height) - 150)
    return ActionsWindow(window_rect, manager)