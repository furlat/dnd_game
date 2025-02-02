import pygame
import math

class IsometricGrid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        
        # Calculate surface size
        self.surface_width = (self.width + self.height) * self.cell_size
        self.surface_height = (self.width + self.height) * self.cell_size // 2
        
        # Initialize offsets to center the grid
        self.offset_x = (1000 - self.surface_width) // 2
        self.offset_y = (800 - self.surface_height) // 2
        
        self.surface = pygame.Surface((1000, 800), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 255))  # Black background
        
        self.cubes = {}
        self.highlighted_cell = None
        self.angle = 0  # Initial rotation angle

    def draw_grid(self):
        self.surface.fill((0, 0, 0, 255))  # Clear the surface

        # Draw grid lines
        for x in range(self.width + 1):
            for y in range(self.height + 1):
                if (x, y) not in self.cubes:
                    if x < self.width:
                        start = self.grid_to_iso(x, y)
                        end = self.grid_to_iso(x + 1, y)
                        pygame.draw.line(self.surface, (255, 255, 255), start, end)
                    if y < self.height:
                        start = self.grid_to_iso(x, y)
                        end = self.grid_to_iso(x, y + 1)
                        pygame.draw.line(self.surface, (255, 255, 255), start, end)

        # Cover areas below blue cubes with black surfaces
        for (grid_x, grid_y), (draw_up, z_offset) in self.cubes.items():
            if not draw_up:
                self.cover_cube_with_black(grid_x, grid_y, draw_up, z_offset, below=True)
        
        # Cover areas above blue cubes and below red cubes with black surfaces
        for (grid_x, grid_y), (draw_up, z_offset) in self.cubes.items():
            self.cover_cube_with_black(grid_x, grid_y, draw_up, z_offset, middle=True)

        # Draw blue cubes
        for (grid_x, grid_y), (draw_up, z_offset) in self.cubes.items():
            if not draw_up:
                self.draw_cube(grid_x, grid_y, draw_up, z_offset)

        # Cover areas above red cubes with black surfaces
        for (grid_x, grid_y), (draw_up, z_offset) in self.cubes.items():
            if draw_up:
                self.cover_cube_with_black(grid_x, grid_y, draw_up, z_offset, above=True)

        # Draw red cubes
        for (grid_x, grid_y), (draw_up, z_offset) in self.cubes.items():
            if draw_up:
                self.draw_cube(grid_x, grid_y, draw_up, z_offset)

    def grid_to_iso(self, grid_x, grid_y):
        # Center of the grid
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Translate grid coordinates to be relative to the center
        trans_x = grid_x - center_x
        trans_y = grid_y - center_y
        
        # Apply rotation
        if self.angle == 90:
            new_x, new_y = trans_y, -trans_x
        elif self.angle == 180:
            new_x, new_y = -trans_x, -trans_y
        elif self.angle == 270:
            new_x, new_y = -trans_y, trans_x
        else:
            new_x, new_y = trans_x, trans_y
        
        # Translate coordinates back
        final_x = new_x + center_x
        final_y = new_y + center_y
        
        iso_x = (final_x - final_y) * self.cell_size + self.offset_x
        iso_y = (final_x + final_y) * self.cell_size // 2 + self.offset_y
        return round(iso_x), round(iso_y)

    def iso_to_grid(self, iso_x, iso_y):
        iso_x -= self.offset_x
        iso_y -= self.offset_y

        grid_y = (iso_y / (self.cell_size / 2) - iso_x / self.cell_size) / 2
        grid_x = iso_y / (self.cell_size / 2) - grid_y

        # Center of the grid
        center_x = self.width / 2
        center_y = self.height / 2

        # Translate coordinates to be relative to the center
        trans_x = grid_x - center_x
        trans_y = grid_y - center_y

        # Apply inverse rotation
        if self.angle == 90:
            new_x, new_y = -trans_y, trans_x
        elif self.angle == 180:
            new_x, new_y = -trans_x, -trans_y
        elif self.angle == 270:
            new_x, new_y = trans_y, -trans_x
        else:
            new_x, new_y = trans_x, trans_y

        # Translate coordinates back
        final_x = new_x + center_x
        final_y = new_y + center_y

        return math.floor(final_x), math.floor(final_y)

    def is_in_grid(self, iso_x, iso_y):
        grid_x, grid_y = self.iso_to_grid(iso_x, iso_y)
        return 0 <= grid_x < self.width and 0 <= grid_y < self.height

    def highlight_cell(self, grid_x, grid_y, color):
        points = [
            self.grid_to_iso(grid_x, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y + 1),
            self.grid_to_iso(grid_x, grid_y + 1)
        ]
        pygame.draw.polygon(self.surface, color, points)

    def cover_grid_with_black(self, grid_x, grid_y):
        points = [
            self.grid_to_iso(grid_x, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y + 1),
            self.grid_to_iso(grid_x, grid_y + 1)
        ]
        pygame.draw.polygon(self.surface, (0, 0, 0), points)

    def cover_cube_with_black(self, grid_x, grid_y, draw_up, z_offset, below=False, middle=False, above=False):
        top_points = [
            self.grid_to_iso(grid_x, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y + 1),
            self.grid_to_iso(grid_x, grid_y + 1)
        ]

        vertical_offset = -self.cell_size if draw_up else self.cell_size
        vertical_offset *= z_offset / self.cell_size  # Adjust based on z_offset

        # Draw black square on the bottom face for blue cubes
        if below:
            bottom_square_points = [
                (top_points[0][0], top_points[0][1] + vertical_offset),
                (top_points[1][0], top_points[1][1] + vertical_offset),
                (top_points[2][0], top_points[2][1] + vertical_offset),
                (top_points[3][0], top_points[3][1] + vertical_offset)
            ]
            pygame.draw.polygon(self.surface, (0, 0, 0), bottom_square_points)

        # Draw black square on the top face for blue cubes and bottom face for red cubes
        if middle:
            middle_square_points = [
                (top_points[0][0], top_points[0][1]),
                (top_points[1][0], top_points[1][1]),
                (top_points[2][0], top_points[2][1]),
                (top_points[3][0], top_points[3][1])
            ]
            pygame.draw.polygon(self.surface, (0, 0, 0), middle_square_points)

        # Draw black square on the top face for red cubes
        if above:
            above_square_points = [
                (top_points[0][0], top_points[0][1] + vertical_offset),
                (top_points[1][0], top_points[1][1] + vertical_offset),
                (top_points[2][0], top_points[2][1] + vertical_offset),
                (top_points[3][0], top_points[3][1] + vertical_offset)
            ]
            pygame.draw.polygon(self.surface, (0, 0, 0), above_square_points)

    def draw_cube(self, grid_x, grid_y, draw_up, z_offset):
        top_points = [
            self.grid_to_iso(grid_x, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y),
            self.grid_to_iso(grid_x + 1, grid_y + 1),
            self.grid_to_iso(grid_x, grid_y + 1)
        ]

        vertical_offset = -self.cell_size if draw_up else self.cell_size
        vertical_offset *= z_offset / self.cell_size  # Adjust based on z_offset

        cube_color = (255, 0, 0) if draw_up else (0, 0, 255)

        bottom_points = [(point[0], point[1] + vertical_offset) for point in top_points]
        for i in range(4):
            pygame.draw.line(self.surface, cube_color, top_points[i], bottom_points[i], 1)
        pygame.draw.lines(self.surface, cube_color, True, bottom_points, 1)

        pygame.draw.lines(self.surface, cube_color, True, top_points, 1)

    def render(self, screen):
        self.draw_grid()

        if self.highlighted_cell:
            self.highlight_cell(*self.highlighted_cell, (255, 255, 0, 100))

        screen.blit(self.surface, (0, 0))

        if self.highlighted_cell and self.highlighted_cell in self.cubes:
            _, z_offset = self.cubes[self.highlighted_cell]
            font = pygame.font.Font(None, 36)
            height_text = font.render(f"Height offset: {z_offset:.2f}", True, (255, 255, 255))
            screen.blit(height_text, (screen.get_width() - height_text.get_width() - 10, screen.get_height() - height_text.get_height() - 10))

    def move_grid(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy

    def toggle_cube(self, grid_x, grid_y, draw_up):
        if (grid_x, grid_y) in self.cubes:
            del self.cubes[(grid_x, grid_y)]
        else:
            self.cubes[(grid_x, grid_y)] = (draw_up, 0.5 * self.cell_size)  # Initialize at 0.5 height

    def adjust_cube_height(self, grid_x, grid_y, delta):
        if (grid_x, grid_y) in self.cubes:
            draw_up, z_offset = self.cubes[(grid_x, grid_y)]
            z_offset = min(max(0, z_offset + delta), 2 * self.cell_size)  # Ensure height offset is between 0 and 2 times the cell size
            self.cubes[(grid_x, grid_y)] = (draw_up, z_offset)

def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 800))
    clock = pygame.time.Clock()

    grid = IsometricGrid(10, 10, 40)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                iso_x, iso_y = event.pos
                if grid.is_in_grid(iso_x, iso_y):
                    grid_x, grid_y = grid.iso_to_grid(iso_x, iso_y)
                    grid.highlighted_cell = (grid_x, grid_y)
                else:
                    grid.highlighted_cell = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if grid.highlighted_cell:
                    if event.button == 1:  # Left mouse button
                        x, y = grid.highlighted_cell
                        grid.toggle_cube(x, y, True)
                    elif event.button == 3:  # Right mouse button
                        x, y = grid.highlighted_cell
                        grid.toggle_cube(x, y, False)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if grid.highlighted_cell:
                        x, y = grid.highlighted_cell
                        grid.adjust_cube_height(x, y, -0.25 * grid.cell_size)
                elif event.key == pygame.K_2:
                    if grid.highlighted_cell:
                        x, y = grid.highlighted_cell
                        grid.adjust_cube_height(x, y, 0.25 * grid.cell_size)
                elif event.key == pygame.K_r:  # Rotate grid with 'r' key
                    grid.angle = (grid.angle + 90) % 360  # Rotate by 90 degrees

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            grid.move_grid(0, -5)
        if keys[pygame.K_s]:
            grid.move_grid(0, 5)
        if keys[pygame.K_a]:
            grid.move_grid(-5, 0)
        if keys[pygame.K_d]:
            grid.move_grid(5, 0)

        screen.fill((0, 0, 0))  # Black background
        grid.render(screen)

        if grid.highlighted_cell:
            font = pygame.font.Font(None, 36)
            pos_text = font.render(f"Pos: {grid.highlighted_cell}", True, (255, 255, 255))
            screen.blit(pos_text, (screen.get_width() - pos_text.get_width() - 10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
