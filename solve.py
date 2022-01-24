from greedy_solver import GreedySolver
from GRASP import GRASP
from genetic_solver import GeneticSolver
import sys 
import json


try:
    json_name = sys.argv[1]

    if '.json' not in json_name:
        json_name += '.json'
except:
    print(f'You should provide json source file name like: test or test.json')
    exit(0)

try:
    algorithm_name = sys.argv[2]
except:
    print(f'You should provide algorithm name ["genetic", "grasp", "greedy"]')
    exit(0)


print(f'Json file: {json_name}')
print(f'Algorithm chosen: {algorithm_name}')

with open(json_name) as f:
    dic = json.load(f)
    print(dic)
    artifacts = {
        'results': list(), 
        'parameters': {}
        }

    for element in dic['problems']:
        problem = element['S']
        sumT = element['T']

        print(f'Problem{problem}\nSum to {sumT}')

        if 'grasp' in algorithm_name.lower():
            algorithm = GRASP(problem=problem, 
                T=sumT,
                dropout_rate=0.8,
                RCL_count=200,
                dropout_size=0.4,
                bootsrap_iters=10,
                iterations=100
                )
            algorithm.perform_GRASP()
            result = algorithm.get_result_dict()
            params = algorithm.get_parameters()
        elif 'genetic' in algorithm_name.lower():
            algorithm = GeneticSolver()
            #TODO add
        else:
            algorithm = GreedySolver()
            algorithm.greedy_solution(start_set=problem, T=sumT)
            

        artifacts['results'].append(result)
    
    artifacts['parameters'] = params

    with open(json_name[:-4] + '_results.json', 'w') as fwr: 
        json.dump(artifacts, fwr)
        print('Saved')
        
