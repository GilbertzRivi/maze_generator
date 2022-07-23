import time, os, threading, subprocess
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

    def __init__(self, width: int, height: int, dwidth: int, dheight: int, start: list, animation: bool = True) -> None:
        self.width, self.height, self.cp, self.do_animate, self.sp = width, height, start, animation, start
        self.dwidth, self.dheight, self.start = dwidth, dheight, start
        self.maze = np.zeros((width, height), dtype=np.bool_)
        
        self.maze[start[0], start[1]] = not self.maze[start[0], start[1]]
                
        self.animation = {'start': (start[0], start[1]), 'changes': []}
        
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

            if self.do_animate:
                changes.append({'x': self.cp[0], 'y': self.cp[1], 'changed': changed})

        if self.do_animate:
            self.animation['changes'] = changes

    def create_animation(self, duration: int = 60, fps: int = 60, video_path: str = './maze.mp4', verbose: bool = True) -> None:
        if not self.do_animate:
            print('No animation files has been generated')
            return

        def __generate_images(base, num_frames: int, divisor: int) -> None:

            def __save_image(image: list):
                image[0].save(f'./temp/{image[1]}.png')

            changes = self.animation['changes']
            len_changes = len(self.animation['changes'])
            
            if verbose:
                bar = Bar('Generating Images', max=divisor, suffix = '%(percent).1f%% - eta: %(eta)ds')

            if len_changes < num_frames:
                skip_frames = 1
            else:
                skip_frames = int(len_changes/num_frames)

            generated_frame_counter = 0
            frames = []
            imdraw = ImageDraw.ImageDraw(base)
            for i, step in enumerate(changes):
                imdraw.point(xy=(step['x'], step['y']), fill=(255, 0, 0))
                imdraw.point(xy=(changes[i-1]['x'], changes[i-1]['y']), fill=(255, 255, 255))
                if i == 2:
                    imdraw.point(xy=(self.start[0], self.start[1]), fill=(0, 255, 0))
                if i % skip_frames == 0 or i == len_changes:
                    frames.append([base.copy(), generated_frame_counter])
                    generated_frame_counter += 1
                if generated_frame_counter % 100 == 0:
                    threads = [threading.Thread(target=__save_image, args=[image]) for image in frames]
                    [t.start() for t in threads]
                    [t.join() for t in threads]
                    frames = []
                if i % int(len(changes)/divisor) == 0 and verbose:
                    bar.next()
            
            if verbose:
                bar.finish()

            threads = [threading.Thread(target=__save_image, args=[image]) for image in frames]
            [t.start() for t in threads]
            [t.join() for t in threads]

        def __resize_images(divisor):

            def __save_resize_image(image):
                path = './temp/' + image
                image = Image.open(path)
                image = image.resize((self.dwidth, self.dheight), resample=0)
                os.remove(path)
                image.save(path)

            if verbose:
                bar = Bar('Resizing Images', max=divisor, suffix = '%(percent).1f%% - eta: %(eta)ds')
            images = []
            paths = os.listdir('./temp')
            images_num = len(paths)
            for i, image in enumerate(paths):
                images.append(image)
                if len(images) % 100 == 0:
                    threads = [threading.Thread(target=__save_resize_image, args=[image]) for image in images]
                    [t.start() for t in threads]
                    [t.join() for t in threads]
                    images = []
                if i % int(images_num/divisor) == 0 and verbose:
                    bar.next()
            
            if verbose:
                bar.finish()
                    
            threads = [threading.Thread(target=__save_resize_image, args=[image]) for image in images]
            [t.start() for t in threads]
            [t.join() for t in threads]

        divisor = len(self.animation['changes'])
        if divisor > 200:
            divisor = 200

        num_frames = duration*fps 

        base = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        basedraw = ImageDraw.ImageDraw(base)
        basedraw.point(xy=(self.start[0], self.start[1]), fill=(0, 255, 0))

        if os.path.isdir('./temp'):
            files = os.listdir('./temp')
            if len(files) > 0:
                for file in files:
                    os.remove('./temp/'+file)
        else:
            os.mkdir('./temp')

        __generate_images(base, num_frames, divisor)

        if divisor > len(os.listdir('./temp')):
            divisor = len(os.listdir('./temp')) 
            
        if dwidth != width:
            __resize_images(divisor)
        
        if os.path.exists(video_path):
            os.remove(video_path)
        
        if verbose:
            print('Generating video...')
        subprocess.call([
            'ffmpeg', '-r', str(fps), '-s',
            f'{self.dwidth}x{self.dheight}', '-i',
            './temp/%d.png', '-vcodec', 'libx264',
            '-crf', '25', '-pix_fmt', 'yuv420p', 'maze.mp4'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for file in os.listdir('./temp'):
            os.remove('./temp/'+file)
        os.rmdir('./temp')

    def write_maze(self, path: str = './maze.png') -> None:
        maze_img = Image.new('RGB', size=(self.width, self.height))
        maze_draw = ImageDraw.Draw(maze_img)
        for x in range(self.width):
            for y in range(self.height):
                tile = self.maze[x, y]
                if tile:
                    maze_draw.point(xy=(x, y), fill=(255, 255, 255))
        maze_draw.point(xy=(self.sp[0], self.sp[1]), fill=(255, 0, 0))
        maze_draw.point(xy=(self.width-1, self.height-1), fill=(0, 255, 0))
        maze_img.resize((self.dwidth, self.dheight), resample=0).save(fp=path)

if __name__ == '__main__':
    
    width = int(input('Input maze width: '))
    dwidth = input('Input image width (blank means same as mazes): ')
    start = input('Input the point where maze should start (x/y (def 0/0)): ')
    do_maze_animation = input('Do you want to generate animation? (Y/n): ').lower()

    if start == '':
        sp = [0, 0]
    else:
        sp = [int(start.split('/')[0]), int(start.split('/')[1])]

    if do_maze_animation == 'n':
        do_maze_animation = False
    else:
        do_maze_animation = True
        duration_fps = input('Enter animation duration/fps (default 60/60): ')
        if duration_fps != '':
            duration, fps = int(duration_fps.split('/')[0]), int(duration_fps.split('/')[1])
        else:
            duration, fps = 60, 60
        
    if dwidth == '':
        dwidth = width
    else:
        dwidth = int(dwidth)
    
    if dwidth % 2 != 0:
        dwidth += 1

    print('Initializing maze...')
    maze = Maze(width, width, dwidth, dwidth, sp, do_maze_animation)
    start = time.time()
    print('Generating path...')
    maze.generate_path()
    end = time.time()
    print(f'Generated maze {maze.height}x{maze.width}')
    print(f'it took {round(end-start, 2)}s')
    print('Saving maze...')
    maze.write_maze()
    if do_maze_animation:
        print('Generating animation...')
        maze.create_animation(duration, fps)