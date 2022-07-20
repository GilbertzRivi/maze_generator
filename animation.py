from unittest import skip
from PIL import Image, ImageDraw
from progress.bar import IncrementalBar as Bar
import json, os

if not os.path.isfile('./changes.json'):
    print('No maze has been generated yet')
    input('Press enter to continue ')
    exit()

with open('changes.json', 'r') as file:
    animation = json.loads(file.read())

start = animation['start']
changes = animation['changes']
width = len(start)
height = len(start['0'])
divisor = len(changes)
if divisor > 200:
    divisor = 200

print(f'maze size: {width}x{height}')
dwidth = int(input('input desired output width: '))
dheight = int(dwidth/(width/height))

duration = int(input('aproximate video duration (seckonds): '))
fps = 60
num_frames = duration*fps 

base = Image.new('RGBA', (width, height), (0, 0, 0, 255))
basedraw = ImageDraw.ImageDraw(base)
for x in start:
    for y in start[x]:
        tile = start[x][y]
        if tile == 'p':
            basedraw.point(xy=(int(x), int(y)), fill=(255, 255, 255, 255))

os.mkdir('./temp')

with Bar('Generating Images', max=divisor, suffix = '%(percent).1f%% - eta: %(eta)ds') as bar:
    if len(changes) < num_frames:
        skip_frames = 1
    else:
        skip_frames = int(len(changes)/num_frames)
    saved_frame_counter = 0
    for i, step in enumerate(changes):
        imdraw = ImageDraw.ImageDraw(base)
        imdraw.point(xy=(step['x'], step['y']), fill=(255, 0, 0, 255))
        imdraw.point(xy=(changes[i-1]['x'], changes[i-1]['y']), fill=(255, 255, 255, 255))
        if i % skip_frames == 0 or i == len(changes):
            base.save(f'./temp/{saved_frame_counter}.png')
            saved_frame_counter += 1
        if i % int(len(changes)/divisor) == 0:
            bar.next()

if divisor > len(os.listdir('./temp')):
    divisor = len(os.listdir('./temp')) 

if dwidth != width:
    with Bar('Resizing Images', max=divisor, suffix = '%(percent).1f%% - eta: %(eta)ds') as bar:
        images_num = len(os.listdir('./temp'))
        for i, path in enumerate(os.listdir('./temp')):
            path = './temp/' + path
            image = Image.open(path)
            image = image.resize((dwidth, dheight), resample=0)
            os.remove(path)
            image.save(path)
            if i % int(images_num/divisor) == 0:
                bar.next()

os.system(f'ffmpeg -r {fps} -s {dwidth}x{dheight} -i ./temp/%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p maze.mp4')

for file in os.listdir('./temp'):
    os.remove('./temp/'+file)
os.rmdir('./temp')