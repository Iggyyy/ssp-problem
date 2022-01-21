from collections import defaultdict
import time
from generator import Generator 
import random
from GRASP import GRASP
from greedy_solver import GreedySolver
import matplotlib.pyplot as plt

random.seed(time.time())

TARR = [50000, 100000, 150000, 200000, 250000] 
ITERATIONS = len(TARR)
generator = Generator()
results = defaultdict(list)

for i, T in enumerate(TARR):
    problemset = generator.generate_random_set(size=10000, low=0, high=20000)
    
    grasp = GRASP(verbose=False, problem=problemset, T=T)
    grasp.perform_GRASP(15)
    results['GRASP'].append(grasp.get_best_achieved_score())

    greedy = GreedySolver(verbose=False)
    _, _, pen = greedy.greedy_solution(start_set=problemset, T=T, list_order='desc')
    results['Greedy'].append(pen)

fig= plt.figure()
labels = ['GRASP', 'Greedy']
averages = [sum(results[key])/len(results[key]) for key in labels]
plt.bar(labels, averages)
plt.xlabel('Algorithms')
plt.ylabel('Score (the lower the better)')
plt.title('Algorithm quality comparison')
plt.show()

print(labels, averages)