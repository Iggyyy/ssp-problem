import random
from generator import Generator

class GeneticSolver:

    class Individual:
        __slots__ = ["solution", "num_leftovers", "num_sets", "sums", "_solver"]

        def __init__(self, solution: list, solver: 'GeneticSolver') -> None:
            self.solution = solution
            self._solver = solver
            self._calculate_properties()
        
        def cross(self, other: 'GeneticSolver.Individual') -> 'GeneticSolver.Individual':
            selection = [random.choice([False, True]) for _ in range(self._solver._n)]
            selector = lambda i: self.solution[i] * selection[i] + other.solution[i] * (not selection[i])

            return GeneticSolver.Individual([selector(i) for i in range(self._solver._n)], self._solver)
        
        def mutate(self, probability: float) -> None:
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

    def __init__(self, problem: list, T: int, pop_size: int) -> None:
        self.problem = problem
        self.T = T
        self.pop_size = pop_size
        # TODO: standardize problem values & T?

        self._n = len(problem)

        # initialize population
        self.population = [self._random_individual() for _ in range(pop_size)]

        for pop in self.population:
            print("I loss:", self.get_fitness(pop))

    def run(self, generations: int) -> None:
        for _ in range(generations):
            #  select parents
            #  crossover and generate new population
            #  perform mutation
            #  calculate fitness
            pass

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
#  select parents
#  crossover [v]
#  and generate new population
#  perform mutation [v]
#  calculate fitness [v]

gen = Generator()
gs = GeneticSolver(gen.generate_random_set(40), 20, 20)

aa = gs._random_individual()
bb = gs._random_individual()

print(aa.solution)
print(bb.solution)
print(aa.cross(bb).solution)

bb.mutate(0.3)
print(bb.solution)

