import pygame
import math
from queue import PriorityQueue
from utils import *

pygame.init()

WIDTH = 600
OFFSET = 125
WIN = pygame.display.set_mode((WIDTH, WIDTH+OFFSET))
pygame.display.set_caption("path visualizer")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TEAL = (100, 204, 197)
DARKGREEN = (23, 107, 135)
ORANGE = (255, 165, 0)
PURPLE = (237, 200, 255)
YELLOW = (248, 255, 150)
GREY = (200, 200, 200)
DARKGREY = (100, 100, 100)

class Grid:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        
    def get_pos(self):
        return self.row, self.col
    
    def is_closed(self):
        return self.color == TEAL
    
    def is_barrier(self):
        return self.color == BLACK
    
    def is_open(self):
        return self.color == DARKGREEN
    
    def is_end(self):
        return self.color == PURPLE
    
    def is_start(self):
        return self.color == ORANGE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = TEAL

    def make_open(self):
        self.color = DARKGREEN
    
    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = PURPLE

    def make_path(self):
        if self.color != ORANGE and self.color != PURPLE:
            self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.y, self.x+OFFSET, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def make_grid(rows, width):
    grids = []
    gap = width // rows
    for i in range(rows):
        grids.append([])
        for j in range(rows):
            grid = Grid(i, j, gap, rows)
            grids[i].append(grid)
    return grids

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, OFFSET+i*gap), (width, OFFSET+i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, OFFSET), (j*gap, width+OFFSET))

def draw(win, grids, rows, width):
    win.fill(WHITE)

    for row in grids:
        for grid in row:
            grid.draw(win)
    
    draw_grid(win, rows, width)

    font1 = pygame.font.SysFont("calibri", 32)
    text1 = font1.render('pathfinding visualizer', True, PURPLE)
    textRect1 = text1.get_rect()
    textRect1.center = (WIDTH // 2, OFFSET // 2 - 15)
    font2 = pygame.font.SysFont("calibri", 15)
    text2 = font2.render("space = start A*, q = start Dijkstra\'s", True, DARKGREY)
    textRect2 = text2.get_rect()
    textRect2.topleft = (5, OFFSET-40)
    font3 = pygame.font.SysFont("calibri", 15)
    text3 = font3.render("j = undo result, esc = reset, shift = remove barrier", True, DARKGREY)
    textRect3 = text3.get_rect()
    textRect3.topleft = (5, OFFSET-20)
    WIN.blit(text1, textRect1)
    WIN.blit(text2, textRect2)
    WIN.blit(text3, textRect3)
    
    pygame.display.update()

#########      algorithm A*         #########

def astar_algo(draw, grid, start, end):
    count = 0  # 'count' tells insertion order for open_set
    open_set = PriorityQueue()
    open_set.put((0, count, start))  # f_score, count, node
    came_from = {}

    # formula of f_score
    # f_score = g_score + h( )

    g_score = {}
    f_score = {}
    for row in grid:
        for spot in row:
            # init all to infinity
            g_score[spot] = float("inf")
            f_score[spot] = float("inf")
    g_score[start] = 0
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start} # help tell us what is in open_set

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2] # fetch the one with least f_score
        open_set_hash.remove(current)

        if current == end:
            while current in came_from:
                current = came_from[current]
                current.make_path()
                draw()
            return True
        
        # find shortest path to reach each node
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos()) 

                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor] ,count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor.color != PURPLE: neighbor.make_open()
        draw()

        # mark those considered already as closed
        if current != start:
            current.make_closed()

###########          Dijkstra's         ############

def dijkstra(draw, grid, start, end):
    visited = set()
    unvisited = PriorityQueue()
    distance = {}
    came_from = {}  # for storing path
    unvisited.put((0, start))  # min distance from start, node
    for row in grid:
        for spot in row:
            distance[spot] = float("inf")
            came_from[spot] = None
    
    distance[start] = 0

    while not unvisited.empty():
        current = unvisited.get()
        visited.add(current[1])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if current[1] == end:
            current = current[1]
            while current in came_from and came_from[current]:
                current = came_from[current]
                current.make_path()
                draw()
            return True
        
        for neighbor in current[1].neighbors:
            if neighbor not in visited:
                temp_distance = current[0] + 1
                if temp_distance < distance[neighbor]:
                    distance[neighbor] = temp_distance
                    came_from[neighbor] = current[1]
                    unvisited.put((temp_distance, neighbor))
                    if neighbor.color != PURPLE: neighbor.make_open()
        
        draw()
        
        if current[1] != start:
            current[1].make_closed()
    


####  start main function  ####

def main(win, width):
    ROWS = 40
    grids = make_grid(ROWS, WIDTH)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grids, ROWS, WIDTH)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue
            
            # press shift, remove barrier
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
                pos = pygame.mouse.get_pos()
                if pos[1] < OFFSET: continue
                row, col = get_clicked_pos(pos[0], pos[1]-OFFSET, ROWS, width)
                spot = grids[row][col]
                if spot.is_barrier(): spot.reset()

            # left click, placing barriers
            if pygame.mouse.get_pressed()[0]:  
                pos = pygame.mouse.get_pos()
                if pos[1] < OFFSET: continue
                row, col = get_clicked_pos(pos[0], pos[1]-OFFSET, ROWS, width)
                print(row, col)
                spot = grids[row][col]
                
                if spot.color == WHITE: spot.make_barrier()
            ## right click, choosing start / end
            elif pygame.mouse.get_pressed()[2]: 
                pos = pygame.mouse.get_pos()
                if pos[1] < OFFSET: continue
                row, col = get_clicked_pos(pos[0], pos[1]-OFFSET, ROWS, width)
                spot = grids[row][col]
                if not start:
                    # cant put start at the chosen end
                    if spot.is_end(): continue
                    start = spot
                    spot.make_start()
                elif not end:
                    # cant put end at the chosen start
                    if spot.is_start(): continue  
                    end = spot
                    spot.make_end()
                elif start or end:
                    if spot.is_start(): 
                        spot.reset()
                        start = None
                    elif spot.is_end():
                        spot.reset()
                        end = None
            
            # start the program with A* algorithm
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and start and end: 
                    for row in grids:
                        for spot in row:
                            spot.update_neighbors(grids)

                    astar_algo(lambda: draw(win, grids, ROWS, width), grids, start, end)

            # start the program with Dijkstra's algorithm        
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q and start and end:
                    for row in grids:
                        for spot in row:
                            spot.update_neighbors(grids)       

                    dijkstra(lambda: draw(win, grids, ROWS, width), grids, start, end)

            # reset the whole map
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    start = None
                    end = None
                    grids = make_grid(ROWS, width)
            
            # reset the result
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_j:
                    for row in grids:
                        for spot in row:
                            if not spot.is_start() and not spot.is_end() and not spot.is_barrier(): spot.reset()
    pygame.quit()

main(WIN, WIDTH)