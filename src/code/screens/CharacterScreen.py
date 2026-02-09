import pygame
import pygame_widgets
from pygame_widgets.button import Button

from skeletons.screen import Screen
from skeletons.character import Character
from skeletons.character_classes.characters import CHARACTER_REGISTRY
from assets.assets import getFont
from screens.SettingsScreen import SETTINGS

from data.storage import save_settings


class CharacterScreen(Screen):
    def __init__(self, screen, caption):
        self.clear_widgets()
        self.row_rects = []
        button_width = 150
        button_height = 50
        button_spacing = 20
        start_y = (screen.get_height() / 2) - ((button_height + button_spacing) * 2)
        self.dt = 0
        self.clock = pygame.time.Clock()
        self.selected_character = SETTINGS.get("character", "character1")

        self.character_previews = self._create_previews()

        # Define buttons
        self.character_ids = list(CHARACTER_REGISTRY.keys())
        if self.selected_character not in CHARACTER_REGISTRY and self.character_ids:
            self.selected_character = self.character_ids[0]
            SETTINGS["character"] = self.selected_character
            save_settings(SETTINGS)
        grid_x = (screen.get_width() / 2) - 320
        list_top = (screen.get_height() / 2) - 200
        list_bottom = (screen.get_height() / 2) + 260
        available_height = max(180, list_bottom - list_top)
        row_height = max(
            70, min(110, int(available_height / max(1, len(self.character_ids))))
        )
        row_width = 640
        grid_y = list_top
        for idx, _ in enumerate(self.character_ids):
            y = grid_y + idx * row_height
            self.row_rects.append(pygame.Rect(grid_x, y, row_width, row_height - 10))

        self.back_btn = Button(
            screen,
            40,
            screen.get_height() - 90,
            button_width,
            button_height,
            False,
            text="Back",
            onClick=self.onBtnBack,
            font=getFont(30),
            radius=10,
        )

        # Set Title Text
        self.title_text = "Character Selection"
        self.title_width = getFont(60).size(self.title_text)[0]

        super().__init__(screen, caption)

    def onBtnBack(self):
        self.running = False
        from screens.TitleScreen import TitleScreen

        TitleScreen(self.screen, "Title Screen")

    def _create_previews(self):
        previews = {}
        for character_id, character_cls in CHARACTER_REGISTRY.items():
            character_instance = character_cls()
            preview = character_instance.build(pygame.Vector2(0, 0))
            preview.set_state("walk", force=True)
            preview.scale_x = character_instance.sprite_scale[0]
            preview.scale_y = character_instance.sprite_scale[1]
            previews[character_id] = preview
        return previews

    def selectCharacter(self, character_id):
        SETTINGS["character"] = character_id
        self.selected_character = character_id
        save_settings(SETTINGS)

    def _draw_checkmark(self, x, y, selected):
        color = (40, 200, 40) if selected else (160, 160, 160)
        box_size = 26
        pygame.draw.rect(
            self.screen, color, (x, y, box_size, box_size), 2, border_radius=4
        )
        if selected:
            pygame.draw.line(self.screen, color, (x + 6, y + 14), (x + 12, y + 20), 3)
            pygame.draw.line(self.screen, color, (x + 12, y + 20), (x + 20, y + 6), 3)

    def run(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                return  # Exit immediately without drawing
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, row_rect in enumerate(self.row_rects):
                    if row_rect.collidepoint(event.pos):
                        self.selectCharacter(self.character_ids[idx])

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            self.running = False
            from screens.TitleScreen import TitleScreen

            TitleScreen(self.screen, "Title Screen")
            return  # Exit immediately to prevent further updates

        # Fill screen with Background Image
        self.set_backgroundImage("character_selection.jpg")

        # Draw the Title
        self.draw_text(
            self.title_text,
            getFont(60),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - (self.title_width / 2),
            (self.screen.get_height() / 2) - 235,
        )

        # Draw selection grid rows (checkbox + label + animated preview)
        for idx, row_rect in enumerate(self.row_rects):
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = row_rect.collidepoint(mouse_pos)
            character_id = self.character_ids[idx]
            character_name = CHARACTER_REGISTRY[character_id].name
            current_character = SETTINGS.get("character", self.character_ids[0])
            is_selected = current_character == character_id
            base_color = (30, 30, 30) if is_hovered else (20, 20, 20)
            border_color = (140, 140, 140) if is_hovered else (90, 90, 90)
            pygame.draw.rect(self.screen, base_color, row_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, row_rect, 2, border_radius=8)
            self._draw_checkmark(row_rect.x + 14, row_rect.y + 18, is_selected)
            self.draw_text(
                character_name,
                getFont(24),
                255,
                255,
                255,
                row_rect.x + 52,
                row_rect.y + 18,
            )

        # Draw current selection text and previews
        selected_id = SETTINGS.get("character", self.character_ids[0])
        if selected_id not in CHARACTER_REGISTRY:
            selected_id = self.character_ids[0]
        selected_name = CHARACTER_REGISTRY[selected_id].name
        self.draw_text(
            f"Selected: {selected_name}",
            getFont(24),
            255,
            255,
            255,
            (self.screen.get_width() / 2) - 140,
            (self.screen.get_height() / 2) + 300,
        )
        for idx, character_id in enumerate(self.character_ids):
            preview = self.character_previews[character_id]
            row_rect = self.row_rects[idx]
            preview.set_center(pygame.Vector2(row_rect.right - 80, row_rect.centery))
            preview.update_state(is_on_ground=True, is_moving=True)
            preview.update(self.dt)
            preview.draw(self.screen)

        # Draw the buttons and toggle
        self.back_btn.draw()

        # Update widgets
        pygame_widgets.update(events)

        # Update Screen
        pygame.display.update()
        self.dt = min(self.clock.tick() / 1000, 0.0167)
