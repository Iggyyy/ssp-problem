#My proposition of a greedy approach
from global_functions import create_all_posible_subsets_from_set, check_if_all_sets_sum_to_T, are_overlapping
from typing import List, Tuple
from generator import Generator


class Pair:
    def __init__(self) -> None:
        self.elements = []
        self.sum = 0

class GreedySolver:
    '''Greedy solver running in O(n^2) time, but loses on solution quality (to be measured/defined).'''

    def basic_quadratic_greedy_solution(self, start_set, T) -> Tuple[int, List[List[int]]]:
        '''Generate basic greedy solution in O(nlogn) time.'''
        solution_pretenders= list()
        start_set.sort(reverse=True)

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
        for pretender in solution_pretenders:
            if pretender.sum == T:
                solution.append(pretender.elements)

        print(f'Found solution with {len(solution)} subsets: {solution}')
        return solution


if __name__ == '__main__':
    set = Generator().generate_multiset(15, 0, 5)
    print(f'Generated set {set}')
    solution = GreedySolver().basic_quadratic_greedy_solution(set, 8)
                    
            

