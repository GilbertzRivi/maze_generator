import time, json
import numpy as np
from numba import njit
from PIL import Image, ImageDraw
from progress.bar import Bar

@njit(cache=True)
def check_tile_neighbours(cpx: int, cpy: int, width: int, height: int, maze) -> bool:
    directions_8 = [(1,0), (-1,0), (0,1), (0,-1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    type_p_count = 0
    for dir in directions_8:
        x = cpx + dir[0]
        y = cpy + dir[1]
        if 0 <= x < width and 0 <= y < height and maze[x, y]:
            type_p_count += 1
            if type_p_count > 2:
                return False
    return True

@njit(cache=True)
def check_aviable_directions(cpx: int, cpy: int, width: int, height: int, maze) -> list:
    available_directions = []
    directions_4 = [(1,0), (-1,0), (0,1), (0,-1)]
    for dir in directions_4:
        if  0 <= cpx + dir[0] < width and \
            0 <= cpy + dir[1] < height and \
            not maze[cpx + dir[0], cpy + dir[1]] and \
            check_tile_neighbours(cpx + dir[0], cpy + dir[1], width, height, maze):
            available_directions.append(dir)
    return available_directions

class Maze:

    def __init__(self, width: int, height: int, dwidth: int, dheight: int, start: list) -> None:
        self.width, self.height, self.cp, self.sp = width, height, start, start
        self.dwidth, self.dheight, self.start = dwidth, dheight, start
        self.maze = np.zeros((width, height), dtype=np.bool_)
        self.end = [0, 0]
        
        self.maze[start[0], start[1]] = not self.maze[start[0], start[1]]
                
        self.animation = {'start': (start[0], start[1]), 'size': (width, height), 'changes': []}
        
    def generate_path(self):
                
        prev_dir = None
        dir_couter = 0
        stack = [self.cp]
        changes = []

        while len(stack) != 0: 
            available_directions = check_aviable_directions(self.cp[0], self.cp[1], self.width, self.height, self.maze)
            changed = False

            if len(available_directions) == 0:
                self.cp = stack.pop()
            
            else:
                if prev_dir in available_directions and dir_couter < 1:
                    dir = prev_dir
                    dir_couter += 1
                else:
                    dir = available_directions[int(np.random.random()*(len(available_directions)))]
                    dir_couter = 0
                    
                self.cp = (self.cp[0] + dir[0], self.cp[1] + dir[1])
                prev_dir = dir
                self.maze[self.cp[0], self.cp[1]] = not self.maze[self.cp[0], self.cp[1]]
                changed = True
                stack.append(self.cp)

            changes.append({'x': self.cp[0], 'y': self.cp[1], 'changed': changed})

        self.animation['changes'] = changes

        for y in range(self.height)[::-1]:
            if self.maze[self.width-1, y]:
                self.end = [self.width-1, y]
                break

    def write_maze(self, path: str = './maze.png') -> None:
        maze_img = Image.new('RGB', size=(self.width, self.height))
        maze_draw = ImageDraw.Draw(maze_img)
        for x in range(self.width):
            for y in range(self.height):
                tile = self.maze[x, y]
                if tile:
                    maze_draw.point(xy=(x, y), fill=(255, 255, 255))

        for y in range(self.height)[::-1]:
            if self.maze[self.height-1, y]:
                maze_draw.point(xy=(self.width-1, y), fill=(0, 255, 0))
                break

        maze_draw.point(xy=(self.sp[0], self.sp[1]), fill=(255, 0, 0))
        maze_img.resize((self.dwidth, self.dheight), resample=0).save(fp=path)

    def write_changes(self, path: str = './animation.json') -> None:
        with open(path, 'w') as file:
            file.write(json.dumps(self.animation))

if __name__ == '__main__':
    
    width = int(input('Input maze width: '))
    dwidth = input('Input image width (blank means same as mazes): ')
    start = input('Input the point where maze should start (x/y (def 0/0)): ')

    if start == '':
        sp = [0, 0]
    else:
        sp = [int(start.split('/')[0]), int(start.split('/')[1])]
        
    if width % 2 != 0:
        width += 1

    if dwidth == '':
        dwidth = width
    else:
        dwidth = int(dwidth)

    print('Initializing maze...')
    maze = Maze(width, width, dwidth, dwidth, sp)
    start = time.time()
    print('Generating path...')
    maze.generate_path()
    end = time.time()
    print(f'Generated maze {maze.height}x{maze.width}')
    print(f'it took {round(end-start, 2)}s')
    print('Saving maze...')
    maze.write_maze()
    print('Saving changes...')
    maze.write_changes()