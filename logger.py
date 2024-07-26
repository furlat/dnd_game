import pygame
import pygame_gui
from combat import CombatSimulator, ActionText
from character_info import CharacterInfoWindow

pygame.init()

pygame.display.set_caption('Combat Log')
window_surface = pygame.display.set_mode((1600, 1200))
manager = pygame_gui.UIManager((1600, 1200))

background = pygame.Surface((1600, 1200))
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

character_windows = {}

while is_running:
    time_delta = clock.tick(60)/1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                try:
                    logs = next(combat_iterator)
                    for log in logs:
                        combat_log.append_html_text(log.to_html())
                        #check if character wrindow exists
                    if log.attacker.id  in character_windows:
                        #update the character window
                        print(f"updating {log.attacker.id}")
                        character_windows[log.attacker.id].update_character_info(log.attacker)
                        character_windows[log.attacker.id].info_textbox._reparse_and_rebuild()
                    if log.defender.id in character_windows:
                        print(f"updating {log.defender.id}")
                        character_windows[log.defender.id].update_character_info(log.defender)
                        character_windows[log.defender.id].info_textbox._reparse_and_rebuild()
                except StopIteration:
                    combat_log.append_html_text("<br>Combat has ended!")

        if event.type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
            if event.link_target.startswith("entity:"):
                entity_id = event.link_target.split(":")[1]
                if entity_id not in character_windows:
                    if entity_id == combat_simulator.goblin.id:
                        character = combat_simulator.goblin
                    elif entity_id == combat_simulator.skeleton.id:
                        character = combat_simulator.skeleton
                    else:
                        continue
                    
                    character_windows[entity_id] = CharacterInfoWindow(manager, character)
                else:
                    character_windows[entity_id].show()

        manager.process_events(event)

    manager.update(time_delta)

    window_surface.blit(background, (0, 0))
    manager.draw_ui(window_surface)

    pygame.display.update()