## Opis:

Znaleźć niepuste i niezależne podzbiory, które muszą sumować się do danego T, zostawiając zarazem najmniej leftovers. Jeśli algorytm nie wykorzysta wszystkich elementów, to dostaje karę od ilości pozostawionych elementów. Kiedy kara jest inf to algorytm szuka rozwiązania pokrywającego cały zbiór.

***

## Kluczowe elementy

### generator.py
- generate_set_with_guaranteed_solution - generowanie problemu, który zawsze ma rozwiązanie
- generate_random_set - generowanie losowego problemu bez żadnych gwarancji

### calculate_penalty
obliczanie kary dla danego rozwiązania, kara to liczba leftovers/liczba wszystkich elementów

### GreedySolver
zachłanne rozwiązanie

### GRASP
implementacja podejścia grasp

### GeneticSolver
mplementacja genetycznego rozwiązania

### benchmark.py
skrypt do generowania wykresów

***
## GRASP approach
![](src/grasp.png)
