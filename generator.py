import random
from typing import List
import numpy as np

class Generator:
    '''Problem generator'''

    def __init__(self) -> None:
        self.possible_subsets = []
    
    def generate_random_set(self, size: int, low: int = 0, high: int = 100) -> List[int]:
        '''Generate set of unique integers in range [low:high].\n
        Return set.'''
        assert high-low >= size, 'Range should be equal or greater than set size'
        assert high>low, 'Upper bound should be greater than lower bound'
        s = random.sample(range(low,high), size) 
        return s
    
    def generate_random_multiset(self, size: int, low: int = 0, high: int = 100) -> List[int]:
        '''Generate multiset of integers in range [low:high].\n
        Return set.'''
        assert high>low, 'Upper bound should be greater than lower bound'
        s = [random.randint(low,high) for _ in range(size)]
        return s

    def generate_set_with_guaranteed_solution(self, size: int, T: int, max_num: int) -> List[int]:
        '''DO NOT USE, POSSIBLE TO GET STUCK. Generate set that has solution of approx size. 
        This is a greedy algorithm that allows little extensions of size and max_num after a size^3 iterations.
        To easily generate '''
        ints = [i for i in range(0, max_num+1)]
        random.shuffle(ints)
        ints = np.array(ints)
        set = []
        original_size = size

        tmp_sum = 0
        tmp_set = []
        iteration = 0
        while len(set) < size:
            indexes_to_remove = []
            found = False
            #find subset
            for i, num in enumerate(ints):
                if num < T and sum(tmp_set) + num <= T:
                    tmp_set.append(num)
                    tmp_sum += num
                    indexes_to_remove.append(i)

                    if tmp_sum == T and len(set) + len(tmp_set) <= size:
                        set += tmp_set
                        tmp_sum = 0
                        tmp_set = []
                        found = True

            if found:
                #remove indexes
                ints = np.delete(ints, indexes_to_remove)

            #shufle and extend to avoid local minimum
            np.random.shuffle(ints)
            tmp_sum = 0
            tmp_set = []

            #stop searching for proper sets if it takes too long
            if iteration > 2*original_size**2:
                return set
            
            #increase limits by relaxing contraints
            if iteration > original_size**2:
                if max_num <= T:
                    max_num+=1
                    ints = np.append(ints, [max_num])
                size+=1

            iteration+=1

        return set

    def __gen_subsets_that_sum_to_T(self, numbers, T, partial=[]):
        '''Generate all possible subsets from [numbers] with sum of T.'''
        s = sum(partial)
        #Check if partial sum equals T
        if s == T: 
            self.possible_subsets.append(partial)

        #Stop if the T is reached
        if s >= T:
            return
        
        for i in range(len(numbers)):
            n = numbers[i]
            remaining = numbers[i+1:]
            self.__gen_subsets_that_sum_to_T(remaining, T, partial + [n]) 

    def generate_proceural_guaranteed_solution(self, T, dropout=.3, numbers=[]) -> List[int]:
        '''Generate set of integers with subsets that sum of T.'''

        #Generate all subsets with sum of T. If numbers list is not passed then create list of numbers in range 0-T with given dropout rate
        self.__gen_subsets_that_sum_to_T(
            numbers if len(numbers)>0 else list(filter(lambda _: random.random() > dropout ,[i for i in range(0, T)])), 
            T
            )

        #Reference array to mark taken elements 
        solution = [0 for i in range(0, T)]

        for subset in self.possible_subsets:
            #Check if all numbers are not overlapping with those already taken
            all = True
            for num in subset:
                if solution[num] == 1:
                    all = False

            #Chance to drop subset in order to achieve more randomness in generated solution
            if random.random() < dropout:
                all = False

            #Add subset to solution
            if all:
                for num in subset:
                    solution[num] = 1

        #Change indexes into numbers
        ret = []
        for num, flag in enumerate(solution):
            if flag == 1:
                ret.append(num)

        print(f'Generated set with non-overlapping subset with sum of {T}: {set}')
        return ret


if __name__ == '__main__':
    set = Generator().generate_proceural_guaranteed_solution(45)
    print(set)