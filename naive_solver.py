import  numpy as np
from typing import List, Tuple
from generator import Generator
'''
The goal is to find whether set can be divided into N non-overlapping subsets, each of which sums to a given T.

If this is not possible, then algorithm should propose achievable number (closest to N) of non-overlapping subsets.
'''
T = 6
HIGH = 10
LOW = 1
SET_LEN = 4


class NaiveSolver:
    '''Naive approach solver. Finds optimum in O(2^(2^n-1))time.'''

    def naive_exponential_solution(self, start_set, T) -> Tuple[int, List[List[int]]]:
        '''Check whether set contains any subset of integers that sums up to t.\n
        Return maximum number of subsets, list of subsets.'''

        #Generate all possible subsets and check their sums
        n, sets = self.create_all_posible_subsets_from_set(start_set)
        print('Number of unique subsets:', n)

        #Variables with best solution
        highest_number_of_valid_subsets = -1
        best_set_of_subsets = list()

        iters = 2**len(sets)
        print(f'Naive algorithm has to perform {iters} iterations [2^(number_of_subsets)]')
        #Validate all possible subsets
        for i in range(1, iters):
            mask = bin(i)[2:]
            mask = '0'*(len(sets) - len(mask)) + mask
            local_list_of_sets = list(map(lambda x: x[1], filter(lambda x: x[0] == '1', zip(mask, sets))))

            #Check if subsets non-overlap and sum to T, then if solution is better than previous, save
            if self.are_overlapping(local_list_of_sets) == False and self.check_if_all_sets_sum_to_T(local_list_of_sets, T) == True:
                
                if highest_number_of_valid_subsets < len(local_list_of_sets):
                    highest_number_of_valid_subsets = len(local_list_of_sets)
                    best_set_of_subsets = local_list_of_sets

            if i % 1000000 == 0:
                print(f'Iteration nr. {i//1000000}M')

        if highest_number_of_valid_subsets == -1:
            print(f'There is no any subsets that sum to {T}.')
        else:
            print(f'Found solution with {highest_number_of_valid_subsets} subsets, each of which sums up to {T}\n \
                List of found subsets: {best_set_of_subsets}')
       

    def create_all_posible_subsets_from_set(self, set) -> Tuple[int, List[List[int]]]:
        '''Generate all (non-empty) possible subsets for a given set.\n
        Retrun number of subsets, list of subsets.'''
        all_subsets = list() 
        for i in range(0, int('0b'+'1'*len(set), 2)+1):
            mask = bin(i)[2:]
            mask = '0'*(len(set) - len(mask)) + mask
            subset = list(map(lambda x: x[1], filter(lambda x: x[0] == '1', zip(mask, set))))
            if len(subset) > 0:
                all_subsets.append(subset)
        return len(all_subsets), all_subsets
    
    def check_if_all_sets_sum_to_T(self, list_of_sets, T) -> bool:
        for set in list_of_sets:
            if sum(set) != T:
                return False
        return True

    def are_overlapping(self, list_of_sets) -> bool:
        for i in range(len(list_of_sets)):
            for item in list_of_sets[i]:
                for j in range(i+1, len(list_of_sets)):
                    if item in list_of_sets[j]:
                        return True
        return False


    


if __name__ == '__main__':


    set = Generator().generate_set(SET_LEN,LOW,HIGH)
    print("Generated set: ", set)

    NaiveSolver().naive_exponential_solution(set, T)

    #print( NaiveSolver().are_overlapping([  [1, 2, 3], [4,5,6], [12,14,7], [77] ]))
    

