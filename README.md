# Swarm Simulations

![Swarm Simulation Screenshot](https://github.com/titancoder12/swarms/blob/main/Cover.png)

## Installation

### Install using UV
1. Create a new directory:
    ```
    mkdir swarms_test
    cd swarms_test
    ```
2. Clone the repository:
    ```
    git clone https://github.com/titancoder12/swarms
    cd swarms
    ```

3. Run the setup script:
   
   ```
   ./setup-uv.sh
   ```

4. Activate the environment:
   
   ```
   source .venv/bin/activate
   ```

## Running the Simulations
**Note: It takes a few seconds to launch. Please be patient.**
**Note: This has only been tested on MacOS.***

To run a demonstration of swarms and their algorithm, run:
```
python pure-swarm.py
```

To run a demonstration of swarms working collectively to achieve a task, run:
```
python swarm-soccer.py
```

Click the plus symbol next to 'boids' to add a few autonomous agents. Try playing around with the other parameters as well!

If there are any issues, the program can also be run on Replit by clicking [here](https://replit.com/@babytitanlin/Swarm-Simulations).

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
