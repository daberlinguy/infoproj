import pygame
from pygame_widgets.button import Button
import sys

from skeletons.screen import Screen
from skeletons.spieler import Spieler
from skeletons.platform import Platform
from assets.assets import getFont

class GameScreen(Screen):
    def __init__(this, screen, caption):
        this.dt = 0
        this.clock=pygame.time.Clock()

        this.player_pos = pygame.Vector2(screen.get_width() / 2, 100)
        this.player = Spieler(this.player_pos, this.dt)
        
        # Create platforms
        this.platforms = [
            Platform(200, 500, 300, 20, (139, 69, 19)),  # Brown platform
            Platform(600, 400, 250, 20, (34, 139, 34)),   # Green platform
            Platform(400, 600, 400, 20, (169, 169, 169)), # Gray platform (ground)
            Platform(900, 300, 200, 20, (255, 140, 0))    # Orange platform
        ]

        super().__init__(screen, caption)

    def onBtnOpenGameScreen(this):
        print("Game Screen would open here.")  # Add your game screen transition here

    def run(this):
        pygame.display.set_caption(f"X: {int(this.player_pos.x)} Y: {int(this.player_pos.y)} On Ground: {this.player.is_on_ground}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                this.running = False
                exit()
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                    this.player.jump()

        this.screen.fill("purple")

        # Draw platforms
        for platform in this.platforms:
            platform.draw(this.screen)

        # Draw player
        pygame.draw.circle(this.screen, "red", this.player_pos, this.player.radius)

        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            this.player.move_left()
        if keys[pygame.K_d]:
            this.player.move_right()
        if keys[pygame.K_ESCAPE]:
            this.running = False
            from screens.TitleScreen import TitleScreen
            TitleScreen(this.screen, "Title Screen")

        # Update player dt
        this.player.dt = this.dt
        
        # Apply physics
        this.player.apply_gravity(this.dt)
        this.player.check_platform_collision(this.platforms)

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Limits FPS to 60
        this.dt = this.clock.tick(60) / 1000
