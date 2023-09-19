WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (100, 204, 197)
DARKGREEN = (23, 107, 135)
ORANGE = (255, 165, 0)
PURPLE = (237, 200, 255)
YELLOW = (248, 255, 150)
GREY = (200, 200, 200)
DARKGREY = (100, 100, 100)

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def get_clicked_pos(x, y, rows, width):
    gap = width // rows
    row = y // gap
    col = x // gap
    return row, col
