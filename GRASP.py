import random, time
from tabnanny import verbose
import sys
from typing import List
from generator import Generator
from greedy_solver import GreedySolver
from global_functions import calculate_penalty

random.seed(time.time())

class GRASP:
    '''GRASP approach implementation.'''

    def __init__(self, verbose: bool = False, problem: list = None, T: int = None, RCL_count: int = 5, dropout_rate: float = 0.2) -> None:
        '''
        Create GRASP base.  
        Params:  
            `verbose`: flag to indicate whether there should be any debug output  
            `problem`: problem set on which the GRASP should be performed. If not provided then problem will generate random 100 numbers in range 0-150  
            `T`: number to which all the sets should sum up. If not provided then default value is 250   
            `RCL_count`: used to determine how many candidate searches should algorithm perform in each iteration  
            `dropout_rate`: rate of random set dropout performed at the and of each iteration. At rate of (1-dropout_rate) dropout will be based on greedy approach    
        '''
        self.greedySolver = GreedySolver(verbose=False)
        self.generator = Generator()
        self.verbose = verbose
        self.RCLs_count = RCL_count
        self.score = 2e9
        self.dropout_rate = dropout_rate
        self.score_history = list()

        if problem != None:
            self.problem = problem
        else:
            self.problem = self.generator.generate_random_set(100, 0, 150)

        if T != None:
            self.T = T
        else:
            self.T = 250

        

    def find_base_solution(self) -> None:
        '''Find base greedy solution as a baseline'''
        s, l, p = self.greedySolver.greedy_solution(self.problem, self.T, 'desc')
        self.solution = s
        self.penalty = p
        self.leftovers = l
        self.evaluate_Solution()

    def perform_GRASP(self, iterations: int = 100) -> None:
        '''
        Perform GRASP.  
        Params:  
            `iterations`: number of GRASP search iterations
        '''
        self.find_base_solution()
        self.score_history.append(self.score)

        for i in range(iterations):
            self.i = i
            self.solution_dropout()
            self.create_RCL()
            self.perform_selection()
            self.evaluate_Solution()
            self.score_history.append(self.score)

        self.debug_message(f'Best found solution has score of {min(self.score_history)}')

    def create_RCL(self):
        '''Create Restricted Candidate List based on n random greedy searches'''
        best_candidates = None
        best_penalty = 2e9


        #Perform greedy search N times, save only candidate with lowest penalty
        for _ in range(self.RCLs_count):
            sets, _, pen = self.greedySolver.greedy_solution(self.leftovers, self.T, 'desc')

            if pen < best_penalty:
                best_penalty = pen 
                best_candidates = sets

        self.best_candidates = best_candidates

        if best_candidates == None:
            self.debug_message('Create RCL: No best candidates found')

    def perform_selection(self):
        '''Perform selection over list of best candidates'''
        best_candidate = None
        
        #Select the shortest candidate
        for candidate in self.best_candidates:
            if best_candidate == None or len(candidate) < len(best_candidate):
                best_candidate = candidate

        if best_candidate != None:
            self.solution.append(best_candidate)

            #Remove elements from lefotvers that are memebers of added set 
            for c in best_candidate:
                self.leftovers.remove(c)
        else:
            self.debug_message('Perform Selection: no best candidate found')


    def evaluate_Solution(self):
        '''Get penalty evaluation for current solution'''
        self.score = calculate_penalty(self.T, self.solution, self.leftovers)

    def solution_dropout(self):
        '''
        Perform dropout of one set from solution.\n   
        Selection in `dropout_rate` cases is based on the random choice, other times the longest set is chosen to be dropped.
        '''
        remove_index = None

        #Remove least promising (or randomly chosen with %chance) set from solution
        if random.random() < self.dropout_rate:
            items = len(self.solution)
            remove_index = random.randint(0, items-1)
            
        #Remove constraint based, weakest element in solution
        else:
            worst_element = None 
            worst_idx = None
            for idx, set in enumerate(self.solution):
                if worst_element == None or len(set) > len(worst_element):
                    worst_element = set 
                    worst_idx = idx 

            remove_index = worst_idx
        
        if remove_index == None:
            self.debug_message('Solution dropout: No set to remove')
            return

        set_to_remove = self.solution[remove_index]

        #Add removed set to leftovers 
        for m in set_to_remove:
            self.leftovers.append(m)

        #Remove set from solution
        self.solution = self.solution[0:remove_index] + self.solution[remove_index+1:]
    
    def debug_message(self, message) -> None:
        '''Print message'''
        if self.verbose:
            print(message, file=sys.stderr)
            
    def get_solution(self) -> List[List[int]]:
        return self.solution 

    def get_solution_penalty(self) -> float:
        return self.penalty 

    def get_leftovers(self) -> List[int]:
        return self.leftovers

    def get_score_history(self) -> List[int]:
        return self.score_history

if __name__ == '__main__':
    grasp = GRASP(verbose=True)
    grasp.perform_GRASP(iterations=20)

    print('GRASP: ')
    print(f'Solution:\n{grasp.get_solution()}\nLeftovers:\n{grasp.get_leftovers()}\nScore:\n{grasp.get_solution_penalty()}\nScore history:\n{grasp.get_score_history()}')