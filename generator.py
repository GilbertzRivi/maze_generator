import time, json
import numpy as np
from numba import njit
from PIL import Image, ImageDraw

@njit(cache=True)
def check_tile_neighbours(coordinates: tuple, width, height, maze) -> bool:
    directions_8 = [(1,0), (-1,0), (0,1), (0,-1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    type_p_count = 0
    for dir in directions_8:
        x = coordinates[0] + dir[0]
        y = coordinates[1] + dir[1]
        if 0 <= x < width and 0 <= y < height and maze[x, y]:
            type_p_count += 1
            if type_p_count > 2:
                return False
    return True

@njit(cache=True)
def check_aviable_directions(cp, width, height, maze):
    available_directions = []
    directions_4 = [(1,0), (-1,0), (0,1), (0,-1)]
    for dir in directions_4:
        if  0 <= cp[0] + dir[0] < width and \
            0 <= cp[1] + dir[1] < height and \
            not maze[cp[0] + dir[0], cp[1] + dir[1]] and \
            check_tile_neighbours((cp[0] + dir[0], cp[1] + dir[1]), width, height, maze):
            available_directions.append(dir)
    return available_directions

class Maze:

    def __init__(self, width: int, height: int, start: tuple, animation: bool = True) -> None:
        self.width, self.height, self.cp, self.do_animate = width-2, height-2, start, animation
        self.maze = np.zeros((width, height), dtype=np.bool_)
        
        self.maze[self.cp[0], self.cp[1]] = not self.maze[self.cp[0], self.cp[1]]
                
        self.animation = {'start': (width, height), 'changes': []}
        
    def generate_path(self):
                
        prev_dir = None
        dir_couter = 0
        stack = [self.cp]
        changes = []

        while len(stack) != 0: 
            available_directions = check_aviable_directions(self.cp, self.width, self.height, self.maze)
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

            if self.do_animate:
                changes.append({'x': self.cp[0], 'y': self.cp[1], 'changed': changed})

        if self.do_animate:
            self.animation['changes'] = changes

    def write_animation(self, path: str = './changes.json') -> None:
        if not self.do_animate:
            print('No animation has been generated')
        else:
            with open(path, 'w') as file:
                file.write(json.dumps(self.animation))

    def write_maze(self, dwidth: int = None, dheight: int = None, path: str = './maze.png') -> None:
        if dwidth is None:
            dwidth = self.width+2
        if dheight is None:
            dheight = self.height+2
        maze_img = Image.new('1', size=(self.width+2, self.height+2))
        maze_draw = ImageDraw.Draw(maze_img)
        maze_draw.point(xy=(0, 1), fill=1)
        maze_draw.point(xy=(self.width+1, self.height), fill=1)
        for x in range(self.width):
            for y in range(self.height):
                tile = self.maze[x, y]
                if tile:
                    maze_draw.point(xy=(x+1, y+1), fill=1)
        maze_img.resize((dwidth, dheight), resample=0).save(fp=path)

if __name__ == '__main__':
    
    width = int(input('Input maze width/height: ')) + 2
    dwidth = input('Input image width/height (blank means same as above): ')
    do_maze_animation = input('Do you want animations files? (Y/n): ').lower()

    if do_maze_animation == 'n':
        do_maze_animation = False
    else:
        do_maze_animation = True

    if dwidth == '':
        dwidth = width
    else:
        dwidth = int(dwidth)
    
    start = time.time()
    print('Initializing maze...')
    maze = Maze(width, width, (0, 0), do_maze_animation)
    print('Generating path...')
    maze.generate_path()
    end = time.time()
    print(f'Generated maze {maze.height}x{maze.width}')
    print(f'it took {round(end-start, 2)}s')
    print('Saving files...')
    maze.write_maze(dwidth, dwidth)
    maze.write_animation()