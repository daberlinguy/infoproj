import pygame
from pygame_widgets.button import Button
import sys

from skeletons.screen import Screen
from skeletons.spieler import Spieler
from skeletons.platform import Platform, Grid
from assets.assets import getFont

class GameScreen(Screen):
    def __init__(this, screen, caption):
        this.dt = 0
        this.clock=pygame.time.Clock()

        this.player_pos = pygame.Vector2(screen.get_width() / 2, 100)
        this.player = Spieler(this.player_pos, this.dt)
        
        # Create debug grid
        this.grid = Grid(cell_size=50, color=(80, 80, 80), line_width=1)
        this.grid.visible = True  # Start with grid visible
        
        # Create platforms
        this.platforms = [
            Platform(200, 500, 300, 20, (139, 69, 19)),  # Brown platform
            Platform(600, 400, 250, 20, (34, 139, 34)),   # Green platform
            Platform(400, 600, 400, 20, (169, 169, 169)), # Gray platform (ground)
            Platform(900, 300, 200, 60, (255, 140, 0))    # Orange platform
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
                if event.key == pygame.K_g:  # Toggle grid with 'G' key
                    this.grid.toggle()
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:  # Increase grid size
                    this.grid.set_cell_size(this.grid.cell_size + 10)
                if event.key == pygame.K_MINUS:  # Decrease grid size
                    this.grid.set_cell_size(this.grid.cell_size - 10)

        this.screen.fill("purple")
        
        # Draw grid first (behind everything)
        this.grid.draw(this.screen)
        
        this.draw_text(f"FPS: {int(this.clock.get_fps())}", getFont(30), 255, 255, 255, 10, 10)


        # Draw platforms
        for platform in this.platforms:
            platform.draw(this.screen)

        # Draw player
        scale_factor = 0.2# Scale factor for the sprite and bounding box
        sprite_width = int(182 * scale_factor)
        sprite_height = int(243 * scale_factor)
        this.draw_sprite("Sprite_laufen-0001.png", 
                 this.player.player_pos.x - sprite_width / 2, 
                 this.player.player_pos.y - sprite_height / 2, 
                 sprite_width, sprite_height)
        pygame.draw.rect(this.screen, "black", 
                 pygame.Rect(this.player.player_pos.x - sprite_width / 2, 
                         this.player.player_pos.y - sprite_height / 2, 
                         sprite_width, sprite_height), 2)  # Draw scaled bounding box for debugging

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
        
        # Apply physics - apply gravity first, then check collisions to resolve
        this.player.apply_gravity(this.dt)
        for platform in this.platforms:
            pygame.draw.rect(this.screen, "red", platform.rect, 2)  # Draw platform bounding box for debugging
        this.player.check_platform_collision(this.platforms)

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Limits FPS to 60 and cap dt to prevent large jumps
        this.dt = min(this.clock.tick(60) / 1000, 0.05)  # Cap at 50ms (20 FPS minimum)
