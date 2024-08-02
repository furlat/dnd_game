import pygame
import pygame_gui
from typing import Callable, Dict, List, Any
from enum import Enum, auto

class GameEventType(Enum):
    ENTITY_SELECTED = auto()
    TILE_SELECTED = auto()
    TARGET_SET = auto()
    FOV_UPDATED = auto()
    PATH_UPDATED = auto()
    ACTION_PERFORMED = auto()
    ACTION_LOG = auto()
    UPDATE_ACTIONS = auto()
    RENDER_BATTLEMAP = auto()

class GameEvent:
    def __init__(self, type: GameEventType, data: Dict[str, Any] = {}):
        self.type = type
        self.data = data

class EventHandler:
    def __init__(self):
        self.pygame_handlers: Dict[int, List[Callable[[pygame.event.Event], None]]] = {}
        self.game_handlers: Dict[GameEventType, List[Callable[[GameEvent], None]]] = {event_type: [] for event_type in GameEventType}

    def register_pygame_handler(self, event_type: int, handler: Callable[[pygame.event.Event], None]):
        if event_type not in self.pygame_handlers:
            self.pygame_handlers[event_type] = []
        self.pygame_handlers[event_type].append(handler)

    def register_game_handler(self, event_type: GameEventType, handler: Callable[[GameEvent], None]):
        self.game_handlers[event_type].append(handler)

    def handle_pygame_event(self, event: pygame.event.Event):
        if event.type in self.pygame_handlers:
            for handler in self.pygame_handlers[event.type]:
                handler(event)

    def handle_game_event(self, event: GameEvent):
        for handler in self.game_handlers[event.type]:
            handler(event)

    def dispatch_game_event(self, event_type: GameEventType, data: Dict[str, Any] = {}):
        event = GameEvent(event_type, data)
        self.handle_game_event(event)

# Global event handler instance
event_handler = EventHandler()

# Decorators for easy event handling registration
def handle_pygame_event(event_type: int):
    def decorator(func: Callable[[pygame.event.Event], None]):
        event_handler.register_pygame_handler(event_type, func)
        return func
    return decorator

def handle_game_event(event_type: GameEventType):
    def decorator(func: Callable[[GameEvent], None]):
        event_handler.register_game_handler(event_type, func)
        return func
    return decorator

# Example usage:
@handle_pygame_event(pygame_gui.UI_BUTTON_PRESSED)
def on_button_pressed(event: pygame.event.Event):
    print(f"Button pressed: {event.ui_element} dioporco")

@handle_game_event(GameEventType.ENTITY_SELECTED)
def on_entity_selected(event: GameEvent):
    print(f"Entity selected: {event.data.get('entity_id')}")

@handle_game_event(GameEventType.TILE_SELECTED)
def on_tile_selected(event: GameEvent):
    print(f"Tile selected: {event.data.get('position')}")

@handle_game_event(GameEventType.TARGET_SET)
def on_target_set(event: GameEvent):
    print(f"Target set: {event.data.get('target_position')}")

# In your main loop:
# for event in pygame.event.get():
#     event_handler.handle_pygame_event(event)
#     ui_manager.process_events(event)
#
# To dispatch a game event:
# event_handler.dispatch_game_event(GameEventType.ENTITY_SELECTED, {"entity_id": "goblin_1"})