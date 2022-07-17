from asyncore import write
import random, time, json
from PIL import Image, ImageDraw

class v2d:
    def __init__(self, x: int, y: int) -> object:
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
    def __init__(self, coordinates: v2d, type: str) -> object:
        self.coordinates, self.type = coordinates, type

    def __str__(self) -> str:
        return f"{self.coordinates}, {self.type}"

    def __eq__(self, other: object) -> bool:
        try:
            return self.coordinates == other.coordinates and self.type == other.type
        except AttributeError:
            return False

def change_tile_type(maze: dict, coordinates: v2d, type: str) -> None:
    tile = maze[coordinates.x][coordinates.y]
    tile.type = 'p'

def print_maze(maze: dict) -> None:
    for row in reversed(range(len(maze))):
        for col in range(len(maze[row])):
            tile = maze[row][col] 
            if tile.type == 'p':
                print('#', end='')
            else:
                print('-', end='')
        print('\n')
    print('$'*10)

def check_tile_neighbours(maze: dict, coordinates: v2d) -> list:
    neighbours = []
    directions = [v2d(1,0), v2d(-1,0), v2d(0,1), v2d(0,-1), v2d(1, 1), v2d(1, -1), v2d(-1, 1), v2d(-1, -1)]
    for dir in directions:
        try:
            neighbours.append(maze[coordinates.x + dir.x][coordinates.y + dir.y])
        except KeyError:
            pass
    return neighbours

def maze_jsonize(maze: dict) -> dict:
    dict = {}
    for x in maze:
        dict[x] = {}
        for y in maze[x]:
            tile = maze[x][y]
            dict[x][y] = tile.type
    return dict

def maze_init(width: int, height: int) -> dict:
    maze = {}

    for x in range(width):
        maze[x] = {}
        for y in range(height):
            maze[x][y] = tile(v2d(x, y), 'w')
    
    return maze

def generate_maze(maze: dict, width: int, height: int, animation: dict, cp: v2d):
        
    prev_dir = None
    dir_couter = 0
    directions = {'r': v2d(1,0),'l': v2d(-1,0),'u': v2d(0,1),'d': v2d(0,-1)}
    stack = [cp.copy()]
    
    while True:
        available_directions = []
        for dir in directions.values():
            if  cp.x + dir.x in range(width) and \
                cp.y + dir.y in range(height) and \
                maze[cp.x + dir.x][cp.y + dir.y].type == 'w' and \
                [tile.type for tile in check_tile_neighbours(maze, cp + dir)].count('p') <= 2:
                available_directions.append(dir)

        changed = False

        if len(stack) == 0:
            break

        if len(available_directions) == 0:
            cp = stack.pop()
        
        else:
            if prev_dir in available_directions and dir_couter < 1:
                dir = prev_dir
                dir_couter += 1
            else:
                dir = random.choice(available_directions)
                dir_couter = 0
            cp += dir
            prev_dir = dir
            change_tile_type(maze, cp, 'p')
            changed = True
            stack.append(cp.copy())

        animation['changes'].append({'x': cp.x, 'y': cp.y, 'changed': changed})
    
    return maze, animation

def write_animation(animation: dict) -> None:
    with open('changes.json', 'w') as file:
        file.write(json.dumps(animation))

def write_maze(width: int, height: int, dwith: int, dheight: int, maze: dict):
    maze_img = Image.new('1', size=(width+2, height+2))
    maze_draw = ImageDraw.Draw(maze_img)
    maze_draw.point(xy=(0, 1), fill=1)
    maze_draw.point(xy=(width+1, height), fill=1)
    for x in maze:
        for y in maze[x]:
            tile = maze[x][y]
            if tile.type == 'p':
                maze_draw.point(xy=(tile.coordinates.x+1, tile.coordinates.y+1), fill=1)

    maze_img.resize((dwidth, dheight), resample=0).save(fp='./maze.png')

def start(width: int, dwidth: int):
    
    height = width
    dheight = dwidth
    start = time.time()
    
    maze = maze_init(width, height)
    cp = v2d(0, 0)
    change_tile_type(maze, cp, 'p')
    
    animation = {'start': None, 'changes': []}
    animation['start'] = maze_jsonize(maze)
    maze, animation = generate_maze(maze, width, height, animation, cp)
    end = time.time()
    print(f'Generated maze {width}x{height} in {round(end-start, 2)}s')
    write_animation(animation)
    write_maze(width, height, dwidth, dheight, maze)

if __name__ == '__main__':
    
    width = int(input('maze width/height: '))
    dwidth = int(input('image width/height: '))
    start(width, dwidth)