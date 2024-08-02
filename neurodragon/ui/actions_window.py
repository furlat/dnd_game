import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UIScrollingContainer
from pygame_gui.core import ObjectID
from typing import List, Optional
from dnd.actions import Attack, MovementAction, Action
from dnd.battlemap import Entity
from neurorefactor.config import config
from neurorefactor.event_handler import event_handler, handle_game_event, GameEventType, GameEvent

class ActionsWindow(UIWindow):
    def __init__(self, rect: pygame.Rect, manager: pygame_gui.UIManager):
        super().__init__(rect, manager, window_display_title='Available Actions')

        self.active_entity: Optional[Entity] = None
        self.target_entity: Optional[Entity] = None
        self.actions: List[Action] = []
        self.action_buttons: List[UIButton] = []

        self.reset_button = UIButton(
            relative_rect=pygame.Rect(10, 10, rect.width - 20, 30),
            text='Reset Action Economy',
            manager=manager,
            container=self
        )

        container_height = rect.height - 50
        self.actions_container = UIScrollingContainer(
            relative_rect=pygame.Rect(0, 50, rect.width, container_height),
            manager=manager,
            container=self
        )

        # Set initial scrollable area to be slightly larger than the container
        self.actions_container.set_scrollable_area_dimensions((rect.width, container_height + 1))

        self.setup_event_handlers()

    def setup_event_handlers(self):
        @handle_game_event(GameEventType.ENTITY_SELECTED)
        def on_entity_selected(event: GameEvent):
            self.update_actions(event.data['entity'])

        @handle_game_event(GameEventType.TARGET_SET)
        def on_target_set(event: GameEvent):
            if 'entity' in event.data:
                self.update_actions(self.active_entity, event.data['entity'])
            else:
                self.update_actions(self.active_entity)

    def update_actions(self, entity: Optional[Entity], target_entity: Optional[Entity] = None):
        self.active_entity = entity
        self.target_entity = target_entity
        if entity is not None:
            self.actions = entity.actions
        else:
            self.actions = []
        self._create_action_buttons()

    def _create_action_buttons(self):
        for button in self.action_buttons:
            button.kill()
        self.action_buttons.clear()

        button_height = 50
        spacing = 5
        total_height = max(len(self.actions) * (button_height + spacing), self.actions_container.rect.height + 1)
        
        self.actions_container.set_scrollable_area_dimensions((self.actions_container.rect.width, total_height))

        for i, action in enumerate(self.actions):
            button_theme = self._get_button_theme(action)
            button = UIButton(
                relative_rect=pygame.Rect(5, i * (button_height + spacing), self.actions_container.rect.width - 10, button_height),
                text=action.name,
                manager=self.ui_manager,
                container=self.actions_container,
                object_id=ObjectID(class_id=button_theme, object_id=f"#action_button_{i}")
            )
            self.action_buttons.append(button)

    def _get_button_theme(self, action: Action) -> str:
        print(f"Checking button theme for action: {action.name}")
        if isinstance(action, Attack) and self.target_entity:
            context = {"action": action}
            can_perform, details = action.check_prerequisites(self.active_entity, self.target_entity, context)
            print(f"Action: {action.name}, Can Perform: {can_perform} with details {details}")
            return "@action_button_green" if can_perform else "@action_button_red"
        elif isinstance(action, MovementAction):
            return "@action_button_blue"
        return "@action_button_gray"

    def process_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.reset_button:
                self._handle_reset_action_economy()
            else:
                for i, button in enumerate(self.action_buttons):
                    if event.ui_element == button:
                        self._handle_action_click(i)
                        break
        super().process_event(event)

    def _handle_reset_action_economy(self):
        if self.active_entity:
            self.active_entity.action_economy.reset()
            event_handler.dispatch_game_event(GameEventType.UPDATE_ACTIONS, {"entity": self.active_entity})

    def _handle_action_click(self, action_index: int):
        if 0 <= action_index < len(self.actions):
            action: Action = self.actions[action_index]
            result = action.apply(self.active_entity, self.target_entity)
            event_handler.dispatch_game_event(GameEventType.ACTION_PERFORMED, {
                "action": action,
                "result": result,
                "attacker": self.active_entity,
                "defender": self.target_entity
            })
            self.update_actions(self.active_entity, self.target_entity)

def create_actions_window(manager: pygame_gui.UIManager) -> ActionsWindow:
    window_rect = pygame.Rect(**config.ui.actions_window)
    return ActionsWindow(window_rect, manager)