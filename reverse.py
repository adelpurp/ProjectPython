# https://github.com/adelpurp/ProjectPython.git

import random, sys, pygame, time, copy
from pygame.locals import *

FPS = 60                    # кадров в секунду обновления экрана
WINDOWWIDTH = 1024          # ширина окна программы в пикселях
WINDOWHEIGHT = 768          # высота в пикселях
SPACESIZE = 85              # ширина и высота каждого поля на доске, в пикселях
BOARDWIDTH = 8              # сколько столбцов на игровом поле
BOARDHEIGHT = 8             # сколько строк на игровом поле
WHITE_TILE = 'WHITE_TILE'
BLACK_TILE = 'BLACK_TILE'
EMPTY_SPACE = 'EMPTY_SPACE'
HINT_TILE = 'HINT_TILE'
ANIMATIONSPEED = 100        # целое число от 1 до 100, чем выше значение, тем выше скорость анимации

# Количество места слева и справа (XMARGIN) или выше и ниже
# (YMARGIN) игровое поле, в пикселях.
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * SPACESIZE)) / 6)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * SPACESIZE)) / 2)

#         R    G    B
WHITE = (255, 255, 255)
MilkPunch = (255, 246, 212)
BlueShadeOfBlack = (0, 9, 43)
BLACK = (0, 0, 0)
BROWN = (174, 94, 0)
LightGoldenrod2 = (238, 220, 130)

TEXTBGCOLOR1 = LightGoldenrod2
TEXTBGCOLOR2 = LightGoldenrod2
GRIDLINECOLOR = BLACK           # цвет сетки
TEXTCOLOR = BLACK
HINTCOLOR = BROWN               # цвет подсказки

pygame.init()
MAINCLOCK = pygame.time.Clock()
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Реверси')
FONT = pygame.font.Font('freesansbold.ttf', 34)
BIGFONT = pygame.font.Font('freesansbold.ttf', 48)

# Настройка фонового изображения.
boardImage = pygame.image.load('board.jpg')
# Использую smoothscale(), чтобы растянуть изображение доски, чтобы оно поместилась на всю доску:
boardImage = pygame.transform.smoothscale(boardImage, (BOARDWIDTH * SPACESIZE, BOARDHEIGHT * SPACESIZE))
boardImageRect = boardImage.get_rect()
boardImageRect.topleft = (XMARGIN, YMARGIN)
BGIMAGE = pygame.image.load('br.jpg')
# Использую smoothscale(), чтобы растянуть изображение фона, чтобы оно поместилась на всё окно:
BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWIDTH, WINDOWHEIGHT))
BGIMAGE.blit(boardImage, boardImageRect)


def translateBoardToPixelCoord(x, y):   # перевод доски в пиксельную координату
    return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)


def drawBoard(board):
    # Рисовка фона доски.
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    # Рисовка линий сетки на доске.
    for x in range(BOARDWIDTH + 1):
        # Рисовка горизонтальных линий.
        startx = (x * SPACESIZE) + XMARGIN
        starty = YMARGIN
        endx = (x * SPACESIZE) + XMARGIN
        endy = YMARGIN + (BOARDHEIGHT * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))
    for y in range(BOARDHEIGHT + 1):
        # Рисовка вертикальных линий.
        startx = XMARGIN
        starty = (y * SPACESIZE) + YMARGIN
        endx = XMARGIN + (BOARDWIDTH * SPACESIZE)
        endy = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startx, starty), (endx, endy))

    # Рисовка чёрных и белых кругов или подсказок.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tileColor = MilkPunch
                else:
                    tileColor = BLACK
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(SPACESIZE / 3) - 6)
            if board[x][y] == HINT_TILE:
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (centerx - 4, centery - 4, 8, 8))


def getNewBoard():
    # Настройка доски (без всего).
    board = []
    for i in range(BOARDWIDTH):
        board.append([EMPTY_SPACE] * BOARDHEIGHT)

    return board


def resetBoard(board):
    # Если доска пройдена полностью, то она очищается.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            board[x][y] = EMPTY_SPACE

    # Начальная расстановка игровых фишек
    board[3][3] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    board[4][4] = WHITE_TILE

