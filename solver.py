import time, json
import numpy as np
from numba import njit
from PIL import Image, ImageDraw

def printmaze(cp: list, width: int, height: int, maze) -> None:
    for x in range(width):
        line = ''
        for y in range(height):
            if cp == [x, y]:
                line += '##'
            elif maze[x, y]:
                line += 'oo'
            else: 
                line += '--'
        print(line)

if __name__ == '__main__':
    maze_fp = input('Input path to maze (default ./maze.png): ')
    if maze_fp == '':
        maze_fp = './maze.png'

    maze_png = Image.open(maze_fp)
    maze_size = input('Input resolution of the maze, not image (defalut is image width/height): ')
    width, height = maze_png.size[0], maze_png.size[1]
    org_width, org_height = width, height
    if maze_size != '':
        width, height = int(maze_size.split('/')[0]), int(maze_size.split('/')[1])
        maze_png = maze_png.resize((width, height), resample=0)

    maze_list = np.zeros((width, height), dtype=np.bool_)
    for x in range(height):
        for y in range(width):
            if maze_png.getpixel((x, y)) == (255, 255, 255):
                maze_list[x, y] = True
            elif maze_png.getpixel((x, y)) == (255, 0, 0):
                cp = [x, y]
                maze_list[x, y] = True
            elif maze_png.getpixel((x, y)) == (0, 255, 0):
                end = [x, y]
                maze_list[x, y] = True
                
    history = [cp]
    moves = []
    path = [cp]
    while cp != end:

        directions_4 = [[1,0], [-1,0], [0,1], [0,-1]]
        available_directions = []
        for dir in directions_4:
            x = cp[0] + dir[0]
            y = cp[1] + dir[1]
            if  0 <= x < width and \
                0 <= y < height and \
                maze_list[x, y]:
                available_directions.append(dir)
        
        if len(available_directions) == 0:
            cp = history.pop()
            moves.pop()
        elif len(available_directions) == 1:
            dir = available_directions[0]
        elif len(available_directions) == 2:
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

    solved = Image.new('RGB', (width, height))
    solved_draw = ImageDraw.Draw(solved)

    for x in range(width):
        for y in range(height):
            if maze_list[x, y]:
                solved_draw.point((x, y), (255, 255, 255))

    gradient_step = 255 * 2 / len(path)
    gradient = [255, 0, 0]
    gradient_int = gradient
    for tile in path:
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

    if org_height != height or org_width != width:
        solved = solved.resize((org_width, org_height), resample=0)
    solved.save('./solved.png')