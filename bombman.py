import pygame
import sys
import random
from pygame.locals import *


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 40
PLAYER_SIZE = 30
BOMB_RADIUS = 4
MOVE_DELAY = 250  
BOMB_TIMER = 1200  
EXPLOSION_TIME = 500  


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)


def create_maze():
    maze = []
    for x in range(1, SCREEN_WIDTH // GRID_SIZE, 2):
        for y in range(1, SCREEN_HEIGHT // GRID_SIZE, 2):
            maze.append((x * GRID_SIZE, y * GRID_SIZE))
    return maze

def draw_maze(screen, maze):
    for wall in maze:
        pygame.draw.rect(screen, WHITE, (wall[0], wall[1], GRID_SIZE, GRID_SIZE))

def get_random_position(maze):
    while True:
        x = random.randint(0, SCREEN_WIDTH // GRID_SIZE - 1) * GRID_SIZE
        y = random.randint(0, SCREEN_HEIGHT // GRID_SIZE - 1) * GRID_SIZE
        if (x, y) not in maze:
            return x, y

class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.color = color
        self.controls = controls
        self.last_move = 0  
        self.lives = 3  
    
    def move(self, keys, maze):
        now = pygame.time.get_ticks()
        if now - self.last_move < MOVE_DELAY:
            return
        dx, dy = 0, 0
        if keys[self.controls['up']]:
            dy = -GRID_SIZE
        elif keys[self.controls['down']]:
            dy = GRID_SIZE
        elif keys[self.controls['left']]:
            dx = -GRID_SIZE
        elif keys[self.controls['right']]:
            dx = GRID_SIZE
        
        new_pos = (self.x + dx, self.y + dy)
        if new_pos not in maze and 0 <= new_pos[0] < SCREEN_WIDTH and 0 <= new_pos[1] < SCREEN_HEIGHT:
            self.x += dx
            self.y += dy
            self.last_move = now
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x + 5, self.y + 5, PLAYER_SIZE, PLAYER_SIZE))
    
    def take_damage(self, maze):
        self.lives -= 1
        if self.lives > 0:
            self.x, self.y = get_random_position(maze)


class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.time_planted = pygame.time.get_ticks()
        self.exploded = False
    
    def draw(self, screen):
        pygame.draw.circle(screen, RED, (self.x + GRID_SIZE // 2, self.y + GRID_SIZE // 2), GRID_SIZE // 2)
    
    def explode(self, maze):
        explosion_positions = [(self.x, self.y)]
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            for i in range(1, BOMB_RADIUS + 1):
                pos = (self.x + i * dx * GRID_SIZE, self.y + i * dy * GRID_SIZE)
                if pos in maze:
                    break  
                explosion_positions.append(pos)
        return explosion_positions


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bomberman")
    clock = pygame.time.Clock()
    

    maze = create_maze()
    

    player1 = Player(0, 0, BLUE, {'up': K_w, 'down': K_s, 'left': K_a, 'right': K_d, 'bomb': K_f})
    player2 = Player(SCREEN_WIDTH - GRID_SIZE, SCREEN_HEIGHT - GRID_SIZE, GREEN, {'up': K_UP, 'down': K_DOWN, 'left': K_LEFT, 'right': K_RIGHT, 'bomb': K_l})
    

    bombs = []
    explosions = []

    while True:
        screen.fill(BLACK)
        draw_maze(screen, maze)
        
        keys = pygame.key.get_pressed()
        player1.move(keys, maze)
        player2.move(keys, maze)
        
        player1.draw(screen)
        player2.draw(screen)


        current_time = pygame.time.get_ticks()
        new_explosions = []
        for bomb in bombs[:]:
            if not bomb.exploded and current_time - bomb.time_planted >= BOMB_TIMER:
                bomb.exploded = True
                new_explosions.extend(bomb.explode(maze))
                bombs.remove(bomb)
            elif not bomb.exploded:
                bomb.draw(screen)


        for pos in explosions:
            pygame.draw.rect(screen, YELLOW, (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
        explosions = [pos for pos in explosions if current_time - bomb.time_planted < BOMB_TIMER + EXPLOSION_TIME]
        explosions.extend(new_explosions)

        
        for pos in explosions:
            if (player1.x, player1.y) == pos:
                player1.take_damage(maze)
            if (player2.x, player2.y) == pos:
                player2.take_damage(maze)

        
        if player1.lives <= 0:
            print("Gracz 2 wygrał!")
            pygame.quit()
            sys.exit()
        elif player2.lives <= 0:
            print("Gracz 1 wygrał!")
            pygame.quit()
            sys.exit()

        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == player1.controls['bomb']:
                    bombs.append(Bomb(player1.x, player1.y))
                elif event.key == player2.controls['bomb']:
                    bombs.append(Bomb(player2.x, player2.y))

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
