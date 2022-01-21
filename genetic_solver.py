from email import generator
import random
import os
from statistics import mean, stdev
from datetime import datetime
from tqdm import tqdm
import matplotlib.pyplot as plt

from generator import Generator

class GeneticSolver:

    class Individual:
        __slots__ = ["solution", "num_leftovers", "num_sets", "sums", "fitness", "_solver"]

        def __init__(self, solution: list, solver: 'GeneticSolver') -> None:
            self.solution = solution
            self._solver = solver
        
        def cross(self, other: 'GeneticSolver.Individual') -> 'GeneticSolver.Individual':
            selection = [random.choice([False, True]) for _ in range(self._solver._n)]
            selector = lambda i: self.solution[i] * selection[i] + other.solution[i] * (not selection[i])

            ind = GeneticSolver.Individual([selector(i) for i in range(self._solver._n)], self._solver)
            ind.recalculate()

            return ind
        
        def mutate(self, probability: float = 0.01) -> None:
            for i in range(self._solver._n):
                if random.uniform(0, 1) > probability:
                    continue

                rs = random.randint(0, self._solver._n)

                if rs > self.num_sets:
                    self.num_sets += 1
                    rs = self.num_sets
                
                self.solution[i] = rs
        
        def swap_mutate(self, probability: float = 0.01) -> None:
            for i in range(self._solver._n):
                if random.uniform(0, 1) > probability:
                    continue

                j = random.randrange(i, self._solver._n)
                
                self.solution[i], self.solution[j] = self.solution[j], self.solution[i]

        def recalculate(self):
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

    class Logger:
        def __init__(self, parameters: list, interval: int = 1) -> None:
            self.series = {pn: [] for pn in parameters}
            self.generation = []
            self.initial = None
            self.solutions = {}
            self.interval = interval
        
        def log_initial(self, solver: 'GeneticSolver') -> None:
            self.initial = {k: v for k, v in solver.__dict__.items() if k[0] != '_' and isinstance(v, (int, float, bool))}
            self.initial['problem'] = solver.problem
        
        def log_parameters(self, generation: int, **kwargs) -> None:
            if generation % self.interval:
                return
            
            self.generation.append(generation)

            for k, v in kwargs.items():
                self.series[k].append(v)
        
        def log_solution(self, key: str, sln: 'GeneticSolver.Individual') -> None:
            self.solutions[key] = sln
            
        def show(self, param: str) -> None:
            plt.plot(self.series[param])
            plt.title(param)
            plt.show()
        
        def save(self, path: str, mode: str = 'ips') -> None:
            if path[-1] != '/':
                path += '/'
            path += datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
            os.makedirs(path)
            
            with open(f"{path}/log.txt", 'x') as f:
                f.write("GENETIC SOLVER REPORT\n")
                if 'i' in mode and self.initial:
                    for k, v in self.initial.items():
                        f.write(f" {k}: {str(v)}\n")
                
                if 's' in mode:
                    f.write("Saved solutions:")
                    for k, v in self.solutions.items():
                        f.write(f" {k}:\n")
                        for attr in v.__slots__:
                            if attr[0] != '_' and isinstance(getattr(v, attr), (int, float, bool, list)):
                                f.write(f"  {attr}: {str(getattr(v, attr))}\n")

                if 'p' in mode:
                    f.write("Tracked parameters:\n")
                    for k, v in self.series.items():
                        f.write(f" {k}: {str(v)}\n")

            if 'g' in mode:
                for k, v in self.series.items():
                    plt.figure()
                    plt.plot(self.generation, v)
                    plt.title(k)
                    plt.savefig(f"{path}/graph_{k}.png")

    def __init__(
            self,
            problem: list,
            T: int,
            pop_size: int,
            mating_ratio: float = 0.5,
            elitism_ratio: float = 0.1,
            mutation_rate: float = 0.01,
            swap_mutation_rate: float = 0.01,
            leftover_weight: float = 0.01,
            patience: int = 50) -> None:
        self.problem = problem
        self.T = T
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.swap_mutation_rate = swap_mutation_rate
        self.leftover_weight = leftover_weight

        self._logger = GeneticSolver.Logger(["best_fit", "avg_fit"], interval=50)

        assert mating_ratio + elitism_ratio < 1

        self.mating_pool_size = int(mating_ratio * pop_size)
        self.elite_size = int(elitism_ratio * pop_size)

        self._early_stop_counter = 0
        self.patience = patience

        self._n = len(problem)
        self._mean = mean(problem)
        self._stdev = stdev(problem)

        assert self._n > 0

        # initialize population
        self.population = [self._random_individual() for _ in range(pop_size)]
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.total_fitness = sum([sln.fitness for sln in self.population])

        self._logger.log_initial(self)

    def run(self, generations: int) -> None:
        with tqdm(range(generations), postfix={'best': self.population[0].fitness}, disable=False) as progress_bar:
            for gen in progress_bar:
                self._early_stop_counter += 1
                if self._early_stop_counter >= self.patience:
                    print("Early stopping triggered on generation", gen)
                    break

                #  select parents
                mating_pool = []

                step = self.total_fitness / self.pop_size
                cur_selection_point = random.uniform(0, step)            
                total_visited = 0
                for sln in self.population:
                    if total_visited + sln.fitness >= cur_selection_point:
                        cur_selection_point += step
                        mating_pool.append(sln)

                    total_visited += sln.fitness
                
                # advance elite to next generation
                new_generation = self.population[:self.elite_size]

                assert len(new_generation) <= self.elite_size
                
                self.total_fitness = sum([sln.fitness for sln in new_generation])

                # crossover and generate new population
                for _ in range(self.pop_size - len(new_generation)):
                    a = random.choice(mating_pool)
                    b = random.choice(mating_pool)
                    while a is b:
                        if len(mating_pool) < 2:
                            break

                        b = random.choice(mating_pool)
                    
                    child = a.cross(b)
                    child.mutate(self.mutation_rate)
                    child.swap_mutate(self.swap_mutation_rate)
                    child.recalculate()
                    self.total_fitness += child.fitness
                    new_generation.append(child)
                
                old_best = self.population[0].fitness

                self.population = new_generation
                self.population.sort(key=lambda x: x.fitness, reverse=True)
                
                if self.population[0].fitness > old_best:
                    self._early_stop_counter = 0
                    progress_bar.set_postfix(best=self.population[0].fitness)
                
                self._logger.log_parameters(
                    generation=gen,
                    best_fit=self.population[0].fitness,
                    avg_fit=self.total_fitness / self.pop_size
                )
        
        self._logger.log_solution("best", self.population[0])

    def get_fitness(self, individual: Individual) -> float:
        return 1 / (1 + sum(map(lambda x: (abs(self.T - x) / self._stdev) ** 2, individual.sums))
                     + self.leftover_weight * individual.num_leftovers / self._n)

    def get_solution(self, n: int = 0) -> list:
        sln = self.population[n]
        res = [[] for _ in range(sln.num_sets)]
        
        for i, v in enumerate(sln.solution):
            if v > 0:
                res[v - 1].append(self.problem[i])

        return [x for x in res if x != []]

    def _random_individual(self) -> 'Individual':
        max_n_sets = random.randint(1, self._n)
        s = [0] * self._n
        n_sets = 0
        for i in range(self._n):
            rs = random.randint(0, max_n_sets)

            if rs > n_sets:
                n_sets += 1
                rs = n_sets
            
            s[i] = rs

        ind = GeneticSolver.Individual(s, self)
        ind.recalculate()
        
        return ind

if __name__=='__main__':
    gen = Generator()

    gs = GeneticSolver(
        gen.generate_random_set(100, 0, 120), T=600,
        pop_size=100,
        patience=10000,
        elitism_ratio=0.2,
        mutation_rate=0.03,
        swap_mutation_rate=0.02,
        leftover_weight=0.01
    )
    gs.run(100000)
    print("Square distances from T:", list(map(lambda x: abs(gs.T - x) ** 2, gs.population[0].sums)))
    print(gs.population[0].solution)
    best = gs.get_solution()
    print("Best solution:", best, ", score:", gs.population[0].num_leftovers / gs._n)
    gs._logger.save("log/", mode='ipgs')
