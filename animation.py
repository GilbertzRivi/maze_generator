from PIL import Image, ImageDraw
from progress.bar import IncrementalBar as Bar
import json, os, threading

def save_image(image: list):
    image[0].save(f'./temp/{image[1]}.png')

def save_resize_image(image, dwidth, dheight):
    path = './temp/' + image
    image = Image.open(path)
    image = image.resize((dwidth, dheight), resample=0)
    os.remove(path)
    image.save(path)

def generate_images(base, changes: dict, start: list, num_frames: int, divisor: int) -> None:
    with Bar('Generating Images', max=divisor, suffix = '%(percent).1f%% - eta: %(eta)ds') as bar:
        if len(changes) < num_frames:
            skip_frames = 1
        else:
            skip_frames = int(len(changes)/num_frames)
        generated_frame_counter = 0
        frames = []
        for i, step in enumerate(changes):
            imdraw = ImageDraw.ImageDraw(base)
            imdraw.point(xy=(step['x'], step['y']), fill=(255, 0, 0))
            imdraw.point(xy=(changes[i-1]['x'], changes[i-1]['y']), fill=(255, 255, 255))
            if i == 2:
                imdraw.point(xy=(start[0], start[1]), fill=(0, 255, 0))
            if i % skip_frames == 0 or i == len(changes):
                frames.append([base.copy(), generated_frame_counter])
                generated_frame_counter += 1
            if i % int(len(changes)/divisor) == 0:
                bar.next()
            if generated_frame_counter % 100 == 0:
                threads = [threading.Thread(target=save_image, args=[image]) for image in frames]
                [t.start() for t in threads]
                [t.join() for t in threads]
                frames = []
        
        threads = [threading.Thread(target=save_image, args=[image]) for image in frames]
        [t.start() for t in threads]
        [t.join() for t in threads]

def resize_images(divisor, dwidth, dheight):
    with Bar('Resizing Images', max=divisor, suffix = '%(percent).1f%% - eta: %(eta)ds') as bar:
        threads = []
        images = []
        images_num = len(os.listdir('./temp'))
        for i, image in enumerate(os.listdir('./temp')):
            images.append(image)
            if len(images) % 100 == 0:
                threads = [threading.Thread(target=save_resize_image, args=[image, dwidth, dheight]) for image in images]
                [t.start() for t in threads]
                [t.join() for t in threads]
                images = []
            if i % int(images_num/divisor) == 0:
                bar.next()
                
        threads = [threading.Thread(target=save_resize_image, args=[image, dwidth, dheight]) for image in images]
        [t.start() for t in threads]
        [t.join() for t in threads]

def main():
    if not os.path.isfile('./changes.json'):
        print('No maze has been generated yet')
        input('Press enter to continue ')
        exit()

    with open('changes.json', 'r') as file:
        animation = json.loads(file.read())

    width, height = animation['size'][0], animation['size'][1]
    start = animation['start']
    changes = animation['changes']
    divisor = len(changes)
    if divisor > 200:
        divisor = 200

    print(f'maze size: {width}x{height}')
    dwidth = input('input desired output width (blank means same as maze (must be divisible by 2)): ')
    if dwidth == '':
        dwidth = width
    else:
        dwidth = int(dwidth)

    dheight = int(dwidth/(width/height))

    if dwidth % 2 != 0:
        dwidth += 1
    if dheight % 2 != 0:
        dheight += 1

    duration = input('aproximate video duration (seckonds, blank for 60, min:2): ')
    if duration == '':
        duration = 60
    else:
        duration = int(duration)
    fps = 60
    num_frames = duration*fps 

    base = Image.new('RGB', (width, height), (0, 0, 0))
    basedraw = ImageDraw.ImageDraw(base)
    basedraw.point(xy=(start[0], start[1]), fill=(0, 255, 0))

    try:
        for file in os.listdir('./temp'):
            os.remove('./temp/'+file)
        os.rmdir('./temp')
    except:
        pass

    os.mkdir('./temp')

    generate_images(base, changes, start, num_frames, divisor)

    if divisor > len(os.listdir('./temp')):
        divisor = len(os.listdir('./temp')) 

    if dwidth != width:
        resize_images(divisor, dwidth, dheight)

    os.system(f'ffmpeg -r {fps} -s {dwidth}x{dheight} -i ./temp/%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p maze.mp4')

    for file in os.listdir('./temp'):
        os.remove('./temp/'+file)
    os.rmdir('./temp')

if __name__ == '__main__':
    main()