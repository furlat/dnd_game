import pygame
import pygame_gui
from neurorefactor.config import config
from neurorefactor.event_handler import event_handler
from neurorefactor.ui.battlemap_window import create_battlemap_window
from neurorefactor.ui.details_window import create_details_window
from neurorefactor.ui.actions_window import create_actions_window
from neurorefactor.ui.logger_window import create_logger_window
from neurorefactor.ui.active_entity_window import create_active_entity_window
from neurorefactor.ui.target_window import create_target_window

def main():
    pygame.init()

    pygame.display.set_caption(config.window.title)
    window_surface = pygame.display.set_mode((config.window.width, config.window.height))

    background = pygame.Surface((config.window.width, config.window.height))
    background.fill(pygame.Color("#000000"))

    manager = pygame_gui.UIManager((config.window.width, config.window.height), config.theme.path)

    battlemap_window = create_battlemap_window(manager)
    details_window = create_details_window(manager)
    actions_window = create_actions_window(manager)
    logger_window = create_logger_window(manager)
    active_entity_window = create_active_entity_window(manager)
    target_window = create_target_window(manager)

    clock = pygame.time.Clock()
    is_running = True

    while is_running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            manager.process_events(event)
            event_handler.handle_pygame_event(event)

        manager.update(time_delta)

        window_surface.blit(background, (0, 0))
        manager.draw_ui(window_surface)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()