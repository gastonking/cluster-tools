#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import random
import select
import termios
import tty
import shutil

# Dimensiones del tablero
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Formas de las piezas (Tetrominós)
SHAPES = [
    [[[1, 1, 1, 1]], [[1], [1], [1], [1]]], # I
    [[[1, 1], [1, 1]]], # O
    [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]], [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]], # T
    [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]], # S
    [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]], # Z
    [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]], [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]], # J
    [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]], [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]]  # L
]

# Códigos de colores ANSI (Bloques sólidos)
COLORS = [
    "\033[48;5;0m   \033[0m",       # Vacío / Fondo negro
    "\033[48;5;51m   \033[0m",      # I - Cyan
    "\033[48;5;226m   \033[0m",     # O - Amarillo
    "\033[48;5;135m   \033[0m",     # T - Morado
    "\033[48;5;46m   \033[0m",      # S - Verde
    "\033[48;5;196m   \033[0m",     # Z - Rojo
    "\033[48;5;21m   \033[0m",      # J - Azul
    "\033[48;5;208m   \033[0m",     # L - Naranja
    "\033[48;5;240m   \033[0m"      # Borde / Sombra gris
]

# Caracteres Unicode para bordes (se ven mejor que │)
BORDER_H = '─'
BORDER_V = '│'
CORNER_TL = '┌'
CORNER_TR = '┐'
CORNER_BL = '└'
CORNER_BR = '┘'

class TetrisGame:
    def __init__(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.spawn_piece()

    def spawn_piece(self):
        self.current_shape_idx = random.randint(0, len(SHAPES) - 1)
        self.current_rotation = 0
        self.current_color = self.current_shape_idx + 1
        shape = SHAPES[self.current_shape_idx][self.current_rotation]
        self.piece_x = BOARD_WIDTH // 2 - len(shape[0]) // 2
        self.piece_y = 0
        if not self.check_collision(self.piece_x, self.piece_y, shape):
            self.game_over = True

    def check_collision(self, px, py, shape):
        for r_idx, row in enumerate(shape):
            for c_idx, cell in enumerate(row):
                if cell:
                    nx = px + c_idx
                    ny = py + r_idx
                    if nx < 0 or nx >= BOARD_WIDTH or ny >= BOARD_HEIGHT: return False
                    if ny >= 0 and self.board[ny][nx] != 0: return False
        return True

    def merge_piece(self):
        shape = SHAPES[self.current_shape_idx][self.current_rotation]
        for r_idx, row in enumerate(shape):
            for c_idx, cell in enumerate(row):
                if cell:
                    nx, ny = self.piece_x + c_idx, self.piece_y + r_idx
                    if 0 <= ny < BOARD_HEIGHT and 0 <= nx < BOARD_WIDTH:
                        self.board[ny][nx] = self.current_color
        self.clear_lines()
        self.spawn_piece()

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        cleared = BOARD_HEIGHT - len(new_board)
        if cleared > 0:
            self.lines_cleared += cleared
            self.score += [0, 40, 100, 300, 1200][cleared] * self.level
            self.level = 1 + self.lines_cleared // 10
            for _ in range(cleared): new_board.insert(0, [0] * BOARD_WIDTH)
            self.board = new_board

    def move_side(self, dx):
        shape = SHAPES[self.current_shape_idx][self.current_rotation]
        if self.check_collision(self.piece_x + dx, self.piece_y, shape): self.piece_x += dx

    def move_down(self):
        shape = SHAPES[self.current_shape_idx][self.current_rotation]
        if self.check_collision(self.piece_x, self.piece_y + 1, shape):
            self.piece_y += 1
            return True
        else:
            self.merge_piece()
            return False

    def drop_fast(self):
        while self.move_down(): pass

    def rotate(self):
        rotations = SHAPES[self.current_shape_idx]
        new_rot = (self.current_rotation + 1) % len(rotations)
        if self.check_collision(self.piece_x, self.piece_y, rotations[new_rot]):
            self.current_rotation = new_rot

def get_char():
    if select.select([sys.stdin], [], [], 0)[0]: return sys.stdin.read(1)
    return None

def draw_centered(stdscr, output_list):
    """Dibuja el contenido centrado en la terminal."""
    term_size = shutil.get_terminal_size((80, 24))
    term_h = term_size.lines
    term_w = term_size.columns
    
    output_str = "".join(output_list)
    lines = output_str.split('\n')
    
    # Limpiar toda la pantalla por completo
    sys.stdout.write('\033[2J\033[3J') 
    
    current_row = max(0, (term_h // 2) - (len(lines) // 2))
    for line in lines:
        if current_row < term_h:
            # Centrar horizontalmente
            padding = max(0, (term_w // 2) - (len(line.encode('utf-8')) // 2)) # Codificar para contar ancho real
            # Corrección de ancho de caracteres unicode
            actual_len = len(line)
            display_len = len(line.replace(BORDER_V,' ').replace(BORDER_H,' ').replace(CORNER_BL,' ').replace(CORNER_BR,' ').replace(CORNER_TL,' ').replace(CORNER_TR,' '))
            display_len = (len(line) - display_len) + display_len # Ajuste burdo para unicode
            
            # Mas sencillo, calcular el padding solo para el texto normal y rellenar
            sys.stdout.write(f"\033[{current_row};{max(0, term_w // 2 - 15)}H{line}") # Centrado aprox del tablero ancho 24+2
            current_row += 1
    sys.stdout.flush()

def main():
    if not sys.stdin.isatty():
        print("Error: Este script debe ejecutarse en una terminal interactiva.")
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    # Ocultar cursor
    sys.stdout.write("\033[?25l")
    time.sleep(0.1) # Pequeña pausa para asegurar que la terminal se limpia

    game = TetrisGame()
    fall_time = time.time()
    fall_speed = 0.5

    try:
        while not game.game_over:
            current_speed = max(0.08, fall_speed - (game.level - 1) * 0.04)
            ch = get_char()
            if ch == '\x1b':
                seq = sys.stdin.read(2)
                if seq == '[A': game.rotate()
                elif seq == '[B': game.move_down()
                elif seq == '[C': game.move_side(1)
                elif seq == '[D': game.move_side(-1)
            elif ch == ' ': game.drop_fast()
            elif ch in ('q', 'Q'): break
            elif ch in ('p', 'P'): game.paused = not game.paused
            
            if not game.paused and time.time() - fall_time > current_speed:
                game.move_down()
                fall_time = time.time()

            # Renderizado de pantalla
            output = []
            output.append("\033[1;36m================ TĒTRIS SHELL ================\033[0m\n")
            
            display_board = [row[:] for row in game.board]
            if not game.paused:
                shape = SHAPES[game.current_shape_idx][game.current_rotation]
                for r_idx, row in enumerate(shape):
                    for c_idx, cell in enumerate(row):
                        if cell:
                            ny, nx = game.piece_y + r_idx, game.piece_x + c_idx
                            if 0 <= ny < BOARD_HEIGHT and 0 <= nx < BOARD_WIDTH:
                                display_board[ny][nx] = game.current_color

            # Borde superior
            output.append(f"\033[38;5;240m{CORNER_TL}{BORDER_H * (BOARD_WIDTH * 3)}{CORNER_TR}\033[0m\n")

            # Tablero principal con bordes y bloques
            for row in display_board:
                line = f"\033[38;5;240m{BORDER_V}\033[0m"
                for cell in row:
                    line += COLORS[cell]
                line += f"\033[38;5;240m{BORDER_V}\033[0m"
                output.append(line + "\n")
            
            # Borde inferior
            output.append(f"\033[38;5;240m{CORNER_BL}{BORDER_H * (BOARD_WIDTH * 3)}{CORNER_BR}\033[0m\n")
            output.append(f"\033[1;33m Puntuación: {game.score:<6} | Nivel: {game.level:<2} | Líneas: {game.lines_cleared:<3}\033[0m\n")
            output.append("\033[32m [←][→] Mover  [↑] Rotar  [↓] Bajar  [Espacio] Caída  [q] Salir\033[0m\n")

            # Dibujar todo centrado
            draw_centered(main, output) # Pasa main como referencia para el calculo, pero usa output

            time.sleep(0.02)

        # Game Over
        sys.stdout.write("\033[2J\033[H")
        print("\n\n\033[1;31m   ¡GAME OVER! \033[0m")
        print(f"\033[1;33m   Puntuación final: {game.score}\033[0m\n\n")
        sys.stdout.flush()

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

if __name__ == "__main__":
    main()