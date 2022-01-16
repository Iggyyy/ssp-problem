from collections import defaultdict
import time
from generator import Generator 
import random
from GRASP import GRASP
from greedy_solver import GreedySolver
import matplotlib.pyplot as plt

random.seed(time.time())

ITERATIONS = 10
generator = Generator()
results = defaultdict(list)

for i in range(ITERATIONS):
    
    T = 6000
    problemset = generator.generate_random_set(1000, 0, 1200)
    
    grasp = GRASP(verbose=False, problem=problemset, T=T)
    grasp.perform_GRASP()
    results['GRASP'].append(grasp.get_best_achieved_score())

    greedy = GreedySolver(verbose=False)
    _, _, pen = greedy.greedy_solution(start_set=problemset, T=T, list_order='desc')
    results['Greedy'].append(pen)

fig= plt.figure()
labels = ['GRASP', 'Greedy']
averages = [sum(results[key])/len(results[key])  for key in labels]
plt.bar(labels, averages)
plt.xlabel('Algorithms')
plt.ylabel('Score (the lower the better)')
plt.title('Algorithm quality comparison')
plt.show()

print(labels, averages)