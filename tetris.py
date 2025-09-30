"""
Simple Tetris implementation using pygame.
Run: python tetris.py

Controls:
- Left/Right arrows: move
- Up arrow / X: rotate
- Down arrow / Down: soft drop
- Space: hard drop
- P: pause
- Esc / Q: quit

This is a compact single-file implementation suitable for learning and playing.
"""

import sys
import random
import pygame

# Game constants
CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLUMNS
HEIGHT = CELL_SIZE * ROWS
FPS = 60

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # I - cyan
    (0, 0, 255),    # J - blue
    (255, 165, 0),  # L - orange
    (255, 255, 0),  # O - yellow
    (0, 255, 0),    # S - green
    (128, 0, 128),  # T - purple
    (255, 0, 0),    # Z - red
]

# Tetrimino shapes: lists of 4x4 matrices (rotations)
SHAPES = {
    'I': [
        [[0,0,0,0],
         [1,1,1,1],
         [0,0,0,0],
         [0,0,0,0]],
        [[0,0,1,0],
         [0,0,1,0],
         [0,0,1,0],
         [0,0,1,0]],
    ],
    'J': [
        [[1,0,0],
         [1,1,1],
         [0,0,0]],
        [[0,1,1],
         [0,1,0],
         [0,1,0]],
        [[0,0,0],
         [1,1,1],
         [0,0,1]],
        [[0,1,0],
         [0,1,0],
         [1,1,0]],
    ],
    'L': [
        [[0,0,1],
         [1,1,1],
         [0,0,0]],
        [[0,1,0],
         [0,1,0],
         [0,1,1]],
        [[0,0,0],
         [1,1,1],
         [1,0,0]],
        [[1,1,0],
         [0,1,0],
         [0,1,0]],
    ],
    'O': [
        [[1,1],
         [1,1]],
    ],
    'S': [
        [[0,1,1],
         [1,1,0],
         [0,0,0]],
        [[0,1,0],
         [0,1,1],
         [0,0,1]],
    ],
    'T': [
        [[0,1,0],
         [1,1,1],
         [0,0,0]],
        [[0,1,0],
         [0,1,1],
         [0,1,0]],
        [[0,0,0],
         [1,1,1],
         [0,1,0]],
        [[0,1,0],
         [1,1,0],
         [0,1,0]],
    ],
    'Z': [
        [[1,1,0],
         [0,1,1],
         [0,0,0]],
        [[0,0,1],
         [0,1,1],
         [0,1,0]],
    ],
}

SHAPE_KEYS = list(SHAPES.keys())

class Piece:
    def __init__(self, shape_key):
        self.shape_key = shape_key
        self.rotations = SHAPES[shape_key]
        self.rotation = 0
        self.shape = self.rotations[self.rotation]
        # Starting position (top-middle)
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.color = COLORS[SHAPE_KEYS.index(shape_key)]

    def rotate(self, grid):
        old_rot = self.rotation
        self.rotation = (self.rotation + 1) % len(self.rotations)
        self.shape = self.rotations[self.rotation]
        if not valid_position(self, grid, self.x, self.y):
            # try wall kicks (simple)
            for dx in (-1, 1, -2, 2):
                if valid_position(self, grid, self.x + dx, self.y):
                    self.x += dx
                    return True
            # revert
            self.rotation = old_rot
            self.shape = self.rotations[self.rotation]
            return False
        return True

    def get_cells(self):
        cells = []
        for r, row in enumerate(self.shape):
            for c, val in enumerate(row):
                if val:
                    cells.append((self.x + c, self.y + r))
        return cells


def create_grid():
    return [[None for _ in range(COLUMNS)] for _ in range(ROWS)]


def valid_position(piece, grid, x, y):
    for r, row in enumerate(piece.shape):
        for c, val in enumerate(row):
            if not val:
                continue
            gx = x + c
            gy = y + r
            if gx < 0 or gx >= COLUMNS or gy < 0 or gy >= ROWS:
                return False
            if grid[gy][gx] is not None:
                return False
    return True


def lock_piece(piece, grid):
    for x, y in piece.get_cells():
        if 0 <= y < ROWS and 0 <= x < COLUMNS:
            grid[y][x] = piece.color


def clear_lines(grid):
    new_grid = [row for row in grid if any(cell is None for cell in row)]
    cleared = ROWS - len(new_grid)
    while len(new_grid) < ROWS:
        new_grid.insert(0, [None for _ in range(COLUMNS)])
    return new_grid, cleared


def draw_grid(surface, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if cell is None:
                pygame.draw.rect(surface, BLACK, rect)
                pygame.draw.rect(surface, GRAY, rect, 1)
            else:
                pygame.draw.rect(surface, cell, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)


def draw_piece(surface, piece):
    for x, y in piece.get_cells():
        if y >= 0:
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, piece.color, rect)
            pygame.draw.rect(surface, WHITE, rect, 1)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    grid = create_grid()

    current = Piece(random.choice(SHAPE_KEYS))
    next_piece = Piece(random.choice(SHAPE_KEYS))
    fall_time = 0
    fall_speed = 0.5  # seconds per cell
    score = 0
    level = 1
    lines = 0
    running = True
    paused = False

    move_left = move_right = rotate = False
    soft_drop = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        fall_time += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_LEFT:
                    move_left = True
                elif event.key == pygame.K_RIGHT:
                    move_right = True
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    rotate = True
                elif event.key == pygame.K_DOWN:
                    soft_drop = True
                elif event.key == pygame.K_SPACE:
                    # hard drop
                    while valid_position(current, grid, current.x, current.y + 1):
                        current.y += 1
                    lock_piece(current, grid)
                    grid, cleared = clear_lines(grid)
                    if cleared:
                        score += cleared * 100
                        lines += cleared
                    current = next_piece
                    next_piece = Piece(random.choice(SHAPE_KEYS))
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    move_left = False
                elif event.key == pygame.K_RIGHT:
                    move_right = False
                elif event.key == pygame.K_DOWN:
                    soft_drop = False
                elif event.key == pygame.K_UP or event.key == pygame.K_x:
                    rotate = False

        if paused:
            continue

        # handle lateral moves
        if move_left:
            if valid_position(current, grid, current.x - 1, current.y):
                current.x -= 1
            move_left = False
        if move_right:
            if valid_position(current, grid, current.x + 1, current.y):
                current.x += 1
            move_right = False
        if rotate:
            current.rotate(grid)
            rotate = False

        # fall handling
        speed = fall_speed / (1 + (level - 1) * 0.1)
        if soft_drop:
            speed = max(0.02, speed / 5)

        if fall_time >= speed:
            fall_time = 0
            if valid_position(current, grid, current.x, current.y + 1):
                current.y += 1
            else:
                # lock
                lock_piece(current, grid)
                grid, cleared = clear_lines(grid)
                if cleared:
                    score += cleared * 100
                    lines += cleared
                    level = 1 + lines // 10
                current = next_piece
                next_piece = Piece(random.choice(SHAPE_KEYS))
                if not valid_position(current, grid, current.x, current.y):
                    print('Game Over! Score:', score)
                    running = False

        # draw
        draw_grid(screen, grid)
        draw_piece(screen, current)

        # HUD
        font = pygame.font.SysFont('Consolas', 20)
        txt = font.render(f'Score: {score}  Lines: {lines}  Level: {level}', True, WHITE)
        screen.blit(txt, (5, 5))

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
