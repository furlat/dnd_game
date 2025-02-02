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
    TOGGLE_BACKGROUND = auto()
    TOGGLE_LABELS = auto()
    TOGGLE_GRID = auto()
    ISOMETRIC_TILE_SELECTED = auto()
    ISOMETRIC_ENTITY_SELECTED = auto()
    ISOMETRIC_TARGET_SET = auto()
    LOAD_BATTLEMAP = auto()
    BATTLEMAP_LOADED = auto()

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

event_handler = EventHandler()

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