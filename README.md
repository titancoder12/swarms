# Swarm Simulations

![Swarm Simulation Screenshot](https://github.com/titancoder12/swarms/blob/main/Cover.png)

## Installation
1. Clone the repository:
```
git clone https://github.com/titancoder12/swarms
```

2. Install dependencies:
```
pip install -r requirements.txt
```

## Running the Simulation
To run a normal swarm simulation, type:
```
python pure-swarm.py
```
To run an example of swarm application, particularly in teamwork:
```
python swarm-soccer.py
```

A deployed version can also be found [here](https://replit.com/@babytitanlin/Swarm-Simulations).

## How does it work?
This project simulates a swarm of autonomous agents (boids) interacting with movable objects in a 2D environment. The simulation is based on the principles of flocking behavior and object manipulation. Here's a simple breakdown of the features and concepts that define the simulation:
1. **Boid behavior**:
    * Each boid follows three main rules to simulate natural flocking:
        * Alignment: Boids align their velocity with nearby boids.
        * Cohesion : Boids move toward the average position of nearby boids
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