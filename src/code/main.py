import pygame
import pygame_widgets
from pygame_widgets.button import Button
import sys

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()



path=sys.argv[0].replace("main.py","")

font_path = path+'../resources/assets/fonts/font.ttf'
font_size = 40
custom_font = pygame.font.Font(font_path, font_size)

cfont = {}
for i in range(1, 100):
    cfont[i] = pygame.font.Font(font_path, i)  # Use : to create key-value pairs

def draw_text(text, font, color, surface, x, y):
    """Function to draw text on the surface."""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))

def title_screen():
    imp = pygame.image.load(path+"../resources/assets/backgrounds/title.jpg").convert()
    imp = pygame.transform.scale(imp, (1280, 720)) 
    def onbtnc():
        game_screen()  # Proceed to the game screen after button click

    running = True
    # Set font for the button to 40pt
    play_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) - 50, 
                    200, 100, False, text="Play", 
                    onClick=onbtnc, font=cfont.get(40),radius=20)
    settings_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) + 70, 
                    200, 100, False, text="Settings", 
                    onClick=onbtnc, font=cfont.get(40),radius=20)
    exit_btn = Button(screen, (screen.get_width() / 2) - 100, (screen.get_height() / 2) + 190, 
                    200, 100, False, text="Exit", onClick=exit, font=cfont.get(40),radius=20)

    title_text = "Platformer"
    title_width, title_height = cfont.get(60).size(title_text)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.set_caption("Platformer: Title Screen")
        
        # Fill screen
        screen.blit(imp, (0, 0))
        # Draw the title
        draw_text("Platformer", cfont.get(60), "white", screen, 
                   (screen.get_width() / 2) - (title_width / 2), 
                   (screen.get_height() / 2) - 200)

        # Draw the button
        play_btn.draw()
        settings_btn.draw()
        exit_btn.draw()
        pygame_widgets.update(pygame.event.get())
        
        pygame.display.update()

def game_screen():
    running = True
    dt = 0
    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

    while running:
        pygame.display.set_caption(f"X: {player_pos.x} Y: {player_pos.y}")
        
        # Poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")

        pygame.draw.circle(screen, "red", player_pos, 40)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            player_pos.y -= 300 * dt
        if keys[pygame.K_s]:
            player_pos.y += 300 * dt
        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_d]:
            player_pos.x += 300 * dt
        if keys[pygame.K_ESCAPE]:
            running = False
            title_screen()

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Limits FPS to 60
        dt = clock.tick(60) / 1000

    pygame.quit()

def main():
    from screens.TitleScreen import TitleScreen
    TitleScreen(screen, "Title Screen")

if __name__ == '__main__':
    main()
