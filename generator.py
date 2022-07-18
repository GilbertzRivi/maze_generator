from asyncore import write
import random, time, json
from PIL import Image, ImageDraw

class v2d:
    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y
    
    def __str__(self) -> str:
        return f"{self.x}x {self.y}y"

    def __add__(self, other) -> object:
        return v2d(self.x + other.x, self.y + other.y)

    def copy(self) -> object:
        return f"{self.x}x {self.y}y"

    def __add__(self, other) -> object:
        return v2d(self.x + other.x, self.y + other.y)

    def copy(self) -> object:
        return v2d(self.x, self.y)

    def __eq__(self, other: object) -> bool:
        try:
            return self.x == other.x and self.y == other.y
        except AttributeError:
            return False

class tile:
    def __init__(self, coordinates: v2d, type: str) -> None:
        self.coordinates, self.type = coordinates, type

    def __str__(self) -> str:
        return f"{self.coordinates}, {self.type}"

    def __eq__(self, other: object) -> bool:
        try:
            return self.coordinates == other.coordinates and self.type == other.type
        except AttributeError:
            return False

class Maze:
    def __init__(self, width: int, height: int, start: v2d, animation: bool = True) -> None:
        self.width, self.height, self.cp, self.do_animate = width-2, height-2, start, animation
        self.maze = {}
        self.directions = {'r': v2d(1,0),'l': v2d(-1,0),'u': v2d(0,1),'d': v2d(0,-1)}

        for x in range(self.width):
            self.maze[x] = {}
            for y in range(self.height):
                self.maze[x][y] = tile(v2d(x, y), 'w')
        
        self.__change_tile_type('p')
        
        if self.do_animate:
            self.animation = {'start': None, 'changes': []}
            self.animation['start'] = self.__maze_json()
            
    def __change_tile_type(self, type: str) -> None:
        tile = self.maze[self.cp.x][self.cp.y]
        tile.type = type

    def __check_tile_neighbours(self, coordinates: v2d) -> list:
        neighbours = []
        directions = [v2d(1,0), v2d(-1,0), v2d(0,1), v2d(0,-1), v2d(1, 1), v2d(1, -1), v2d(-1, 1), v2d(-1, -1)]
        for dir in directions:
            try:
                neighbours.append(self.maze[coordinates.x + dir.x][coordinates.y + dir.y])
            except KeyError:
                pass
        return neighbours

    def __maze_json(self) -> dict:
        dict = {}
        for x in self.maze:
            dict[x] = {}
            for y in self.maze[x]:
                tile = self.maze[x][y]
                dict[x][y] = tile.type
        return dict

    def generate_path(self) -> str:
            
        prev_dir = None
        dir_couter = 0
        stack = [self.cp.copy()]
        
        while True:
            available_directions = []
            for dir in self.directions.values():
                if  self.cp.x + dir.x in range(self.width) and \
                    self.cp.y + dir.y in range(self.height) and \
                    self.maze[self.cp.x + dir.x][self.cp.y + dir.y].type == 'w' and \
                    [tile.type for tile in self.__check_tile_neighbours(self.cp + dir)].count('p') <= 2:
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
                self.cp += dir
                prev_dir = dir
                self.__change_tile_type('p')
                changed = True
                stack.append(self.cp.copy())

            self.animation['changes'].append({'x': self.cp.x, 'y': self.cp.y, 'changed': changed})
        
        return f'Generated path for maze {self.width}x{self.height}'

    def write_animation(self, path: str) -> None:
        if not self.animation:
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
        for x in self.maze:
            for y in self.maze[x]:
                tile = self.maze[x][y]
                if tile.type == 'p':
                    maze_draw.point(xy=(tile.coordinates.x+1, tile.coordinates.y+1), fill=1)

        maze_img.resize((dwidth, dheight), resample=0).save(fp=path)

        return self.maze

if __name__ == '__main__':
    
    width = int(input('maze width/height: '))
    dwidth = int(input('image width/height: '))
    start = time.time()
    maze = Maze(width, width, v2d(0, 0), True)
    print(maze.generate_path())
    maze.write_maze(dwidth, dwidth, './maze.png')
    maze.write_animation('./changes.json')
    end = time.time()
    print(f'it took {round(end-start, 2)}s')