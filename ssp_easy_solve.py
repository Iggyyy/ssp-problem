import random

class Generator:
    '''Problem generator class.'''

    def __init__(self) -> None:
        pass
    
    @classmethod
    def gen_multiset(self, size: int, low: int = 0, high: int = 100):
        '''Generate multiset of integers.'''
        s = [random.randint(low, high) for i in range(size)]
        return s

class EasyNaiveSolver:
    '''Simplest approach solver.'''

    @classmethod
    def has_any_solution(multiset, T):
        '''Check whether multiset contains any subset of integers that sums up to T.'''



if __name__ == '__main__':
    multiset = Generator.gen_multiset(20,0,5)
    print("Generated multiset: ", multiset)

