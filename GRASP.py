import random, time
from typing import List
from generator import Generator
from greedy_solver import GreedySolver
from global_functions import calculate_penalty

random.seed(time.time())

class GRASP:
    '''GRASP approach implementation.'''

    def __init__(self, verbose:bool=False, problem:list=None, T:int=None) -> None:
        self.greedySolver = GreedySolver(verbose=verbose)
        self.generator = Generator()
        self.verbose = verbose

        if problem != None:
            self.problem = problem
        else:
            self.problem = self.generator.generate_random_set(100, 0, 150)

        if T != None:
            self.T = T
        else:
            self.T = 250

        self.find_base_solution()

    def find_base_solution(self) -> None:
        s, l, p = self.greedySolver.greedy_solution(self.problem, self.T, 'random')
        self.solution = s
        self.penalty = p
        self.leftovers = l

    def create_RCL(self):
        pass

    def perform_selection(self):
        pass 

    def evaluate_Solution(self):
        pass 

    def solution_dropout(self):
        pass 

    def get_solution(self) -> List[List[int]]:
        return self.solution 

    def get_solution_penalty(self) -> float:
        return self.penalty 

    def get_leftovers(self) -> List[int]:
        return self.leftovers