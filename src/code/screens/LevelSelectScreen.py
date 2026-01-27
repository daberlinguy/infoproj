import pygame
from data.storage import load_worlds, save_settings
from screens.SettingsScreen import SETTINGS
from skeletons.screen import Screen
from assets.assets import getFont


class LevelSelectScreen(Screen):
    def __init__(self, screen, caption, world_id):
        self.clear_widgets()
        self.world_id = world_id
        self.worlds = load_worlds()
        self.world = self.worlds.get(world_id)
        self.levels = self.world["levels"] if self.world else []
        self.page = 0
        self.levels_per_page = 5
        self.row_rects = []
        self.prev_rect = None
        self.next_rect = None
        self.dt = 0
        self.clock = pygame.time.Clock()

        grid_x = (screen.get_width() / 2) - 320
        grid_y = (screen.get_height() / 2) - 160
        row_height = 90
        row_width = 640
        for idx in range(self.levels_per_page):
            y = grid_y + idx * row_height
            self.row_rects.append(pygame.Rect(grid_x, y, row_width, row_height - 10))

        self.prev_rect = pygame.Rect(
            grid_x, grid_y + self.levels_per_page * row_height + 10, 140, 44
        )
        self.next_rect = pygame.Rect(
            grid_x + row_width - 140,
            grid_y + self.levels_per_page * row_height + 10,
            140,
            44,
        )

        super().__init__(screen, caption)

    def select_level(self, level):
        self.running = False
        SETTINGS["selected_world"] = self.world_id
        SETTINGS["selected_level"] = level["id"]
        save_settings(SETTINGS)
        from screens.GameScreen import GameScreen

        GameScreen(self.screen, "Game", level_path=level["path"])

    def _get_page_levels(self):
        start = self.page * self.levels_per_page
        end = start + self.levels_per_page
        return self.levels[start:end]

    def run(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return  # Exit immediately without drawing
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                from screens.WorldSelectScreen import WorldSelectScreen

                WorldSelectScreen(self.screen, "Worlds")
                return  # Exit immediately to prevent further updates
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.prev_rect.collidepoint(event.pos):
                    self.page = max(0, self.page - 1)
                if self.next_rect.collidepoint(event.pos):
                    max_page = max(0, (len(self.levels) - 1) // self.levels_per_page)
                    self.page = min(max_page, self.page + 1)
                for idx, row_rect in enumerate(self.row_rects):
                    levels_page = self._get_page_levels()
                    if idx >= len(levels_page):
                        continue
                    if row_rect.collidepoint(event.pos):
                        self.select_level(levels_page[idx])

        self.set_backgroundImage("title.jpg")
        title = f"Levels - {self.world_id}" if self.world else "Levels"
        self.draw_text(
            title,
            getFont(48),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 200,
            (self.screen.get_height() / 2) - 260,
        )

        if not self.levels:
            self.draw_text(
                "No levels found for this world",
                getFont(24),
                255,
                255,
                255,
                (self.screen.get_width() / 2) - 220,
                (self.screen.get_height() / 2) - 20,
            )
        else:
            mouse_pos = pygame.mouse.get_pos()
            levels_page = self._get_page_levels()
            progress = (
                SETTINGS.get("progress", {})
                .get("worlds", {})
                .get(self.world_id, {})
                .get("levels", {})
            )
            for idx, row_rect in enumerate(self.row_rects):
                if idx >= len(levels_page):
                    continue
                level = levels_page[idx]
                is_hovered = row_rect.collidepoint(mouse_pos)
                is_completed = progress.get(level["id"], False)
                base_color = (30, 30, 30) if is_hovered else (20, 20, 20)
                border_color = (
                    (40, 200, 40)
                    if is_completed
                    else ((140, 140, 140) if is_hovered else (90, 90, 90))
                )
                pygame.draw.rect(self.screen, base_color, row_rect, border_radius=8)
                pygame.draw.rect(
                    self.screen, border_color, row_rect, 2, border_radius=8
                )
                self.draw_text(
                    level["name"],
                    getFont(24),
                    255,
                    255,
                    255,
                    row_rect.x + 20,
                    row_rect.y + 18,
                )

            total_pages = max(1, (len(self.levels) - 1) // self.levels_per_page + 1)
            page_label = f"{self.page + 1} / {total_pages}"
            self.draw_text(
                page_label,
                getFont(20),
                255,
                255,
                255,
                (self.screen.get_width() / 2) - 30,
                self.prev_rect.y + 8,
            )

            pygame.draw.rect(self.screen, (50, 50, 50), self.prev_rect, border_radius=6)
            pygame.draw.rect(
                self.screen, (120, 120, 120), self.prev_rect, 2, border_radius=6
            )
            self.draw_text(
                "Prev",
                getFont(20),
                255,
                255,
                255,
                self.prev_rect.x + 36,
                self.prev_rect.y + 8,
            )

            pygame.draw.rect(self.screen, (50, 50, 50), self.next_rect, border_radius=6)
            pygame.draw.rect(
                self.screen, (120, 120, 120), self.next_rect, 2, border_radius=6
            )
            self.draw_text(
                "Next",
                getFont(20),
                255,
                255,
                255,
                self.next_rect.x + 36,
                self.next_rect.y + 8,
            )

        pygame.display.update()
        self.dt = min(self.clock.tick() / 1000, 0.0167)
