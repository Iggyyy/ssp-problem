import random
from typing import List, Tuple
'''
The goal is to find whether multiset can be divided into N non-overlapping subsets, each of which sums to a given T.

If this is not possible, then algorithm should propose achievable number (closest to N) of non-overlapping subsets.
'''

class Generator:
    '''Problem generator'''

    def __init__(self) -> None:
        pass
    
    def gen_multiset(cls, size: int, low: int = 0, high: int = 100) -> List[int]:
        '''Generate multiset of integers in range [low:high].\n
        Return multiset.'''
        s = [random.randint(low, high) for i in range(size)]
        return s

class EasyNaiveSolver:
    '''Simplest approach solver.'''

    def naive_exponential_solution(cls, multiset, t) -> Tuple[int, List[List[int]]]:
        '''Check whether multiset contains any subset of integers that sums up to t.\n
        Return maximum number of subsets, list of subsets.'''



if __name__ == '__main__':
    multiset = Generator().gen_multiset(20,1,10)
    print("Generated multiset: ", multiset)

