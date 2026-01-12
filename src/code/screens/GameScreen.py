import pygame
from pygame_widgets.button import Button
import sys

from skeletons.screen import Screen
from assets.assets import getFont

class GameScreen(Screen):
    def __init__(this, screen, caption):
        this.dt = 0
        this.clock=pygame.time.Clock()

        this.player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

        super().__init__(screen, caption)

    def onBtnOpenGameScreen(this):
        print("Game Screen would open here.")  # Add your game screen transition here

    def run(this):
        pygame.display.set_caption(f"X: {this.player_pos.x} Y: {this.player_pos.y}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                this.running = False
                exit()
                pygame.quit()

        this.screen.fill("purple")

        pygame.draw.circle(this.screen, "red", this.player_pos, 40)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            this.player_pos.y -= 300 * this.dt
        if keys[pygame.K_s]:
            this.player_pos.y += 300 * this.dt
        if keys[pygame.K_a]:
            this.player_pos.x -= 300 * this.dt
        if keys[pygame.K_d]:
            this.player_pos.x += 300 * this.dt
        if keys[pygame.K_ESCAPE]:
            this.running = False
            from screens.TitleScreen import TitleScreen
            TitleScreen(this.screen, "Title Screen")

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Limits FPS to 60
        this.dt = this.clock.tick(60) / 1000
