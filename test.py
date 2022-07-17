import generator, time
from progress.bar import IncrementalBar as Bar

iterations = int(input('How many iterations: '))
width = int(input('maze width/height: '))
dwidth = int(input('image width/height: '))
times = []

with Bar('Generating mazes', max=iterations, suffix = '%(percent).1f%% - eta: %(eta)ds') as bar:
    for iter in range(iterations):
        start = time.time()
        generator.start(width, dwidth, False)
        end = time.time()
        times.append(end-start)
        bar.next()
        
avg = 0
sumtime = 0
for onetime in times:
    avg += onetime
sumtime = avg
avg /= len(times)
print(f'Generated {iterations} mazes in {round(sumtime, 2)}s avg: {round(avg, 2)}s')