"""
PSO = Particle Swarm Optimization

Proposed in 1995 by J. Kennedy and DR.Eberhart, the Particle Swarm Optimization (PSO) algorithm  
was born out of the observation that birds and fish often move in groups, following a leader or a common direction. 
This collective behavior allows them to search for food, avoid predators, and navigate through complex environments,

----------------------------------------------------------------------------------------------------------

Author: Muhamad Dimas Wijaya
Date: 2025-07-2
----------------------------------
"""


"""Import necessary libraries"""

import numpy as np
import matplotlib.pyplot as plt

class Particle:

    def __init__(self, dim, bounds, vmax):

        """
        ===========================================================================================
        Initialize the Particle object with the specified parameters
    
        Parameters:
            dim = The dimension of the problem
            bounds = The bounds of each dimension
            vmax = The maximum velocity
        
        For particle initialization:
            self.position = Random position of each vector, each dimension is within the bound limit
            self.velocity = Random velocity of each vector, each dimension is within the bound limit
            self.pbest_position = The best position of the particle
            self.pbest_value = The best fitness value of the particle()

        ==========================================================================================
        """
        
        self.dim = dim
        self.bounds = bounds
        self.vmax = vmax
        self.position = np.array([np.random.uniform(low, high) for low, high in bounds])
        self.velocity = np.random.uniform(-vmax, vmax, dim)
        self.pbest_position = self.position.copy()
        self.pbest_value = float('inf')



    def update_velocity(self, gbest_position, w, c1, c2):

        """
        ========================================================================================== 
        Update the velocity and position of the particle
    
        Parameters:
            gbest_position = The best position of the swarm
            w = The inertia weight
            c1 = Cognitive constant
            c2 = Social constant

        Velocity update:
            v(t+1) = w * v(t) + c1 * r1 * (pbest - x(t)) + c2 * r2 * (gbest - x(t))
    
        Position update:
            x(t+1) = x(t) + v(t+1)
        ==========================================================================================
        """

        r1, r2 = np.random.rand(self.dim), np.random.rand(self.dim)
        cognitive = c1 * r1 * (self.pbest_position - self.position)
        social = c2 * r2 * (gbest_position - self.position)
        self.velocity = w * self.velocity + cognitive + social
        self.velocity = np.clip(self.velocity, -self.vmax, self.vmax)

    def update_position(self):

        """
        Update the position of the particle by adding the velocity to the current position.
        Make sure the new position is within the bounds of the problem by clipping it.
        """

        self.position += self.velocity
        for i, (low, high) in enumerate(self.bounds):
            self.position[i] = np.clip(self.position[i], low, high)

class PSO:
    def __init__(self, func, dim=2, bounds=None, num_particles=30, iterations=100, w=0.5, c1=1.5, c2=1.5, vmax=1.0):

        """
        Initialize the PSO object with the specified parameters

        Parameters:
            func = The function to be optimized
            dim = The dimension of the problem
            bounds = The bounds of each dimension
            num_particles = The number of particles in the swarm
            iterations = The number of iterations
            w = The inertia weight
            c1 = Cognitive constant
            c2 = Social constant
            vmax = The maximum velocity

        For particle initialization:
            self.position = Random position of each vector, each dimension is within the bound limit
            self.velocity = Random velocity of each vector, each dimension is within the bound limit
            self.pbest_position = The best position of the particle
            self.pbest_value = The best fitness value of the particle

        ==========================================================================================
        """

        self.func = func
        self.dim = dim
        self.bounds = bounds
        self.iterations = iterations
        self.particles = [Particle(dim, bounds, vmax) for _ in range(num_particles)]
        self.gbest_position = None
        self.gbest_value = float('inf')
        self.w, self.c1, self.c2 = w, c1, c2
        self.history = []

    def optimize(self):

        """
        ==========================================================================================
        Run the optimization process for the specified number of iterations.

        At each iteration:

        1. Evaluate the fitness of each particle.
        2. Update the personal best position and fitness of each particle if the current
           fitness is better.
        3. Update the global best position and fitness if the current fitness is better.
        4. Update the velocity and position of each particle using the PSO update rules.
        5. Store the global best fitness in the history list.

        After the optimization process is finished, the best position and fitness can be
        accessed using the `gbest_position` and `gbest_value` attributes, and the
        convergence curve can be plotted using the `plot_convergence` method.

        ==========================================================================================
        """

        for _ in range(self.iterations):
            for p in self.particles:
                value = self.func(p.position)
                if value < p.pbest_value:
                    p.pbest_value = value
                    p.pbest_position = p.position.copy()
                if value < self.gbest_value:
                    self.gbest_value = value
                    self.gbest_position = p.position.copy()

            for p in self.particles:
                p.update_velocity(self.gbest_position, self.w, self.c1, self.c2)
                p.update_position()

            self.history.append(self.gbest_value)

    def plot_convergence(self):

        """
        Plot the convergence curve of the optimization process.

        This method visualizes the best fitness value recorded at each iteration
        during the optimization process. The x-axis represents the iteration number,
        and the y-axis represents the best fitness value found up to that iteration.
        
        """


        plt.plot(self.history)
        plt.title('Convergence Curve')
        plt.xlabel('Iteration')
        plt.ylabel('Best Fitness')
        plt.grid()
        plt.show()

    def plot_particles_2d(self):
        """
        ================================================================================
        Plot the positions of particles in a 2D space.

        This method visualizes the current positions of all particles in the swarm when 
        the problem is two-dimensional. Each particle is represented as a blue circle, 
        and the global best position is highlighted as a red star. The plot's axes are 
        set according to the defined bounds for the problem.

        Note:
            This method only works for problems with two dimensions. If the problem 
            dimension is not 2, a message is printed and the method exits.

        ================================================================================
        """

        if self.dim != 2:
            print("2D plot is only available for 2D problems.")
            return

        fig, ax = plt.subplots()
        ax.set_xlim(self.bounds[0])
        ax.set_ylim(self.bounds[1])
        ax.set_title("Particle Positions (2D)")

        for p in self.particles:
            ax.plot(*p.position, 'bo')
        ax.plot(*self.gbest_position, 'r*', markersize=12, label='Global Best')
        ax.legend()
        plt.show()
