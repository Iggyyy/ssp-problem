import random
from typing import List

class Generator:
    '''Problem generator'''

    def __init__(self) -> None:
        pass
    
    def generate_set(cls, size: int, low: int = 0, high: int = 100) -> List[int]:
        '''Generate set of unique integers in range [low:high].\n
        Return set.'''
        assert high-low >= size, 'Range should be equal or greater than set size'
        assert high>low, 'Upper bound should be greater than lower bound'
        s = random.sample(range(low,high), size) 
        return s
    
    def generate_multiset(cls, size: int, low: int = 0, high: int = 100) -> List[int]:
        '''Generate multiset of integers in range [low:high].\n
        Return set.'''
        assert high>low, 'Upper bound should be greater than lower bound'
        s = [random.randint(low,high) for _ in range(size)]
        return s
