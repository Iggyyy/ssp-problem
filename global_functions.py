from typing import List, Tuple
import random


def create_all_posible_subsets_from_set(set) -> Tuple[int, List[List[int]]]:
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

def check_if_all_sets_sum_to_T(list_of_sets, T) -> bool:
    for set in list_of_sets:
        if sum(set) != T:
            return False
    return True

def are_overlapping(list_of_sets) -> bool:
    '''Check if two sets are overlapping. O(n^4). Can be easily optimized to reduce complexity.'''
    for i in range(len(list_of_sets)):
        for item in list_of_sets[i]:
            for j in range(i+1, len(list_of_sets)):
                if item in list_of_sets[j]:
                    return True
    return False

def filter_sets_by_sum_T(list_of_sets, T) -> List[List[int]]:
    '''Filter list of sets to leave only those who sum up to T.'''
    return list(filter(lambda x: sum(x) == T ,list_of_sets))


if __name__ == '__main__':

    #Test overlapping
    print(are_overlapping([ [random.randint(0, 150) for i in range(12)] for _ in range(10000)  ]))

    #Test filtering
    print(filter_sets_by_sum_T([[1,2,3], [2,2,2], [1,1,1], [5,5,5]], 6))