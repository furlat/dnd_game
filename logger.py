import pygame
import pygame_gui
from combat import CombatSimulator, ActionText

pygame.init()

pygame.display.set_caption('Combat Log')
window_surface = pygame.display.set_mode((800, 600))
manager = pygame_gui.UIManager((800, 600))

background = pygame.Surface((800, 600))
background.fill(pygame.Color("#000000"))

combat_log = pygame_gui.elements.UITextBox(
    relative_rect=pygame.Rect(50, 50, 700, 500),
    html_text="",
    manager=manager
)

combat_simulator = CombatSimulator()
combat_iterator = iter(combat_simulator)

clock = pygame.time.Clock()
is_running = True

def format_log_entry(action_text: ActionText):
    color = "#FF0000" if action_text.attacker_name == "Goblin" else "#00FF00"
    return f'<font color={color}>{action_text.to_html()}</font>'

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                try:
                    action_texts = next(combat_iterator)
                    for action_text in action_texts:
                        combat_log.append_html_text(format_log_entry(action_text))
                except StopIteration:
                    combat_log.append_html_text("<br>Combat has ended!")
        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()