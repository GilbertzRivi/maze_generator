import random, time, json, numba
import numpy as np
from PIL import Image, ImageDraw

class tile:
    def __init__(self, coordinates: tuple, type: str) -> None:
        self.coordinates, self.type = coordinates, type

    def __str__(self) -> str:
        return f"{self.coordinates}, {self.type}"

    def __eq__(self, other: object) -> bool:
        try:
            return self.coordinates == other.coordinates and self.type == other.type
        except AttributeError:
            return False

class Maze:
    
    directions_4 = [(1,0), (-1,0), (0,1), (0,-1)]
    directions_8 = directions_4 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def __init__(self, width: int, height: int, start: tuple, animation: bool = True) -> None:
        self.width, self.height, self.cp, self.do_animate = width-2, height-2, start, animation
        self.maze = np.zeros((width, height), dtype=np.bool_)
        
        self.__change_tile_type()
                
        if self.do_animate:
            self.animation = {'start': None, 'changes': []}
            self.animation['start'] = self.__maze_json()

    def __change_tile_type(self) -> None:
        self.maze[self.cp[0], self.cp[1]] = not self.maze[self.cp[0], self.cp[1]]

    def __check_tile_neighbours(self, cp: tuple) -> list:
        neighbours = []
        for dir in self.directions_8:
            try:
                neighbours.append(self.maze[cp[0] + dir[0], cp[1] + dir[1]])
            except KeyError:
                pass
        return neighbours

    def generate_path(self) -> str:
            
        prev_dir = None
        dir_couter = 0
        stack = [self.cp]
        
        while True:
            available_directions = []
            for dir in self.directions_4:
                if  self.cp[0] + dir[0] in range(self.width) and \
                    self.cp[1] + dir[1] in range(self.height) and \
                    not self.maze[self.cp[0] + dir[0], self.cp[1] + dir[1]] and \
                    [tile for tile in self.__check_tile_neighbours((self.cp[0] + dir[0], self.cp[1] + dir[1]))].count(True) <= 2:
                    available_directions.append(dir)

            changed = False

            if len(stack) == 0:
                break

            if len(available_directions) == 0:
                self.cp = stack.pop()
            
            else:
                if prev_dir in available_directions and dir_couter < 1:
                    dir = prev_dir
                    dir_couter += 1
                else:
                    dir = random.choice(available_directions)
                    dir_couter = 0
                self.cp = (self.cp[0] + dir[0], self.cp[1] + dir[1])
                prev_dir = dir
                self.__change_tile_type()
                changed = True
                stack.append(self.cp)

            if self.do_animate:
                self.animation['changes'].append({'x': self.cp[0], 'y': self.cp[1], 'changed': changed})
        
        return f'Generated path for maze {self.width}x{self.height}'

    def __maze_json(self) -> dict:
        dict = {}
        for x in range(self.width):
            dict[x] = {}
            for y in range(self.height):
                dict[x][y] = bool(self.maze[x, y])
        return dict
        
    def write_animation(self, path: str) -> None:
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
                tile = self.maze[x][y]
                if tile:
                    maze_draw.point(xy=(x+1, y+1), fill=1)

        maze_img.resize((dwidth, dheight), resample=0).save(fp=path)

        return self.maze

if __name__ == '__main__':
    
    width = int(input('maze width/height: '))
    dwidth = input('image width/height (if the same leave blank): ')
    
    if dwidth == '':
        dwidth = width
    else:
        int(dwidth)
        
    start = time.time()
    maze = Maze(width, width, (0, 0), True)
    print(maze.generate_path())
    end = time.time()
    print(f'it took {round(end-start, 2)}s')
    maze.write_maze(dwidth, dwidth, './maze.png')
    maze.write_animation('./changes.json')