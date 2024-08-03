import pygame
import pygame_gui

class GridConfigWindow:
    def __init__(self, manager, rect):
        self.manager = manager
        self.rect = rect
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=self.rect,
            manager=self.manager
        )
        self.previous_values = {}

        self.sliders = {}
        self.inputs = {}
        self.is_bound = False
        self.setup_ui()

    def setup_ui(self):
        panel_width = self.rect.width
        slider_width = 180
        label_width = 90
        spacing = 10

        y_offset = spacing
        self.create_labeled_slider('Image Scale', 'image_scale', y_offset, slider_width, label_width, (10, 200), 100)
        y_offset += 50

        self.create_labeled_slider('Tile Size', 'tile_size', y_offset, slider_width, label_width, (1, 50), 10)
        y_offset += 50

        self.grid_size_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(spacing, y_offset, panel_width - 2*spacing, 20),
            text='Grid Size:',
            manager=self.manager,
            container=self.panel
        )
        y_offset += 30
        self.create_labeled_slider('Width', 'grid_size_x', y_offset, slider_width, label_width, (10, 200), 100)
        y_offset += 40
        self.create_labeled_slider('Height', 'grid_size_y', y_offset, slider_width, label_width, (10, 200), 100)
        y_offset += 50

        self.grid_origin_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(spacing, y_offset, panel_width - 2*spacing, 20),
            text='Grid Origin:',
            manager=self.manager,
            container=self.panel
        )
        y_offset += 30
        self.create_labeled_slider('X', 'grid_origin_x', y_offset, slider_width, label_width, (-1000, 1000), 0)
        y_offset += 40
        self.create_labeled_slider('Y', 'grid_origin_y', y_offset, slider_width, label_width, (-1000, 1000), 0)
        y_offset += 50

        self.create_labeled_slider('Iso Angle', 'isometric_angle', y_offset, slider_width, label_width, (1, 89), 30)
        y_offset += 50
        self.create_labeled_slider('Rotation', 'rotation', y_offset, slider_width, label_width, (-359, 359), 0)
        y_offset += 50

        self.bind_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(spacing, y_offset, panel_width - 2*spacing, 40),
            text='Bind Image to Grid',
            manager=self.manager,
            container=self.panel
        )

    def create_labeled_slider(self, label, attr_name, y_offset, slider_width, label_width, value_range, start_value):
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y_offset, label_width, 20),
            text=f'{label}:',
            manager=self.manager,
            container=self.panel
        )
        self.sliders[attr_name] = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect(10 + label_width, y_offset, slider_width, 20),
            start_value=start_value,
            value_range=value_range,
            manager=self.manager,
            container=self.panel
        )
        self.inputs[attr_name] = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(20 + label_width + slider_width, y_offset, 50, 20),
            manager=self.manager,
            container=self.panel
        )
        self.inputs[attr_name].set_text(str(start_value))
        self.previous_values[attr_name] = start_value

    def get_config(self):
        config = {
            'image_scale': int(self.sliders['image_scale'].get_current_value()),
            'tile_size': int(self.sliders['tile_size'].get_current_value()),
            'grid_size_x': int(self.sliders['grid_size_x'].get_current_value()),
            'grid_size_y': int(self.sliders['grid_size_y'].get_current_value()),
            'grid_origin_x': int(self.sliders['grid_origin_x'].get_current_value()),
            'grid_origin_y': int(self.sliders['grid_origin_y'].get_current_value()),
            'isometric_angle': self.sliders['isometric_angle'].get_current_value(),
            'rotation': self.sliders['rotation'].get_current_value(),
            'is_bound': self.is_bound
        }
        return config

    def set_config(self, config):
        for attr, value in config.items():
            if attr in self.sliders:
                self.sliders[attr].set_current_value(value)
                self.inputs[attr].set_text(str(value))
        self.is_bound = config.get('is_bound', False)
        self.update_bind_button_text()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.bind_button:
                self.is_bound = not self.is_bound
                self.update_bind_button_text()
                return 'bind_toggled'
        elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            for attr, slider in self.sliders.items():
                if event.ui_element == slider:
                    value = int(slider.get_current_value())
                    self.inputs[attr].set_text(str(value))
                    if attr in ['grid_origin_x', 'grid_origin_y']:
                        return attr
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            for attr, input_box in self.inputs.items():
                if event.ui_element == input_box:
                    try:
                        value = int(input_box.get_text())
                        self.sliders[attr].set_current_value(value)
                        if attr in ['grid_origin_x', 'grid_origin_y']:
                            return attr
                    except ValueError:
                        input_box.set_text(str(int(self.sliders[attr].get_current_value())))
        return None

    
    def get_previous_value(self, attr):
        return self.previous_values.get(attr, 0)

    def update_bind_button_text(self):
        self.bind_button.set_text('Unbind Image from Grid' if self.is_bound else 'Bind Image to Grid')