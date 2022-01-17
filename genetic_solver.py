import random
from statistics import mean, stdev
from generator import Generator

class GeneticSolver:

    class Individual:
        __slots__ = ["solution", "num_leftovers", "num_sets", "sums", "fitness", "_solver"]

        def __init__(self, solution: list, solver: 'GeneticSolver') -> None:
            self.solution = solution
            self._solver = solver
            self._calculate_properties()
        
        def cross(self, other: 'GeneticSolver.Individual') -> 'GeneticSolver.Individual':
            selection = [random.choice([False, True]) for _ in range(self._solver._n)]
            selector = lambda i: self.solution[i] * selection[i] + other.solution[i] * (not selection[i])

            return GeneticSolver.Individual([selector(i) for i in range(self._solver._n)], self._solver)
        
        def mutate(self, probability: float = 0.01) -> None:
            for i in range(self._solver._n):
                if random.uniform(0, 1) > probability:
                    continue

                rs = random.randint(0, self._solver._n)

                if rs > self.num_sets:
                    self.num_sets += 1
                    rs = self.num_sets
                
                self.solution[i] = rs
            
            self._calculate_properties()

        def _calculate_properties(self):
            self.num_leftovers = self.solution.count(0)
            # self.num_sets = len(set(self.solution)) - (self.num_leftovers > 0)
            self.num_sets = max(self.solution)

            # prune empty sets?

            self.sums = [0] * self.num_sets
            for i in range(self._solver._n):
                if self.solution[i] == 0:
                    continue
                
                self.sums[self.solution[i] - 1] += self._solver.problem[i]
            
            self.fitness = self._solver.get_fitness(self)
        
        def __lt__(self, other: 'GeneticSolver.Individual') -> bool:
            return self.fitness < other.fitness

    def __init__(
            self,
            problem: list,
            T: int,
            pop_size: int,
            mating_ratio: float = 0.5,
            elitism_ratio: float = 0.1) -> None:
        self.problem = problem
        self.T = T
        self.pop_size = pop_size

        assert mating_ratio + elitism_ratio < 1

        self.mating_pool_size = int(mating_ratio * pop_size)
        self.elite_size = int(elitism_ratio * pop_size)
        # TODO: standardize problem values & T?

        self._n = len(problem)
        self._mean = mean(problem)
        self._stdev = stdev(problem)


        # initialize population
        self.population = [self._random_individual() for _ in range(pop_size)]
        self.population.sort(reverse=True)
        self.total_fitness = sum([sln.fitness for sln in self.population])

        for pop in self.population:
            print("I fitness:", self.get_fitness(pop))

    def run(self, generations: int) -> None:
        for gen in range(generations):
            #  select parents
            mating_pool = []

            step = self.total_fitness / self.pop_size
            cur_selection_point = random.uniform(0, step)            
            total_visited = 0
            for sln in sorted(self.population):
                if total_visited + sln.fitness >= cur_selection_point:
                    cur_selection_point += step
                    mating_pool.append(sln)

                total_visited += sln.fitness
            
            # advance elite to next generation
            new_generation = self.population[:self.elite_size]
            assert len(new_generation) == self.elite_size
            self.total_fitness = sum([sln.fitness for sln in new_generation])

            # crossover and generate new population
            for _ in range(self.pop_size - self.elite_size):
                a = random.choice(mating_pool)
                b = random.choice(mating_pool)
                while a is b:
                    b = random.choice(mating_pool)
                
                child = a.cross(b)
                self.total_fitness += child.fitness
                child.mutate(0.02)
                new_generation.append(child)
            
            self.population = new_generation
            self.population.sort(reverse=True)
            
            if gen % 20 == 0:
                print("generation", gen, ": top 8 solutions:")
                for i in range(8):
                    print(" I fit:", new_generation[i].fitness)

    def get_fitness(self, individual: Individual) -> float:
        return 1 / (sum(map(lambda x: abs(self.T - x) * abs(self.T - x), individual.sums)) + individual.num_leftovers)

    def _random_individual(self) -> 'Individual':
        # TODO: encourage larger sets?
        
        s = [0] * self._n
        n_sets = 0
        for i in range(self._n):
            rs = random.randint(0, self._n)

            if rs > n_sets:
                n_sets += 1
                rs = n_sets
            
            s[i] = rs
        
        return GeneticSolver.Individual(s, self)

# generate problem [v]
# initialize solution population [v]
# calculate fitness [v]
# repeat:
#  select parents [v]
#  crossover [v]
#  and generate new population [v]
#  perform mutation [v]
#  calculate fitness [v]

gen = Generator()
gs = GeneticSolver(gen.generate_random_set(40), 20, pop_size=100, elitism_ratio=0.05)

gs.run(800)
print(gs.population[0].sums)
