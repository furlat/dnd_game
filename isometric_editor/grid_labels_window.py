import pygame
import pygame_gui

class GridLabelsWindow:
    def __init__(self, manager, rect):
        self.manager = manager
        self.rect = rect
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager
        )
        self.terrain_buttons = {}
        self.entity_buttons = {}
        self.active_tag = "floor"
        self.active_entity = None
        self.show_terrain_labels = False
        self.show_entity_labels = False
        self.setup_ui()

    def setup_ui(self):
        half_height = self.rect.height // 2
        button_height = 40
        spacing = 5
        toggle_button_spacing = 15  # Extra spacing for toggle buttons

        # Terrain Labels
        y_offset = spacing
        self.toggle_terrain_labels_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(5, y_offset, self.rect.width - 10, button_height),
            text='Toggle Terrain Labels',
            manager=self.manager,
            container=self.panel
        )
        y_offset += button_height + toggle_button_spacing

        for tag in ["floor", "water", "wall", "void", "None"]:
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(5, y_offset, self.rect.width - 10, button_height),
                text=tag.capitalize(),
                manager=self.manager,
                container=self.panel
            )
            self.terrain_buttons[tag] = button
            y_offset += button_height + spacing

        # Entity Labels
        y_offset = half_height + spacing
        self.toggle_entity_labels_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(5, y_offset, self.rect.width - 10, button_height),
            text='Toggle Entity Labels',
            manager=self.manager,
            container=self.panel
        )
        y_offset += button_height + toggle_button_spacing

        self.entity_dict = {
            "skeleton": "assets/sprites/skeleton.png",
            "goblin": "assets/sprites/goblin.png",
            "None": None
        }
        for entity, sprite_path in self.entity_dict.items():
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect(5, y_offset, self.rect.width - 10, button_height),
                text=entity.capitalize(),
                manager=self.manager,
                container=self.panel
            )
            self.entity_buttons[entity] = button
            y_offset += button_height + spacing

        self.remove_all_entities_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(5, self.rect.height - button_height - spacing, self.rect.width - 10, button_height),
            text='Remove All Entities',
            manager=self.manager,
            container=self.panel
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element in self.terrain_buttons.values():
                self.active_tag = [tag for tag, button in self.terrain_buttons.items() if button == event.ui_element][0]
                return 'terrain_tag_selected'
            elif event.ui_element in self.entity_buttons.values():
                self.active_entity = [entity for entity, button in self.entity_buttons.items() if button == event.ui_element][0]
                return 'entity_selected'
            elif event.ui_element == self.toggle_terrain_labels_button:
                self.show_terrain_labels = not self.show_terrain_labels
                return 'toggle_terrain_labels'
            elif event.ui_element == self.toggle_entity_labels_button:
                self.show_entity_labels = not self.show_entity_labels
                return 'toggle_entity_labels'
            elif event.ui_element == self.remove_all_entities_button:
                return 'remove_all_entities'
        return None

    def get_active_tag(self):
        return self.active_tag

    def get_active_entity(self):
        return self.active_entity