import random
from typing import List
import numpy as np

class Generator:
    '''Problem generator'''

    def __init__(self) -> None:
        pass
    
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
        '''Generate set that has solution. 
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


if __name__ == '__main__':
    s = Generator().generate_set_with_guaranteed_solution(20, 45, 30)
    print(f'Generated set with {len(s)} elements: {s}')