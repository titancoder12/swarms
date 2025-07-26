# Swarm Simulations

![Swarm Simulation Screenshot](https://github.com/titancoder12/swarms/blob/main/Cover.png)

## Running the Simulation
**Note: It takes quite long to launch. Please be patient.**
**Note: The executible is built and tested only on MacOS.**

### Download and run the executables.
There are two executables for two types of swarms:
Executable 1. Pure Swarm: 
[download](https://drive.google.com/file/d/1oJgk7xt0dHocAXpRzU_tmRSDZpqCQ39L/view?usp=drive_link)

Executable 2. Soccer Swarm:
[download](https://drive.google.com/file/d/1QCGxuCZWEL1eOjKh03M5Cww9WggqVLOn/view?usp=drive_link)

### You can also download the entire folder
Click [here](https://drive.google.com/drive/folders/1dNAaib_xn4cwSS-aUe3-A7wl6IEqxnNz?usp=drive_link) and download the entire folder in Google Drive.

## Cd into the directory
Open up the terminal and navigate into the location you downloaded.

Enter into the folder you downloaded by running:
```
cd dist
```

### Running the executible on macOS

To run a normal swarm simulation, type:
```
./pure-swarm
```
To run an example of swarm application, particularly in teamwork:
```
./swarm-soccer
```

### Running the executible on Windows

The Mac/Linux executibles without extensions cannot be run with Windows. 

Try running it with `python`:
```
python pure-swarm.py
python swarm-soccer.py
```

Click the plus symbol next to 'boids' to add a few autonomous agents. Try playing around with the other parameters as well!

If there are any issues, the program can also be run on Replit by clicking [here](https://replit.com/@babytitanlin/Swarm-Simulations).

## Installation
1. Create a directory for the project:

    For example...
    ```
    mkdir example_dir
    ```
    Then, cd into the directory.
    ```
    cd example_dir
    ```

2. (Optional) Create a virtual environment:
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    ```
3. Clone the repository:
    Clone the repo into the directory
    ```
    git clone https://github.com/titancoder12/swarms
    ```

5. Cd into 'swarms' directory:
    ```
    cd swarms
    ```

4. Cd into the 'dist' directory:
    ```
    cd dist
    ```

## Adjustable Parameters

### **Boids**
Controls the number of autonomous agents in the simulation. More boids create complex flocking behavior but may impact performance.

### **Max Speed**
Sets how fast boids can move. Higher values create faster, more erratic movement; lower values produce smoother motion.

### **Max Force**
Determines how quickly boids can change direction. Higher values allow sharp turns; lower values create gradual, realistic movement.

### **Neighbor Radius**
Defines how far boids can "see" other boids. Larger radius creates cohesive flocks; smaller radius results in scattered behavior.

### **Separation Radius**
Sets the minimum distance boids maintain from each other. Prevents overcrowding while maintaining group cohesion.

### **Object Separation**
Controls how far boids stay from obstacles and objects. Critical for object manipulation tasks in goal mode.

## How does it work?
This project simulates a swarm of autonomous agents (boids) interacting with movable objects in a 2D environment. The simulation is based on the principles of flocking behavior and object manipulation. Here's a simple breakdown of the features and concepts that define the simulation:
1. **Boid behavior**:
    * Each boid follows [three main rules](https://en.wikipedia.org/wiki/Boids) to simulate natural flocking:
        * Alignment: Boids align their velocity with nearby boids.
        * Cohesion : Boids move toward the average position of nearby boids.
        * Seperation: Boids avoid crowding by steering away from nearby boids and obstacles.
    * These behaviors are combined with additional forces, such as attraction to objects or scattering, to achieve specific goals.

2. **Movable objects**:
    * The simulation includes movable objects (balls, blocks, etc.) that boids can interact with.
    * Boids can push these objects towards a target position (as seen in swarm-soccer.py) and also dodge them (as seen in pure-swarm.py)

3. **Interaction with the Environment**:
    * Boids avoid collisions with obstacles (blocks) and the edges of the screen.
    * Movable objects are constrained within the screen boundaries and experience friction to simulate realistic motion.

4. **Goal Achievement**:
    * The simulation defines a target position (a green circle) where all movable objects need to be placed.
    * Boids work together to push the objects into the goal area. Once all objects are within the goal radius, the goal is considered achieved.

5. **User Interaction**:
    * The user can interact with the simulation through a UI, which allows adding or removing boids, adjusting parameters (e.g., speed, force, and radii), and dragging objects directly with the mouse.

6. **Broadcasting and Coordination**:
    * Boids can broadcast information to nearby boids within a certain radius, enabling coordinated behavior for tasks like object manipulation.

This combination of flocking behavior, object manipulation, and user interaction creates a dynamic and engaging simulation of swarm intelligence.


## Credits
This project uses components from [nazishjaveed/Swarm_Agent](https://github.com/nazishjaveed/Swarm_Agent). Huge credit to the original author for his excellent work.
