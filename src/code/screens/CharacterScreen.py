import pygame
import pygame_widgets
import sys

import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.widget import WidgetHandler

from skeletons.screen import Screen
from skeletons.character import Character
from skeletons.character_classes.characters import CHARACTER_REGISTRY
from assets.assets import getFont
from screens.SettingsScreen import SETTINGS

from data.storage import save_settings

class CharacterScreen(Screen):
    def __init__(self, screen, caption):
        widgets = WidgetHandler.getWidgets()
        WidgetHandler._widgets = widgets.__class__()
        self.row_rects = []
        button_width = 150
        button_height = 50
        button_spacing = 20
        start_y = (screen.get_height() / 2) - ((button_height + button_spacing) * 2)
        self.dt = 0
        self.clock = pygame.time.Clock()
        self.selected_character = SETTINGS.get('character', 'character1')

        self.character_previews = self._create_previews()

       # Define buttons
        self.character_ids = list(CHARACTER_REGISTRY.keys())[:3]
        grid_x = (screen.get_width() / 2) - 320
        grid_y = (screen.get_height() / 2) - 140
        row_height = 110
        row_width = 640
        for idx, _ in enumerate(self.character_ids):
            y = grid_y + idx * row_height
            self.row_rects.append(pygame.Rect(grid_x, y, row_width, row_height - 10))
        
        self.back_btn = Button(screen, 40, screen.get_height() - 90,
                              button_width, button_height, False,
                              text="Back", onClick=self.onBtnBack, 
                              font=getFont(30), radius=10)

       # Set Title Text
        self.title_text = "Platformer"
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
        SETTINGS['character'] = character_id
        self.selected_character = character_id
        save_settings(SETTINGS)

    def _draw_checkmark(self, x, y, selected):
        color = (40, 200, 40) if selected else (160, 160, 160)
        box_size = 26
        pygame.draw.rect(self.screen, color, (x, y, box_size, box_size), 2, border_radius=4)
        if selected:
            pygame.draw.line(self.screen, color, (x + 6, y + 14), (x + 12, y + 20), 3)
            pygame.draw.line(self.screen, color, (x + 12, y + 20), (x + 20, y + 6), 3)

    def run(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                exit()
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, row_rect in enumerate(self.row_rects):
                    if row_rect.collidepoint(event.pos):
                        self.selectCharacter(self.character_ids[idx])
                
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_ESCAPE]:
            self.running = False
            from screens.TitleScreen import TitleScreen
            TitleScreen(self.screen, "Title Screen")
        
        # Fill screen with Background Image
        self.set_backgroundImage("character_selection.jpg")

        # Draw the Title
        self.draw_text(self.title_text, getFont(60), 255, 255, 255,
                       (self.screen.get_width() / 2) - (self.title_width / 2), 
                       (self.screen.get_height() / 2) - 235)

        # Draw selection grid rows (checkbox + label + animated preview)
        for idx, row_rect in enumerate(self.row_rects):
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = row_rect.collidepoint(mouse_pos)
            character_id = self.character_ids[idx]
            character_name = CHARACTER_REGISTRY[character_id].name
            is_selected = SETTINGS.get('character', 'character1') == character_id
            base_color = (30, 30, 30) if is_hovered else (20, 20, 20)
            border_color = (140, 140, 140) if is_hovered else (90, 90, 90)
            pygame.draw.rect(self.screen, base_color, row_rect, border_radius=8)
            pygame.draw.rect(self.screen, border_color, row_rect, 2, border_radius=8)
            self._draw_checkmark(row_rect.x + 14, row_rect.y + 18, is_selected)
            self.draw_text(character_name, getFont(24), 255, 255, 255, row_rect.x + 52, row_rect.y + 18)

        # Draw current selection text and previews
        self.draw_text(f"Selected: {CHARACTER_REGISTRY[SETTINGS.get('character', 'character1')].name}", getFont(24), 255, 255, 255,
                       (self.screen.get_width() / 2) - 100, (self.screen.get_height() / 2) + 320)
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
