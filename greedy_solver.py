#My proposition of a greedy approach
from global_functions import create_all_posible_subsets_from_set, check_if_all_sets_sum_to_T, are_overlapping, calculate_penalty
from typing import List, Tuple
from generator import Generator
import random
import numpy as np
import time

random.seed(time.time())


class Pair:
    def __init__(self) -> None:
        self.elements = []
        self.sum = 0

class GreedySolver:
    '''Greedy solver running in O(n^2) time.'''

    def __init__(self, verbose:bool=True) -> None:
        self.verbose = verbose

    def greedy_solution(self, start_set:list, T:int, list_order:str='desc') -> Tuple[List[List[int]], List[int], float]:
        '''Generate basic greedy solution in O(n^2) time.\n
        Return: \n
        Solution: List of solution sets\n
        Leftovers: List of leftovers\n
        Penalty: Quailty measure of solution'''
        solution_pretenders= list()

        #Apply selected order to list
        if list_order == 'desc':
            start_set.sort(reverse=True)
        elif list_order == 'asc':
            start_set.sort()
        elif list_order == 'rand':
            random.shuffle(start_set)

        #Build solution by greedy approach
        for el in start_set:
            found = False
            for pretender in solution_pretenders:
                #Check if element will fit, if yes then add it to pretender
                if pretender.sum < T and pretender.sum + el <= T:
                    pretender.elements.append(el)
                    pretender.sum += el 
                    found = True
                    break
            if found == False:
                solution_pretenders.append(Pair())
                
        #Gather solution and leftovers from built structure
        solution = list()    
        leftovers = list()
        for pretender in solution_pretenders:
            if pretender.sum == T:
                solution.append(pretender.elements)
            else:
                leftovers += pretender.elements

        #Get quality evaluation
        penalty = calculate_penalty(T, solution, leftovers)

        #Print solution parameters
        if self.verbose == True:
            s = f'Solution penalty {penalty:.2f}\n'
            s += f'local search approach {list_order}\n'
            s += f'{len(solution)} subsets: {solution}\n'
            s += f'{len(leftovers)} leftovers: {leftovers}\n' 
            print(s)

        return solution, leftovers, penalty


if __name__ == '__main__':
    T = random.randint(350, 400)
    generator = Generator()
    #set = generator.generate_proceural_guaranteed_solution(T)
    set = generator.generate_random_set(100, 0, 200)
    print(f'Generated set {set}')

    compare = ['asc', 'desc', 'rand']
    greedySolver = GreedySolver() 

    for order in compare:
        solution, leftovers, penalty = greedySolver.greedy_solution(set, T, list_order=order)
                    
            

