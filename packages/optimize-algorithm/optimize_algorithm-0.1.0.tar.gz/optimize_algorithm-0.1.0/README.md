# PSO & ABC Optimizer: Comparative Analysis for Financial Optimization

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

> This repository contains reusable implementations of Particle Swarm Optimization (PSO) and Artificial Bee Colony (ABC) algorithms, along with a real-world case study in corporate financial allocation. Side-by-side comparison is provided for educational, research, and practical applications.

---

## Features

- Modular Python implementation of PSO and ABC metaheuristics
- Ready-to-use fitness/objective functions (including Rastrigin and financial cost minimization)
- Easy configuration: number of variables, bounds, iterations, etc.
- Visualizations: convergence curves, 2D particle/bee distribution plots
- Example scripts for rapid testing and benchmarking
- Professional documentation & code structure

---

## Project Structure

optimize_algorithm/
│
├── optimize_algorithm/
│   ├── __init__.py
│   ├── pso.py        
│   └── abc.py        
│
├── examples/
│   ├── testing_pso.py
│   └── testing_abc.py
│
├── README.md
├── setup.py
├── LICENSE
└── .gitignore


---

## Algorithms Overview

### Particle Swarm Optimization (PSO)

> Inspired by bird flocking, PSO explores solutions by updating each particle’s position using both individual and global experience. Suitable for continuous optimization and known for rapid convergence.

- [x] Inertia, cognitive, and social update rules
- [x] Easy parameter tuning (`w`, `c1`, `c2`)

### Artificial Bee Colony (ABC)

> Mimics the foraging behavior of bees. Solution updates come from employed bees (explore), onlooker bees (select via "waggle dance"), and scouts (random exploration). Excels at avoiding local optima in complex landscapes.

- [x] Employed, onlooker, scout bee phases
- [x] Adaptive exploration via abandonment and random scouts

---

## Case Study: Financial Allocation Problem

**Goal:**  
Minimize the total corporate expenditure (Marketing, Operational, Salary, Maintenance, Miscellaneous) with:
- Total ≤ 120,000,000
- Marketing ≥ 10,000,000

**Fitness Function Example:**
```python
def cost_function(x):
    ideal_total = 120_000_000
    total = np.sum(x)
    penalty = max(0, total - ideal_total)**2
    underfund_penalty = 0
    if x[0] < 10_000_000:
        underfund_penalty += (10_000_000 - x[0])**2
    return total + 0.1 * penalty + 0.05 * underfund_penalty


**Result Snapshot** 

| Algorithm | Best Fitness | Total Spent | Convergence Speed |
| --------- | ------------ | ----------- | ----------------- |
| PSO       | \~TBD        | \~TBD       | Fast              |
| ABC       | \~TBD        | \~TBD       | Explorative       |


- Both PSO and ABC reach strong feasible solutions.

- PSO typically converges faster; ABC better explores diverse solutions.


**Quickstart**
1. install dependencies
```python
pip install -r requirements.txt

2. run an example
```python
examples/testing_pso.py
examples/testing_abc.py

3. Test on Rastrigin function
```python
examples/testing_rastrigin.py


**References**

Karaboga, D. "An Idea Based on Honey Bee Swarm for Numerical Optimization", 2005

Kennedy, J., Eberhart, R. "Particle Swarm Optimization", 1995

Wikipedia: Artificial Bee Colony

Wikipedia: Particle Swarm Optimization

**License**
This project is licensed under the MIT License.

**Contributing**
Feel free to open issues, pull requests, or suggestions for new features and applications!

