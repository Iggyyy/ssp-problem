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
    '''Greedy solver running in O(n^2) time, but loses on solution quality (to be measured/defined).'''
    #TODO fix this -> solution should cover all elements??
    def basic_quadratic_greedy_solution(self, start_set, T, list_order='desc') -> Tuple[int, List[List[int]]]:
        '''Generate basic greedy solution in O(n^2) time.'''
        solution_pretenders= list()

        if list_order == 'desc':
            start_set.sort(reverse=True)
        elif list_order == 'asc':
            start_set.sort()
        elif list_order == 'rand':
            random.shuffle(start_set)

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
                

        solution = list()    
        leftovers = list()
        for pretender in solution_pretenders:
            if pretender.sum == T:
                solution.append(pretender.elements)
            else:
                leftovers += pretender.elements

        print(f'Found solution with penalty {calculate_penalty(T, solution, leftovers):.2f}, \
            {len(leftovers)} leftovers: {leftovers} and {len(solution)} \
            subsets: {solution}. \
            List order {list_order}'
            )
        return solution


if __name__ == '__main__':
    T = random.randint(50, 70)
    generator = Generator()
    set = generator.generate_proceural_guaranteed_solution(T)
    print(f'Generated set {set}')

    compare = ['asc', 'desc', 'rand']
    for order in compare:
        solution = GreedySolver().basic_quadratic_greedy_solution(set, T, list_order=order)
                    
            

