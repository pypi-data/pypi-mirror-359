
"""ABC = Artificial Bee Colony

The Artificial Bee Colony (ABC) algorithm is based on the
intelligent foraging behaviour of honey bee swarm, and was first proposed
by Karaboga in 2005.

Author: Muhamad Dimas Wijaya
Date: 2025-07-2
==========================================================================================================
"""



"""Import necessary libraries"""
import numpy as np
import matplotlib.pyplot as plt

class Bee:
    """Create a bee object"""

    def __init__(self, dim, bounds):

        """
        ===========================================================================================

        initialize 1 Bee object to be placed in a random location

        Parameters:
        self.position = Random position of each vector, each dimension is within the bound limit
        self.fitness = The fitness values (smallest and largest) are initialized to infinity
        self.trial = Counting how many times the solution does not improve

        ===========================================================================================
        """

        self.bounds = bounds
        self.position = np.array([np.random.uniform(low, high) for low, high in bounds])
        self.fitness = float('inf')
        self.trial = 0

    def evaluate(self, func):
        """
        ===========================================================================================
        Calculating the fitness value of the current solution
        1. Run the func(The function referred to is the objective function that will be executed)
        2. save the result inside self.fitness
        ===========================================================================================
        """

        self.fitness = func(self.position)

    def mutate(self, phi, other):

        """
        ===========================================================================================
        Create new solution(mutate) from the current solution by comparing one solution to another(other bee employed)
        
        Parameters:
            phi = Random number [-1, 1]
            v[j] = Random value expansion
            oter.position[j] = Random value from other bee
            v[j] = np.clip(v[j], low, high) => Functions to limit the value so that it does not exceed the upper and lower limits

        This process aims to produce new solutions that are different from the current solutions
        ===========================================================================================
        """

        dim = len(self.position)
        j = np.random.randint(0, dim)
        v = self.position.copy()
        v[j] = self.position[j] + phi * (self.position[j] - other.position[j])
        # Make sure to stay within the bounds.
        low, high = self.bounds[j]
        v[j] = np.clip(v[j], low, high)
        return v

class ABC:
    """Create an ABC object"""
    """Managing the entire bee colony and implementing the optimization process until the best solution is found."""
    
    def __init__(self, func, dim, bounds, num_bees=30, limit=50, iterations=100):
               
        """
        ===========================================================================================
        Initialize the ABC object with the specified parameters

        Parameters:
            func = The function to be optimized (objective function)
            dim = The dimension of the problem
            bounds = The bounds of each dimension
            num_bees = The number of bees in the colony (solutions)
            limit = The maximum number of times a bee can fail to improve its solution
            iterations = The cycle of optimization

        For colony initialization:
            self.colony = [Bee(dim, bounds) for _ in range(num_bees)]
        
        Tracking result:
            self.best_position = best solution
            self.best_fitness = best fitness value
            self.fitness_history = graphics history

        ===========================================================================================
        """

        self.func = func
        self.dim = dim
        self.bounds = bounds
        self.num_bees = num_bees
        self.limit = limit
        self.iterations = iterations
        self.colony = [Bee(dim, bounds) for _ in range(num_bees)]
        self.best_position = None
        self.best_fitness = float('inf')
        self.fitness_history = []

    def optimize(self):
        
        """
        
        The essence are here! The process is to follow the cycle of bees in real life.
        
        ===========================================================================================
        1. Employed Bees Phase
        2. Onlooker Bees Phase
        3. Scout Bees Phase
        ===========================================================================================

        """

        for bee in self.colony:   
            bee.evaluate(self.func)


        """ the goal in the loop of employed bees is:
            - Finding better solutions by making mutations on bee positions.
            - Avoiding stagnation on the same solution by randomly selecting neighboring bees.
            - Adjusting the trial values of bees to monitor how many different solutions they have tried.
        """    
        for t in range(self.iterations):
            # Employed Bees Phase
            for i, bee in enumerate(self.colony):
                k = np.random.choice([j for j in range(self.num_bees) if j != i])
                phi = np.random.uniform(-1, 1)
                new_pos = bee.mutate(phi, self.colony[k])
                new_fitness = self.func(new_pos)
                if new_fitness < bee.fitness:
                    bee.position = new_pos
                    bee.fitness = new_fitness
                    bee.trial = 0
                else:
                    bee.trial += 1

            # Calculate probabilities for onlookers
            fitnesses = np.array([1 / (1 + bee.fitness) for bee in self.colony])
            probs = fitnesses / np.sum(fitnesses)

            """ Onlooker Bees Phase:
            Choosing colony solutions based on proportional fitness probability,
            and then making mutations on the selected solutions. same as employed bees
            Analogous to employed bees: The bee imitates solutions "that looks good" from other bees
            """
            # Onlooker Bees Phase
            for _ in range(self.num_bees):
                i = np.random.choice(range(self.num_bees), p=probs)
                bee = self.colony[i]
                k = np.random.choice([j for j in range(self.num_bees) if j != i])
                phi = np.random.uniform(-1, 1)
                new_pos = bee.mutate(phi, self.colony[k])
                new_fitness = self.func(new_pos)
                if new_fitness < bee.fitness:
                    bee.position = new_pos
                    bee.fitness = new_fitness
                    bee.trial = 0
                else:
                    bee.trial += 1

            """ Scout Bees Phase:
            If a bee has not found a better solution for a certain number of times, it is replaced by a random solution
            Analogous to employed bees: There is a bee that is bored and flies to search for other 'flowers' in a new place.
            """
            # Scout Bees Phase
            for bee in self.colony:
                if bee.trial > self.limit:
                    bee.position = np.array([np.random.uniform(low, high) for low, high in self.bounds])
                    bee.evaluate(self.func)
                    bee.trial = 0

            """ Update best:
            After one cycle (employed, onlooker, scout), check and save the best solution.
            And Save the results for the convergence graph.
            """
            # Update best
            for bee in self.colony:
                if bee.fitness < self.best_fitness:
                    self.best_fitness = bee.fitness
                    self.best_position = bee.position.copy()

            self.fitness_history.append(self.best_fitness)

    def plot_convergence(self):

        """
        Plot the convergence curve of the optimization process.

        This method visualizes the best fitness value recorded at each iteration
        during the optimization process. The x-axis represents the iteration number,
        and the y-axis represents the best fitness value found up to that iteration.

        """

        plt.plot(self.fitness_history)
        plt.title('Convergence Curve (ABC)')
        plt.xlabel('Iteration')
        plt.ylabel('Best Fitness')
        plt.grid()
        plt.show()
