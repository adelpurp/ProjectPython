import random, sys, pygame, time, copy
from pygame.locals import *

FPS = 60  # кадров в секунду обновления экрана
WINDOWWIDTH = 1024  # ширина окна программы в пикселях
WINDOWHEIGHT = 768  # высота в пикселях
SPACESIZE = 85  # ширина и высота каждого поля на доске, в пикселях
BOARDWIDTH = 8  # сколько столбцов на игровом поле
BOARDHEIGHT = 8  # сколько строк на игровом поле
WHITE_TILE = 'WHITE_TILE'
BLACK_TILE = 'BLACK_TILE'
EMPTY_SPACE = 'EMPTY_SPACE'
HINT_TILE = 'HINT_TILE'
ANIMATIONSPEED = 100  # целое число от 1 до 100, чем выше значение, тем выше скорость анимации

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
GRIDLINECOLOR = BLACK  # цвет сетки
TEXTCOLOR = BLACK
HINTCOLOR = BROWN  # цвет подсказки

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


def translateBoardToPixelCoord(x, y):  # перевод доски в пиксельную координату
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


def enterPlayerTile():
    # Рисует текст и обрабатывает события щелчка мыши, позволяя игроку выбрать нужный цвет.
    # Возвращает [WHITE_TILE, BLACK_TILE], если игрок выбирает быть белым, [BLACK_TILE, WHITE_TILE], если черный.

    # Создание текста.
    textSurf = FONT.render('Какой фишкой предпочтёте играть?', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWIDTH / 2) - 110, int(WINDOWHEIGHT / 3))

    xSurf = BIGFONT.render('Белой', True, TEXTCOLOR, TEXTBGCOLOR1)
    xRect = xSurf.get_rect()
    xRect.center = (int(WINDOWWIDTH / 2) - 325, int(WINDOWHEIGHT / 2) - 40)

    oSurf = BIGFONT.render('Чёрной', True, TEXTCOLOR, TEXTBGCOLOR1)
    oRect = oSurf.get_rect()
    oRect.center = (int(WINDOWWIDTH / 2) + 100, int(WINDOWHEIGHT / 2) - 40)

    while True:
        # Продолжайте цикл до тех пор, пока игрок не нажмет на цвет.
        checkForQuit()
        for event in pygame.event.get():  # цикл обработки событий
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint((mousex, mousey)):
                    return [WHITE_TILE, BLACK_TILE]
                elif oRect.collidepoint((mousex, mousey)):
                    return [BLACK_TILE, WHITE_TILE]

        # Рисовка экрана.
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)


def drawInfo(board, playerTile, computerTile, turn):
    # Рисует очки и чья очередь в нижней части экрана.
    scores = getScoreOfBoard(board)
    scoreSurf = FONT.render("Очки игрока: ", True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomright = (WINDOWWIDTH - 50, WINDOWHEIGHT - 425)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    scoreSurf = FONT.render("%s" % (str(scores[playerTile])), True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomright = (WINDOWWIDTH - 15, WINDOWHEIGHT - 425)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    scoreSurf = FONT.render("Очки ", True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomright = (WINDOWWIDTH - 185, WINDOWHEIGHT - 350)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    scoreSurf = FONT.render("компьютера: ", True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomright = (WINDOWWIDTH - 50, WINDOWHEIGHT - 320)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    scoreSurf = FONT.render("%s" % (str(scores[computerTile])), True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomright = (WINDOWWIDTH - 15, WINDOWHEIGHT - 320)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    scoreSurf = FONT.render("Ход ", True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomright = (WINDOWWIDTH - 197, WINDOWHEIGHT - 250)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    scoreSurf = FONT.render("%s" % (turn.title()), True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomright = (WINDOWWIDTH - 63, WINDOWHEIGHT - 220)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def getScoreOfBoard(board):
    # Определение счета, считая фишки.
    xscore = 0
    oscore = 0
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == WHITE_TILE:
                xscore += 1
            if board[x][y] == BLACK_TILE:
                oscore += 1
    return {WHITE_TILE: xscore, BLACK_TILE: oscore}


def checkForQuit():
    for event in pygame.event.get((QUIT, KEYUP)):  # цикл обработки событий
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()




def isOnBoard(x, y):    # вставить
    # Возвращает True, если координаты находятся на доске.
    return x >= 0 and x < BOARDWIDTH and y >= 0 and y < BOARDHEIGHT


def isValidMove(board, tile, xstart, ystart):
    # Возвращает False, если ход игрока недействителен.
    # Если это верный ход, возвращает список пробелов захваченных фигур.
    if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):
        return False

    board[xstart][ystart] = tile  # временно устанавливает плитку на доску.

    if tile == WHITE_TILE:
        otherTile = BLACK_TILE
    else:
        otherTile = WHITE_TILE

    tilesToFlip = []
    # проверить каждое из восьми направлений:
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:
            # Эта фигура принадлежит другому игроку рядом с нашей фигурой.
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break  # вырваться из цикла while, и дальше в цикл for
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:
                # Есть фишки, которые нужно перевернуть. Идиёт в обратном направлении, пока не достигнет
                # исходного пространства, переворачивая все фишки по пути
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x, y])

    board[xstart][ystart] = EMPTY_SPACE  # делает пространство пустым
    if len(tilesToFlip) == 0:  # Если ни одна фишка не перевернута, этот ход недействителен
        return False
    return tilesToFlip


def getValidMoves(board, tile):
    # Возвращает список (x, y) кортежей всех допустимых ходов.
    validMoves = []

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append((x, y))
    return validMoves


def getBoardWithValidMoves(board, tile):
    # Возвращает новую доску с маркировкой подсказки.
    dupeBoard = copy.deepcopy(board)

    for x, y in getValidMoves(dupeBoard, tile):
        dupeBoard[x][y] = HINT_TILE
    return dupeBoard


def getSpaceClicked(mousex, mousey):
    # Возвращает кортеж из двух целых чисел координат пространства доски, где была нажата мышь.
    # (Или возвращает None, если было нажатие не на своё поле.)
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if mousex > x * SPACESIZE + XMARGIN and \
                    mousex < (x + 1) * SPACESIZE + XMARGIN and \
                    mousey > y * SPACESIZE + YMARGIN and \
                    mousey < (y + 1) * SPACESIZE + YMARGIN:
                return (x, y)
    return None


def animateTileChange(tilesToFlip, tileColor, additionalTile):
    # Рисовать кружок туда, куда нажали. (Иначе придётся перерисовывать всю доску.)
    if tileColor == WHITE_TILE:
        additionalTileColor = MilkPunch
    else:
        additionalTileColor = BLACK
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 3) - 6)
    pygame.display.update()

    for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2.55)):
        if rgbValues > 255:
            rgbValues = 255
        elif rgbValues < 0:
            rgbValues = 0

        if tileColor == WHITE_TILE:
            color = tuple([rgbValues] * 3)  # rgb значения идут от 0 к 255
        elif tileColor == BLACK_TILE:
            color = tuple([255 - rgbValues] * 3)  # rgb значения идут от 255 к 0

        for x, y in tilesToFlip:
            centerx, centery = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(SPACESIZE / 3) - 6)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        checkForQuit()


def makeMove(board, tile, xstart, ystart, realMove=False):
    # Помещает фишку на доску в xstart, ystart
    # Переворот фишки (tilesToFlip) возвращает False, если это недопустимый ход, True, если он действителен.
    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    if realMove:
        animateTileChange(tilesToFlip, tile, (xstart, ystart))

    for x, y in tilesToFlip:
        board[x][y] = tile
    return True


def isOnCorner(x, y):
    # Возвращать True, если позиция в одном из четырёх углов.
    return (x == 0 and y == 0) or \
           (x == BOARDWIDTH and y == 0) or \
           (x == 0 and y == BOARDHEIGHT) or \
           (x == BOARDWIDTH and y == BOARDHEIGHT)


def getComputerMove(board, computerTile):
    # Учитывая доску и фишку компьютера, определяет, куда двигаться, и возвращает этот ход в виде списка [x, y].
    possibleMoves = getValidMoves(board, computerTile)

    # рандомизирует порядок возможных ходов
    random.shuffle(possibleMoves)

    # если есть возможность, всегда иди в угол.
    for x, y in possibleMoves:
        if isOnCorner(x, y):
            return [x, y]

    # Пройти через все возможные ходы и запомнить лучший.
    bestScore = -1
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    return bestMove


def runGame():
    # Играет одну игру реверси каждый раз, когда эта функция вызывается.

    # Reset the board and game.
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    showHints = False
    turn = random.choice(['компьютера', 'игрока'])

    # Рисовка стартовой доски и выбор игроком цвета фишки.
    drawBoard(mainBoard)
    playerTile, computerTile = enterPlayerTile()

    # Создание объектов Surface и Rect для кнопок «Новая игра» и «Подсказки»
    newGameSurf = FONT.render('Новая игра', True, TEXTCOLOR, TEXTBGCOLOR2)
    newGameRect = newGameSurf.get_rect()
    newGameRect.topright = (WINDOWWIDTH - 20, 50)
    hintsSurf = FONT.render('Подсказки', True, TEXTCOLOR, TEXTBGCOLOR2)  # подсказки
    hintsRect = hintsSurf.get_rect()
    hintsRect.topright = (WINDOWWIDTH - 20, 140)

    while True:  # основной игровой цикл
        # Продолжает зацикливаться на ходы игрока и компьютера.
        if turn == 'игрока':
            # Ход игрока:
            if getValidMoves(mainBoard, playerTile) == []:
                break  # Если ход игрока, но он не может двигаться, то игра заканчивается
            movexy = None
            while movexy == None:
                # Продолжает зацикливание, пока игрок не нажмет на допустимое место.

                # Определить какое поле показать.
                if showHints:
                    boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
                else:
                    boardToDraw = mainBoard

                checkForQuit()
                for event in pygame.event.get():  # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        # Обработка события щелчка мыши
                        mousex, mousey = event.pos
                        if newGameRect.collidepoint((mousex, mousey)):
                            # Начать новую игру
                            return True
                        elif hintsRect.collidepoint((mousex, mousey)):
                            # Переключить режим подсказок
                            showHints = not showHints
                        # movexy - это кортеж из двух элементов - XY координат  или значение None
                        movexy = getSpaceClicked(mousex, mousey)
                        if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
                            movexy = None

                # Рисовка игрового поля.
                drawBoard(boardToDraw)
                drawInfo(boardToDraw, playerTile, computerTile, turn)

                # Рисовка кнопок «Новая игра» и «Подсказки».
                DISPLAYSURF.blit(newGameSurf, newGameRect)
                DISPLAYSURF.blit(hintsSurf, hintsRect)

                MAINCLOCK.tick(FPS)
                pygame.display.update()

            # Сделать ход и закончить черёд.
            makeMove(mainBoard, playerTile, movexy[0], movexy[1], True)
            if getValidMoves(mainBoard, computerTile) != []:
                # Настраивается только на ход компьютера, если он может сделать ход.
                turn = 'компьютера'
        # --------------------------------------------------------------------------
        else:
            # Ход компьютера:
            if getValidMoves(mainBoard, computerTile) == []:
                # Если настала очередь компьютера, но он не может двигаться, то игра завершается.
                break

            # Рисовка доски.
            drawBoard(mainBoard)
            drawInfo(mainBoard, playerTile, computerTile, turn)

            # Рисовка кнопок "Новая Игра" и "Подсказки".
            DISPLAYSURF.blit(newGameSurf, newGameRect)
            DISPLAYSURF.blit(hintsSurf, hintsRect)

            # Чтобы выглядело так, будто компьютер компьютер думает, сделаю небольшую паузу.
            pauseUntil = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pauseUntil:
                pygame.display.update()

            # Делает ход и заканчивает черёд.
            x, y = getComputerMove(mainBoard, computerTile)
            makeMove(mainBoard, computerTile, x, y, True)
            if getValidMoves(mainBoard, playerTile) != []:
                # Устанавливается только на ход игрока, если он может сделать ход.
                turn = 'игрока'



if __name__ == '__main__':
    # Запускает игру.
    while True:
        if runGame() == False:
            break
