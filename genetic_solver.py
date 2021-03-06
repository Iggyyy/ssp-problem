import random
import os
from statistics import mean, stdev
import json
from datetime import datetime
import argparse
from tqdm import tqdm
import matplotlib.pyplot as plt

from generator import Generator
from greedy_solver import GreedySolver
from GRASP import GRASP

class GeneticSolver:

    class Individual:
        __slots__ = ["solution", "num_leftovers", "num_sets", "sums", "fitness", "_solver"]

        def __init__(self, solution: list, solver: 'GeneticSolver') -> None:
            '''
            Params:
                `solution`: subset membership vector representation of this individual's solution
                `solver`: GeneticSolver instance to which this individual belongs
            '''
            self.solution = solution
            self._solver = solver
            self.num_leftovers = 0
            self.num_sets = 0
            self.sums = []
            self.fitness = 0.0
        
        def cross(self, other: 'GeneticSolver.Individual') -> 'GeneticSolver.Individual':
            '''
            Perform crossover between this individual and `other`, return the child
            Params:
                `other`: other individual instance to perform crossover with
            '''
            selection = [random.choice([False, True]) for _ in range(self._solver._n)]
            selector = lambda i: self.solution[i] * selection[i] + other.solution[i] * (not selection[i])

            ind = GeneticSolver.Individual([selector(i) for i in range(self._solver._n)], self._solver)

            return ind
        
        def mutate(self, probability: float = 0.01) -> None:
            '''
            Perform random mutation on this individual's chromosome
            Params:
                `probability`: (independent) probability of a gene changing
            '''
            for i in range(self._solver._n):
                if random.uniform(0, 1) > probability:
                    continue

                rs = random.randint(0, self._solver._n)

                if rs > self.num_sets:
                    self.num_sets += 1
                    rs = self.num_sets
                
                self.solution[i] = rs
        
        def swap_mutate(self, probability: float = 0.01) -> None:
            '''
            Perform swap mutation on this individual's chromosome. If a gene initiates mutation,
            the other gene is selected randomly from all genes in the chromosome (incl. the initiating gene)
            Params:
                `probability`: (independent) probability of a gene initiating a change
            '''
            for i in range(self._solver._n):
                if random.uniform(0, 1) > probability:
                    continue

                j = random.randrange(i, self._solver._n)
                
                self.solution[i], self.solution[j] = self.solution[j], self.solution[i]

        def recalculate(self) -> None:
            '''Perform the more expensive calculations needed for fitness estimation, etc.'''
            self.num_leftovers = self.solution.count(0)
            self.num_sets = max(self.solution)

            self.sums = [0] * self.num_sets
            for i in range(self._solver._n):
                if self.solution[i] == 0:
                    continue
                
                self.sums[self.solution[i] - 1] += self._solver.problem[i]
            
            self.fitness = self._solver.get_fitness(self)
        
        def get_dict(self) -> dict:
            return {a: str(getattr(self, a)) for a in self.__slots__ if a[0] != '_' and isinstance(getattr(self, a), (int, float, bool, list))}
        
        @staticmethod
        def make(sln: list, solver: 'GeneticSolver') -> 'GeneticSolver.Individual':
            ind = GeneticSolver.Individual(sln, solver)
            ind.recalculate()
            return ind

    class Logger:
        def __init__(self, metrics: list, interval: int = 1) -> None:
            self.series = {pn: [] for pn in metrics}
            self.generation = []
            self.initial = None
            self.solutions = {}
            self.interval = interval
        
        def log_initial(self, solver: 'GeneticSolver') -> None:
            self.initial = {k: v for k, v in solver.__dict__.items() if k[0] != '_' and isinstance(v, (int, float, bool))}
            self.initial['problem'] = solver.problem
        
        def log_metrics(self, generation: int, **kwargs) -> None:
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
        
        def save(self, path: str, mode: str = 'ims') -> None:
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
                    f.write("Saved solutions:\n")
                    for k, v in self.solutions.items():
                        f.write(f" {k}:\n")
                        for attr in v.__slots__:
                            if attr[0] != '_' and isinstance(getattr(v, attr), (int, float, bool, list)):
                                f.write(f"  {attr}: {str(getattr(v, attr))}\n")

                if 'm' in mode:
                    f.write("Tracked metrics:\n")
                    for k, v in self.series.items():
                        f.write(f" {k}: {str(v)}\n")

            if 'g' in mode:
                for k, v in self.series.items():
                    plt.figure()
                    plt.plot(self.generation, v)
                    plt.title(k)
                    plt.savefig(f"{path}/graph_{k}.png")
        
        def get_dict(self, mode: str = 'ims') -> dict:
            result = {'algorithm': 'genetic'}

            if 'i' in mode:
                result['parameters'] = self.initial
            
            if 'm' in mode:
                result['metrics'] = self.series
                result['metrics']['generation'] = self.generation
            
            if 's' in mode:
                result['solutions'] = {key: sln.get_dict() for key, sln in self.solutions.items()}
            
            return result

    def __init__(
            self,
            problem: list,
            T: int,
            pop_size: int,
            initial_pop: list = [],
            mating_ratio: float = 0.5,
            elitism_ratio: float = 0.1,
            mutation_rate: float = 0.01,
            swap_mutation_rate: float = 0.01,
            leftover_weight: float = 0.01,
            patience: int = 50,
            log_interval: int = 50,
            silent: bool = False) -> None:
        self.problem = problem
        self.T = T
        self.pop_size = pop_size
        self.mutation_rate = mutation_rate
        self.swap_mutation_rate = swap_mutation_rate
        self.leftover_weight = leftover_weight
        self.silent = silent

        self._logger = GeneticSolver.Logger(["best_fit", "avg_fit", "best_viable_fit"], interval=log_interval)

        assert mating_ratio + elitism_ratio < 1

        self.mating_pool_size = int(mating_ratio * pop_size)
        self.elite_size = int(elitism_ratio * pop_size)

        self._early_stop_counter = 0
        self.patience = patience

        self._n = len(problem)
        self._mean = mean(problem)
        self._stdev = stdev(problem)

        assert self._n > 0

        # dummy individual for comparisons only
        self._best_viable = GeneticSolver.Individual([], None)

        # initialize population
        self.population = [GeneticSolver.Individual.make(self._to_internal_repr(sln), self) for sln in initial_pop]
        self.population += [self._random_individual() for _ in range(pop_size - len(self.population))]
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        self.total_fitness = sum([sln.fitness for sln in self.population])

        self._logger.log_initial(self)

    def run(self, generations: int) -> None:
        with tqdm(range(generations), postfix={'best': self.population[0].fitness}, disable=self.silent) as progress_bar:
            for gen in progress_bar:
                self._early_stop_counter += 1
                if self._early_stop_counter >= self.patience and self.patience > 0:
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

                    if child.fitness > self._best_viable.fitness:
                        for s in child.sums:
                            if s != 0 and s != self.T:
                                break
                        else:
                            self._best_viable = child
                
                old_best = self.population[0].fitness

                self.population = new_generation
                self.population.sort(key=lambda x: x.fitness, reverse=True)
                
                if self.population[0].fitness > old_best:
                    self._early_stop_counter = 0
                    progress_bar.set_postfix(best=self.population[0].fitness)
                
                self._logger.log_metrics(
                    generation=gen,
                    best_fit=self.population[0].fitness,
                    avg_fit=self.total_fitness / self.pop_size,
                    best_viable_fit=self._best_viable.fitness
                )
        
        self._logger.log_solution("best", self.population[0])
        self._logger.log_solution("best_viable", self._best_viable)

    def get_fitness(self, individual: Individual) -> float:
        return 1 / (1 + sum(map(lambda x: (abs(self.T - x) / self._stdev) ** 2, individual.sums))
                     + self.leftover_weight * individual.num_leftovers / self._n)

    def get_solution(self, n: int = 0) -> list:
        '''
        Returns n-th best solution in common format
        Params:
            `n`: index of solution to return. 0 is best overall.
        '''
        sln = self.population[n]
        res = [[] for _ in range(sln.num_sets)]
        
        for i, v in enumerate(sln.solution):
            if v > 0:
                res[v - 1].append(self.problem[i])

        return [x for x in res if x != []]
    
    def get_result_dict(self, mode: str = 'ims') -> dict:
        return self._logger.get_dict(mode)
    
    def get_parameters(self) -> dict:
        return self._logger.initial

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
    
    def _to_internal_repr(self, sln: list) -> list:
        i_sln = [0] * self._n

        for setn, setv in enumerate(sln, 1):
            for p in setv:
                # find index of p in problem set
                p_idx = 0

                # in case we want to do a run with multiple occcurences of a number in problem set
                while p_idx < self._n:
                    p_idx = self.problem.index(p, p_idx)

                    if i_sln[p_idx] == 0:
                        i_sln[p_idx] = setn
                        break
        
        return i_sln

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    problem_group = parser.add_argument_group('problem')
    problem_group.add_argument('-T', type=int, default=600, help="Target subset sum")
    problem_group.add_argument('--g:s', '--generator_size',
        type=int,
        default=100,
        dest="generator_size",
        help="Size of problem set to generate",
        metavar="SIZE"
    )
    problem_group.add_argument('--g:m', '--generator_min',
        type=int,
        default=0,
        dest="generator_min",
        help="Min value in problem set",
        metavar="MIN"
    )
    problem_group.add_argument('--g:M', '--generator_max',
        type=int,
        default=100,
        dest="generator_max",
        help="Max value in problem set",
        metavar="MAX"
    )

    parser.add_argument('-g', '--generations',
        type=int,
        default=100000,
        dest="generations",
        help="Number of gnerations to simulate"
    )
    parser.add_argument('-s', '--pop_size',
        type=int,
        default=100,
        dest="pop_size",
        help="GA population size",
        metavar="SIZE"
    )
    parser.add_argument('--mating', type=float, default=0.5, dest="mating", help="Percentage of population to be considered for mating")
    parser.add_argument('-e', '--elitism',
        type=float,
        default=0.1,
        dest="elitism",
        help="Percentage of top performers to graduate to next generation, bypassing selection"
    )
    parser.add_argument('-m', '--mr', '--mutation_rate',
        type=float,
        default=0.03,
        dest="mr",
        help="Probability of a gene undergoing random mutation after crossover",
        metavar="RATE"
    )
    parser.add_argument('--smr', '--swap_mutation_rate',
        type=float,
        default=0.02,
        dest="smr",
        help="Probability of a gene swapping its value with a randomly chosen, different gene after crossover",
        metavar="RATE"
    )
    parser.add_argument('--lw', '--leftover_weight',
        type=float,
        default=0.01,
        dest="lw",
        help="Weight of the leftover ratio in the fitness function", metavar="WEIGHT"
    )
    parser.add_argument('-p', '--patience',
        type=int,
        default=10000,
        dest="patience",
        help="Number of generations with no improvement to best solution before early termination. 0 to disable"
    )

    logging_group = parser.add_argument_group('logging')
    logging_group.add_argument('-R', '--sr', '--save_results',
        action="store_true",
        dest="save_results",
        help="Whether a report should be generated"
    )
    logging_group.add_argument('--r:p', '--results_path',
        type=str,
        default='log/',
        dest="results_path",
        help="Path to save report at",
        metavar="PATH"
    )
    logging_group.add_argument('--r:m', '--results_mode',
        type=str,
        default='imgs',
        dest="results_mode",
        help="What to include in the generated report",
        metavar="MODE"
    )

    parser.add_argument('-i', '--init', '--initial_population',
        nargs="*",
        default=[],
        dest="init",
        help="Population initializers"
    )

    args = parser.parse_args()

    gen = Generator()
    greedy = GreedySolver(verbose=False)

    problem = gen.generate_random_set(
        args.generator_size,
        args.generator_min,
        args.generator_max
    )

    initial_population = []
    for word in args.init:
        tokens = word.split('/')
        if tokens[0] == 'greedy':
            param = tokens[1] if len(tokens) > 1 else 'desc'
            sln, _, _ = greedy.greedy_solution(problem, args.T, param)
            initial_population.append(sln)
        elif tokens[0] == 'grasp':
            grasp = GRASP(
                problem=problem,
                T=args.T,
                RCL_count=int(tokens[2]) if len(tokens) > 2 else 20,
                dropout_rate=float(tokens[3]) if len(tokens) > 3 else 0.5
            )
            grasp.perform_GRASP(int(tokens[1]) if len(tokens) > 1 else 100)

    gs = GeneticSolver(
        problem,
        T=args.T,
        pop_size=args.pop_size,
        initial_pop=initial_population,
        patience=args.patience,
        mating_ratio=args.mating,
        elitism_ratio=args.elitism,
        mutation_rate=args.mr,
        swap_mutation_rate=args.smr,
        leftover_weight=args.lw
    )

    gs.run(args.generations)
    print("Square distances from T:", list(map(lambda x: abs(gs.T - x) ** 2, gs.population[0].sums)))
    print(gs.population[0].solution)
    best = gs.get_solution()
    print("Best solution:", best, ", score:", gs.population[0].num_leftovers / gs._n)
    if args.save_results:
       gs._logger.save(args.results_path, mode=args.results_mode)
