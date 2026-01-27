import pygame
from data.storage import load_worlds, save_settings
from screens.SettingsScreen import SETTINGS
from skeletons.screen import Screen
from assets.assets import getFont


class WorldSelectScreen(Screen):
    def __init__(self, screen, caption):
        self.clear_widgets()
        self.worlds = load_worlds()
        self.world_ids = list(self.worlds.keys())
        self.row_rects = []
        self.dt = 0
        self.clock = pygame.time.Clock()

        grid_x = (screen.get_width() / 2) - 320
        grid_y = (screen.get_height() / 2) - 160
        row_height = 100
        row_width = 640
        for idx, _ in enumerate(self.world_ids[:5]):
            y = grid_y + idx * row_height
            self.row_rects.append(pygame.Rect(grid_x, y, row_width, row_height - 10))

        super().__init__(screen, caption)

    def select_world(self, world_id):
        self.running = False
        SETTINGS["selected_world"] = world_id
        save_settings(SETTINGS)
        from screens.LevelSelectScreen import LevelSelectScreen

        LevelSelectScreen(self.screen, "Levels", world_id)

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return  # Exit immediately without drawing
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                from screens.TitleScreen import TitleScreen

                TitleScreen(self.screen, "Title Screen")
                return  # Exit immediately to prevent further updates
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, row_rect in enumerate(self.row_rects):
                    if row_rect.collidepoint(event.pos):
                        self.select_world(self.world_ids[idx])

        self.set_backgroundImage("title.jpg")
        self.draw_text(
            "Worlds",
            getFont(60),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 120,
            (self.screen.get_height() / 2) - 260,
        )

        if not self.world_ids:
            self.draw_text(
                "No worlds found in ./data/worlds",
                getFont(24),
                255,
                255,
                255,
                (self.screen.get_width() / 2) - 220,
                (self.screen.get_height() / 2) - 20,
            )
        else:
            mouse_pos = pygame.mouse.get_pos()
            progress = SETTINGS.get("progress", {}).get("worlds", {})
            for idx, row_rect in enumerate(self.row_rects):
                world_id = self.world_ids[idx]
                world = self.worlds[world_id]
                is_hovered = row_rect.collidepoint(mouse_pos)
                is_selected = SETTINGS.get("selected_world") == world_id
                is_completed = progress.get(world_id, {}).get("complete", False)
                base_color = (30, 30, 30) if is_hovered else (20, 20, 20)
                border_color = (
                    (40, 200, 40)
                    if is_completed
                    else (
                        (160, 160, 160)
                        if is_selected
                        else ((140, 140, 140) if is_hovered else (90, 90, 90))
                    )
                )
                pygame.draw.rect(self.screen, base_color, row_rect, border_radius=8)
                pygame.draw.rect(
                    self.screen, border_color, row_rect, 2, border_radius=8
                )
                self.draw_text(
                    world["name"],
                    getFont(28),
                    255,
                    255,
                    255,
                    row_rect.x + 20,
                    row_rect.y + 20,
                )

        pygame.display.update()
        self.dt = min(self.clock.tick() / 1000, 0.0167)
