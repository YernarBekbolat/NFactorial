import pygame
import pygame_menu
from pygame_menu import themes
import sys
import time
from solver import Cell, Sudoku
import json
import _pickle as pickle


pygame.init()


cell_size = 50
minor_grid_size = 1
major_grid_size = 3
buffer = 5
button_height = 50
button_width = 125
button_border = 2
width = cell_size*9 + minor_grid_size*6 + major_grid_size*4 + buffer*2
height = cell_size*9 + minor_grid_size*6 + \
    major_grid_size*4 + button_height + buffer*3 + button_border*2
size = width, height
white = 255, 255, 255
black = 0, 0, 0
gray = 200, 200, 200
green = 0, 175, 0
red = 200, 0, 0
inactive_btn = 51, 255, 255
active_btn = 51, 153, 255
go = False
nickname = ''
dict = {}
high_dict = {}



res_dif = 0
tot_time = 0

screen = pygame.display.set_mode(size)
pygame.display.set_caption('Sudoku')



class RectCell(pygame.Rect):
    '''
    A class built upon the pygame Rect class used to represent individual cells in the game.
    This class has a few extra attributes not contained within the base Rect class.
    '''

    def __init__(self, left, top, row, col):
        super().__init__(left, top, cell_size, cell_size)
        self.row = row
        self.col = col


dif = 1

def high_score(d):
    max_key = float('-inf')
    min_value = float('inf')
    max_dict = None

    for key, value in d.items():
        max_key = ""
        max_dict = None
        for key, value in d.items():
            for k, v in value.items():
                if not max_dict or max(value.values()) > max_dict[max_dict.keys()[0]]:
                    max_dict = value
                    max_key = key
                elif max(value.values()) == max_dict[max_dict.keys()[0]]:
                    if min(value.values()) < max_dict[max_dict.keys()[0]]:
                        max_dict = value
                        max_key = key
        

    return max_dict

def MyTextValue(name):
    global nickname
    nickname = name

def set_difficulty(value, Difficulty):
    global dif
    dif = Difficulty

def toClock(time_passed):
    minutes = time_passed//60
    seconds = time_passed%60

    curTimer = str(minutes).zfill(2) + ":" + str(seconds).zfill(2)

    return curTimer

def create_cells():
    '''Creates all 81 cells with RectCell class.'''
    cells = [[] for _ in range(9)]

    
    row = 0
    col = 0
    left = buffer + major_grid_size
    top = buffer + major_grid_size

    while row < 9:
        while col < 9:
            cells[row].append(RectCell(left, top, row, col))

           
            left += cell_size + minor_grid_size
            if col != 0 and (col + 1) % 3 == 0:
                left = left + major_grid_size - minor_grid_size
            col += 1

        top += cell_size + minor_grid_size
        if row != 0 and (row + 1) % 3 == 0:
            top = top + major_grid_size - minor_grid_size
        left = buffer + major_grid_size
        col = 0
        row += 1

    return cells
        
def draw_grid():
    
    lines_drawn = 0
    pos = buffer + major_grid_size + cell_size
    while lines_drawn < 6:
        pygame.draw.line(screen, black, (pos, buffer),
                         (pos, width-buffer-1), minor_grid_size)
        pygame.draw.line(screen, black, (buffer, pos),
                         (width-buffer-1, pos), minor_grid_size)

        
        lines_drawn += 1

        pos += cell_size + minor_grid_size
        if lines_drawn % 2 == 0:
            pos += cell_size + major_grid_size

    for pos in range(buffer+major_grid_size//2, width, cell_size*3 + minor_grid_size*2 + major_grid_size):
        pygame.draw.line(screen, black, (pos, buffer),
                         (pos, width-buffer-1), major_grid_size)
        pygame.draw.line(screen, black, (buffer, pos),
                         (width-buffer-1, pos), major_grid_size)


def fill_cells(cells, board):
    '''Fills in all the numbers for the game.'''
    font = pygame.font.Font(None, 36)

    for row in range(9):
        for col in range(9):
            if board.board[row][col].value is None:
                continue

            if not board.board[row][col].editable:
                font.bold = True
                text = font.render(f'{board.board[row][col].value}', 1, black)

            else:
                font.bold = False
                if board.check_move(board.board[row][col], board.board[row][col].value):
                    text = font.render(
                        f'{board.board[row][col].value}', 1, green)
                else:
                    text = font.render(
                        f'{board.board[row][col].value}', 1, red)

            xpos, ypos = cells[row][col].center
            textbox = text.get_rect(center=(xpos, ypos))
            screen.blit(text, textbox)


def draw_button(left, top, width, height, border, color, border_color, text):
    
    pygame.draw.rect(
        screen,
        border_color,
        (left, top, width+border*2, height+border*2),
    )

    button = pygame.Rect(
        left+border,
        top+border,
        width,
        height
    )
    pygame.draw.rect(screen, color, button)

    font = pygame.font.Font(None, 26)
    text = font.render(text, 1, black)
    xpos, ypos = button.center
    textbox = text.get_rect(center=(xpos, ypos))
    screen.blit(text, textbox)

    return button


def draw_board(active_cell, cells, game):
    '''Draws all elements making up the board.'''
    
    draw_grid()
    if active_cell is not None:
        pygame.draw.rect(screen, gray, active_cell)

    fill_cells(cells, game)


def visual_solve(game, cells):
    
    cell = game.get_empty_cell()
    if not cell:
        return True

    for val in range(1, 10):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        cell.value = val

        screen.fill(white)
        draw_board(None, cells, game)
        cell_rect = cells[cell.row][cell.col]
        pygame.draw.rect(screen, red, cell_rect, 5)
        pygame.display.update([cell_rect])
        time.sleep(0.05)

        if not game.check_move(cell, val):
            cell.value = None
            continue

        screen.fill(white)
        pygame.draw.rect(screen, green, cell_rect, 5)
        draw_board(None, cells, game)
        pygame.display.update([cell_rect])
        if visual_solve(game, cells):
            return True

        cell.value = None

    screen.fill(white)
    pygame.draw.rect(screen, white, cell_rect, 5)
    draw_board(None, cells, game)
    pygame.display.update([cell_rect])
    return False


def check_sudoku(sudoku):
    if sudoku.get_empty_cell():
        raise ValueError('Game is not complete')

    row_sets = [set() for _ in range(9)]
    col_sets = [set() for _ in range(9)]
    box_sets = [set() for _ in range(9)]

    for row in range(9):
        for col in range(9):
            box = (row // 3) * 3 + col // 3
            value = sudoku.board[row][col].value

            if value in row_sets[row] or value in col_sets[col] or value in box_sets[box]:
                return False

            row_sets[row].add(value)
            col_sets[col].add(value)
            box_sets[box].add(value)

    return True

def level_menu():
    mainmenu._open(level)

def high_score_menu():
    mainmenu._open(highscore)


def play():


    '''Contains all the functionality for playing a game of Sudoku.'''
    easy = [
        [6, 2, 0, 0, 3, 9, 7, 8, 4],
        [7, 8, 0, 4, 6, 5, 2, 0, 1],
        [3, 0, 4, 7, 0, 2, 0, 0, 9],
        [0, 0, 7, 9, 0, 1, 8, 4, 6],
        [4, 9, 0, 0, 7, 6, 3, 1, 5],
        [1, 5, 6, 0, 0, 8, 9, 0, 0],
        [0, 7, 3, 8, 0, 0, 0, 6, 2],
        [9, 4, 0, 6, 1, 0, 5, 7, 0],
        [8, 6, 1, 5, 2, 0, 0, 9, 3]
    ]

    middle = [
        [6, 7, 0, 4, 5, 0, 0, 9, 1],
        [9, 0, 4, 1, 3, 7, 5, 0, 0],
        [0, 3, 5, 9, 0, 0, 0, 0, 4],
        [7, 1, 0, 0, 0, 8, 2, 5, 0],
        [8, 4, 0, 2, 7, 5, 0, 6, 0],
        [2, 0, 6, 0, 0, 1, 0, 0, 8],
        [0, 6, 0, 0, 1, 0, 9, 3, 2],
        [4, 9, 0, 5, 0, 3, 0, 0, 0],
        [0, 0, 1, 7, 2, 0, 6, 4, 5]
    ]

    hard = [
        [0, 0, 3, 0, 2, 9, 0, 5, 1],
        [0, 0, 7, 0, 0, 0, 4, 9, 0],
        [9, 2, 5, 4, 1, 0, 0, 0, 0],
        [7, 3, 0, 5, 0, 0, 0, 0, 9],
        [1, 5, 0, 0, 0, 8, 0, 0, 0],
        [0, 0, 0, 9, 3, 0, 8, 7, 5],
        [3, 0, 1, 0, 0, 4, 0, 8, 0],
        [0, 8, 0, 1, 0, 0, 2, 4, 0],
        [0, 0, 4, 7, 8, 6, 0, 0, 0]
    ]

    if dif == 1:
        game = Sudoku(easy)
    if dif == 2:
        game = Sudoku(middle)
    if dif == 3:
        game = Sudoku(hard)

    

    
    cells = create_cells()
    active_cell = None
    solve_rect = pygame.Rect(
        buffer,
        height-button_height - button_border*2 - buffer,
        button_width + button_border*2,
        button_height + button_border*2
    )
        
    start_time = pygame.time.get_ticks()
    font = pygame.font.SysFont("Verdana", 36)
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

    timer_surface = font.render(toClock(elapsed_time), True, (0, 0, 0))
    timer_rect = timer_surface.get_rect(center=(70, 500))
    time_cnt = True

    

    while True:
        go = True
        font = pygame.font.SysFont("Verdana", 36)
        if time_cnt:
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
            timer_surface = font.render(toClock(elapsed_time), True, (0, 0, 0))
            timer_rect = timer_surface.get_rect(center=(70, 500))

        score_surface = font.render(high_score(dict), True, (0, 0, 0))
        score_rect = timer_surface.get_rect(center=(70, 500))

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()

                if reset_btn.collidepoint(mouse_pos):
                    time_cnt = True
                    game.reset()

                if solve_btn.collidepoint(mouse_pos):
                    screen.fill(white)
                    active_cell = None
                    draw_board(active_cell, cells, game)
                    reset_btn = draw_button(
                        width - buffer - button_border*2 - button_width,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        black,
                        'Reset'
                    )
                    solve_btn = draw_button(
                        width - buffer*2 - button_border*4 - button_width*2,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        black,
                        'Solve'
                    )
                    pygame.display.flip()
                    visual_solve(game, cells)

                active_cell = None
                for row in cells:
                    for cell in row:
                        if cell.collidepoint(mouse_pos):
                            active_cell = cell

                if active_cell and not game.board[active_cell.row][active_cell.col].editable:
                    active_cell = None

            if event.type == pygame.KEYUP:
                if active_cell is not None:

                    if event.key == pygame.K_0 or event.key == pygame.K_KP0:
                        game.board[active_cell.row][active_cell.col].value = 0
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        game.board[active_cell.row][active_cell.col].value = 1
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        game.board[active_cell.row][active_cell.col].value = 2
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        game.board[active_cell.row][active_cell.col].value = 3
                    if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        game.board[active_cell.row][active_cell.col].value = 4
                    if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        game.board[active_cell.row][active_cell.col].value = 5
                    if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        game.board[active_cell.row][active_cell.col].value = 6
                    if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        game.board[active_cell.row][active_cell.col].value = 7
                    if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        game.board[active_cell.row][active_cell.col].value = 8
                    if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        game.board[active_cell.row][active_cell.col].value = 9
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        game.board[active_cell.row][active_cell.col].value = None

        screen.fill(white)

        draw_board(active_cell, cells, game)

        reset_btn = draw_button(
            width - buffer - button_border*2 - button_width,
            height - button_height - button_border*2 - buffer,
            button_width,
            button_height,
            button_border,
            inactive_btn,
            black,
            'Reset'
        )
        solve_btn = draw_button(
            width - buffer*2 - button_border*4 - button_width*2,
            height - button_height - button_border*2 - buffer,
            button_width,
            button_height,
            button_border,
            inactive_btn,
            black,
            'Solve'
        )

        if reset_btn.collidepoint(pygame.mouse.get_pos()):
            reset_btn = draw_button(
                width - buffer - button_border*2 - button_width,
                height - button_height - button_border*2 - buffer,
                button_width,
                button_height,
                button_border,
                active_btn,
                black,
                'Reset'
            )
        if solve_btn.collidepoint(pygame.mouse.get_pos()):
            solve_btn = draw_button(
                width - buffer*2 - button_border*4 - button_width*2,
                height - button_height - button_border*2 - buffer,
                button_width,
                button_height,
                button_border,
                active_btn,
                black,
                'Solve'
            )

        if not game.get_empty_cell():
            if check_sudoku(game):
                go = False
                font = pygame.font.Font(None, 36)
                text = font.render('Solved!', 1, green)
                time_cnt = False
                if time_cnt != True:
                    tot_time = elapsed_time
                dict[nickname] = {dif: tot_time}
                high_dict = dict
                textbox = text.get_rect(center=(solve_rect.center))
                screen.blit(text, textbox)
                break

        

        
        if go:
            screen.blit(timer_surface, timer_rect)
        screen.blit(score_surface, score_rect)
        pygame.display.flip()


    

    

    


if __name__ == '__main__':
    
    mainmenu = pygame_menu.Menu('Sudoku', 478, 537, theme=themes.THEME_SOLARIZED)
   
    mainmenu.add.text_input('Name: ', default='', maxchar=20, onchange=MyTextValue)
    mainmenu.add.button('Play', play)
    mainmenu.add.button('Difficulty', level_menu)
    mainmenu.add.button('High Score', high_score_menu)
    mainmenu.add.button('Quit', pygame_menu.events.EXIT)

    highscore = pygame_menu.Menu('High score is ' + str(high_score(high_dict)), 478, 537, theme=themes.THEME_BLUE)
    level = pygame_menu.Menu('Select a Difficulty', 478, 537, theme=themes.THEME_BLUE)
    level.add.selector('Difficulty :', [('Easy', 1), ('Middle', 2), ('Hard', 3)], onchange=set_difficulty)
    
    mainmenu.mainloop(screen)
    