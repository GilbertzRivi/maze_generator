import time
import numpy as np
from numba import njit
from PIL import Image, ImageDraw

@njit(cache=True)
def check_available_directions(cpx: int, cpy: int, maze_width: int, maze_height: int, maze_list) -> list:
    directions_4 = [[1,0], [-1,0], [0,1], [0,-1]]
    available_directions = []
    for dir in directions_4:
        x = cpx + dir[0]
        y = cpy + dir[1]
        if  0 <= x < maze_width and \
            0 <= y < maze_height and \
            maze_list[x, y]:
            available_directions.append(dir)
    return available_directions

class Solver:
    def __init__(self, maze_path: str, maze_res: list) -> None:
        self.maze_width, self.maze_height = maze_res[0], maze_res[1]
        self.maze_path = maze_path
        self.maze_png = Image.open(maze_path)
        self.org_width, self.org_height = self.maze_png.size[0], self.maze_png.size[1]
        if self.maze_width is None: self.maze_width = self.org_width
        if self.maze_height is None: self.maze_height = self.org_height
        if self.maze_height == self.org_height and self.maze_width == self.org_width:
            self.maze_png = self.maze_png.resize((self.maze_width, self.maze_height), resample=0)

        self.cp = [0, 0]
        self.end = [0, 0]
        self.path = []

    def load_maze(self) -> None:
        self.maze_list = np.zeros((self.maze_width, self.maze_height), dtype=np.bool_)
        for x in range(self.maze_height):
            for y in range(self.maze_width):
                if self.maze_png.getpixel((x, y)) == (255, 255, 255):
                    self.maze_list[x, y] = True
                elif self.maze_png.getpixel((x, y)) == (255, 0, 0):
                    self.cp = [x, y]
                    self.maze_list[x, y] = True
                elif self.maze_png.getpixel((x, y)) == (0, 255, 0):
                    self.end = [x, y]
                    self.maze_list[x, y] = True

    def solve(self) -> None:

        cp = self.cp
        end = self.end
        maze_width = self.maze_width
        maze_height = self.maze_height
        maze_list = self.maze_list
        history = [cp]
        moves = []
        path = [cp]

        while cp != end:
            available_directions = check_available_directions(cp[0], cp[1], maze_width, maze_height, maze_list)
            len_av_dir = len(available_directions)
            if len_av_dir == 0:
                cp = history.pop()
                moves.pop()
            elif len_av_dir == 1:
                dir = available_directions[0]
            elif len_av_dir == 2:
                for dir in available_directions:
                    if cp[0] + dir[0] != history[-2][0] or cp[1] + dir[1] != history[-2][1]:
                        break
            else:
                move = moves.pop()
                dir = [-move[1], move[0]]
                if dir not in available_directions:
                    dir = move
            cp = [cp[0] + dir[0], cp[1] + dir[1]]
            history.append(cp)
            moves.append(dir)
            if cp in path:
                path.pop()
            else:
                path.append(cp)
        
        self.path = path

    def draw_solution(self, solved_path: str = './solved.png') -> None:
        solved = Image.new('RGB', (self.maze_width, self.maze_height))
        solved_draw = ImageDraw.Draw(solved)

        for x in range(self.maze_width):
            for y in range(self.maze_height):
                if self.maze_list[x, y]:
                    solved_draw.point((x, y), (255, 255, 255))

        gradient_step = 255 * 2 / len(self.path)
        gradient = [255, 0, 0]
        gradient_int = gradient
        for tile in self.path:
            if gradient[0] > 0 and gradient[2] == 0:
                gradient[0] -= gradient_step
                gradient[1] += gradient_step
            elif gradient[1] > 0 and gradient[0] == 0:
                gradient[1] -= gradient_step
                gradient[2] += gradient_step
            for i in [0, 1, 2]:
                if gradient[i] < 0:
                    gradient[i] = 0
                elif gradient[i] > 255:
                    gradient[i] = 255
            gradient_int = (int(gradient[0]), int(gradient[2]), int(gradient[1]))
            solved_draw.point((tile[0], tile[1]), fill=gradient_int)

        if self.org_height != height or self.org_width != width:
            solved = solved.resize((self.org_width, self.org_height), resample=0)
        solved.save(solved_path)

if __name__ == '__main__':
    maze_fp = input('Input path to maze (default ./maze.png): ')
    if maze_fp == '':
        maze_fp = './maze.png'

    maze_size = input('Input resolution of the maze, not image (defalut is image width/height): ')
    width, height = None, None
    if maze_size != '':
        width, height = int(maze_size.split('/')[0]), int(maze_size.split('/')[1])

    solver = Solver(maze_fp, [width, height])
    solver.load_maze()
    start = time.perf_counter()
    solver.solve()
    end = time.perf_counter()
    print(f'Solved maze {solver.maze_width}x{solver.maze_height} in {round(end-start, 2)}s')
    solver.draw_solution()