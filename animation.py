from PIL import Image, ImageDraw
from progress.bar import IncrementalBar as Bar
import json, os, threading, subprocess

def create_animation(dsize: tuple = (None, None), animation_path: str = 'animation.json', duration: int = 60, fps: int = 60, video_path: str = './maze.mp4', verbose: bool = True) -> None:

    def __generate_images(base, num_frames: int, divisor: int) -> None:

        def __save_image(image: list):
            image[0].save(f'./temp/{image[1]}.png')

        len_changes = len(changes)
        
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
                imdraw.point(xy=(start[0], start[1]), fill=(0, 255, 0))
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
            image = image.resize((dwidth, dheight), resample=0)
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

    if not os.path.exists(animation_path):
        print(animation_path)
        print('File does not exist')
        return

    with open(animation_path, 'r') as file:
        animation = json.loads(file.read())
        
    changes = animation['changes']
    start = animation['start']
    size = animation['size']
    width = size[0]
    height = size[1]

    if dsize[0] is None or dsize[1] is None:
        dwidth = width
        dheight = height
    else:
        dwidth = dsize[0]
        dheight = dsize[1]

    if dwidth % 2 != 0:
        dwidth += 1
    if dheight % 2 != 0:
        dheight += 1

    divisor = len(changes)
    if divisor > 200:
        divisor = 200

    num_frames = duration*fps 

    base = Image.new('RGB', (size[0], size[1]), (0, 0, 0))
    basedraw = ImageDraw.ImageDraw(base)
    basedraw.point(xy=(start[0], start[1]), fill=(0, 255, 0))

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
        
    if dwidth != size[0] or dheight != size[1]:
        __resize_images(divisor)
    
    if os.path.exists(video_path):
        os.remove(video_path)
    
    if verbose:
        print('Generating video...')
    subprocess.call([
        'ffmpeg', '-r', str(fps), '-s',
        f'{dwidth}x{dheight}', '-i',
        './temp/%d.png', '-vcodec', 'libx264',
        '-crf', '25', '-pix_fmt', 'yuv420p', 'maze.mp4'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\
            
    for file in os.listdir('./temp'):
        os.remove('./temp/'+file)
    os.rmdir('./temp')


def main():
    dsize = input('input desired output width/height (default: original width/height): ')
    if dsize != '':
        dsize = (int(dsize.split('/')[0]), int(dsize.split('/')[1]))
    else:
        dsize = None

    duration_fps = input('aproximate video duration/fps (default: 60/60s): ')
    if duration_fps != '':
        duration = int(duration_fps.split('/')[0])
        fps = int(duration_fps.split('/')[1])
    else:
        duration = 60
        fps = 60

    verbose = input('verbose? (Y/n): ')
    if verbose.lower() != 'n':
        verbose = True
    else:
        verbose = False

    if dsize is not None:
        create_animation(dsize, duration=duration, fps=fps, video_path='maze.mp4', verbose=verbose)
    else:
        create_animation(duration=duration, fps=fps, verbose=verbose)

if __name__ == '__main__':
    main()