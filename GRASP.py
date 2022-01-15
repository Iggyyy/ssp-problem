import random, time
import sys
from typing import List
from generator import Generator
from greedy_solver import GreedySolver
from global_functions import calculate_penalty
import matplotlib.pyplot as plt

random.seed(time.time())

class GRASP:
    '''GRASP approach implementation.'''

    def __init__(self, verbose: bool = False, problem: list = None, T: int = None, RCL_count: int = 20, dropout_rate: float = 0.5) -> None:
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
        self.best_achieved_score = 2e9
        self.best_achieved_solution = list()

        if problem != None:
            self.problem = problem
        else:
            self.problem = self.generator.generate_random_set(1000, 0, 1200)

        if T != None:
            self.T = T
        else:
            self.T = 9000

        

    def find_base_solution(self) -> None:
        '''Find base greedy solution as a baseline'''
        s, l, p = self.greedySolver.greedy_solution(self.problem, self.T, 'desc')
        self.solution = s
        self.penalty = p
        self.leftovers = l
        self.evaluate_Solution()
        self.base_solution_quality = self.score

        self.debug_message(f'Base greedy solution: {self.score}')

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

            if self.best_achieved_score > self.score:
                self.best_achieved_score = self.score
                self.best_achieved_solution = self.solution

        self.debug_message(f'Best found solution has score of {min(self.score_history)}')

    def create_RCL(self):
        '''Create Restricted Candidate List based on n random greedy searches'''
        best_candidates = None
        best_penalty = 2e9


        #Perform greedy search N times, save only candidate with lowest penalty
        for _ in range(self.RCLs_count):
            if(random.random() < 0.2):
                approach = 'random'
            else:
                approach = 'desc'
            sets, _, pen = self.greedySolver.greedy_solution(self.leftovers, self.T, approach)

            if pen < best_penalty:
                best_penalty = pen 
                best_candidates = sets

        self.best_candidates = best_candidates

        if best_candidates == None:
            self.debug_message('Create RCL: No best candidates found')

    def perform_selection(self):
        '''Perform selection over list of best candidates'''
        best_candidate = None
        
        #add best candidates to solution
        for candidate in self.best_candidates:
            if best_candidate == None or len(candidate) < len(best_candidate):
                best_candidate = candidate
            
            self.solution.append(candidate)

            #Remove elements from lefotvers that are memebers of added set 
            for c in candidate:
                self.leftovers.remove(c)

        # if best_candidate != None:
        #     self.solution.append(best_candidate)

        #     #Remove elements from lefotvers that are memebers of added set 
        #     for c in best_candidate:
        #         self.leftovers.remove(c)
        # else:
        #     self.debug_message('Perform Selection: no best candidate found')


    def evaluate_Solution(self):
        '''Get penalty evaluation for current solution'''
        self.score = calculate_penalty(self.T, self.solution, self.leftovers)

    def solution_dropout(self):
        '''
        Perform dropout of one set from solution.\n   
        Selection in `dropout_rate` cases is based on the random choice, other times the longest set is chosen to be dropped.
        '''
        remove_index = list()
        dropout_items_cnt =1 #max(int(0.3 * len(self.solution)), 0)

        #Remove least promising (or randomly chosen with %chance) set from solution
        if random.random() < self.dropout_rate:
            items = len(self.solution)
            if items == 0:
                self.debug_message(f'{self.i}, {self.solution}')
                return
            remove_index.append(random.randint(0, items-1))
            
        #Remove constraint based, weakest element in solution
        else:
            for _ in range(dropout_items_cnt):
                longest_element = None 
                longest_idx = None
                shortest_element = None
                shortest_idx = None
                for idx, set in enumerate(self.solution):
                    if (longest_element == None or len(set) > len(longest_element)) and idx not in remove_index:
                        longest_element = set 
                        longest_idx = idx 

                    if (shortest_element == None or len(set) < len(shortest_element)) and idx not in remove_index:
                        shortest_element = set 
                        shortest_idx = idx 

                if longest_idx != None:
                    remove_index.append(longest_idx)
                if shortest_idx != None:
                    remove_index.append(shortest_idx)
        
        if len(remove_index) == 0:
            self.debug_message('Solution dropout: No set to remove')
            return

        for remov_idx in remove_index:
            set_to_remove = self.solution[remov_idx]

            #Add removed set to leftovers 
            for m in set_to_remove:
                self.leftovers.append(m)

            #Remove set from solution
            #self.solution[0:remov_idx] + self.solution[remov_idx+1:]
        
        new_solution = list()
        for idx, set in enumerate(self.solution):
            if idx not in remove_index:
                new_solution.append(set)
        self.solution = new_solution
        #print(self.solution)

    
    def debug_message(self, message) -> None:
        '''Print message'''
        if self.verbose:
            print(message, file=sys.stderr)
            
    def get_solution(self) -> List[List[int]]:
        return self.solution 

    def get_solution_penalty(self) -> float:
        return self.score 

    def get_leftovers(self) -> List[int]:
        return self.leftovers

    def get_score_history(self) -> List[int]:
        return self.score_history

    def get_greedy_basic_score(self) -> float:
        return self.base_solution_quality

    def get_best_achieved_score(self) -> float:
        return self.best_achieved_score

if __name__ == '__main__':
    grasp = GRASP(verbose=True, dropout_rate=0.8, RCL_count=50)
    grasp.perform_GRASP(iterations=200)

    print('GRASP: ')
    print(f'Solution:\n{grasp.get_solution()}\nLeftovers:\n{grasp.get_leftovers()}\nScore:\n{grasp.get_solution_penalty()}\nScore history:\n{grasp.get_score_history()}')

    plt.plot(grasp.get_score_history())
    plt.show()
