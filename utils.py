def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def get_clicked_pos(x, y, rows, width):
    gap = width // rows
    row = y // gap
    col = x // gap
    return row, col