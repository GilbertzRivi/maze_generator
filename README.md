# maze_generator
You need to have ffmpeg installed for animation.py to work.

To generate a maze, run generator.py, and input maze width/heigth (they are the same), then input resolution you'd like for your maze.png and wait.

To create animation from maze generation, run animation.py, input desired resolution and animation length and wait for the script to do the rest.

Note that files generated during generation of an animation my take up to gigabytes. For example, I've generated 320s long animation in resolution 2200x2200, changes.json took 250MB and temp folder took 11GB. 

To solve maze, open solver.py and input path to the maze, then resolution of the MAZE, not the IMAGE. If your maze is in oryginal resolution (paths and walls are 1px thick) you don't need to input anything.
