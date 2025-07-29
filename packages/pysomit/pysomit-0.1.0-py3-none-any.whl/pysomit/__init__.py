# pysomit/__init__.py

import numpy as np
from fractions import Fraction
from scipy.optimize import minimize

# ----- Part I -----
def somit_i():
    n = int(input("\nHow many criteria (or subcriteria) do you want to compare? "))
    print(f"You have {n} criteria. Numbered 1 through {n}.")
    
    # Step 1. Median criterion selection
    while True:
        sel = input(f"->Which criterion (1–{n}) you think is the median level of importance? ")
        try:
            median_idx = int(sel) - 1
            if 0 <= median_idx < n:
                break
        except ValueError:
            pass
        print(f"Please enter an integer between 1 and {n}.")
    print(f"--You chose criterion #{median_idx+1} as the median.")

    # Step 2. Comparisons vs median
    print("\nEnter importance of each criterion relative to the median.")

    comparisons = [None] * n
    comparisons[median_idx] = 1.0

    for j in range(n):
        if j == median_idx:
            continue
        while True:
            val = input(f"Compare Criterion #{j+1} with #{median_idx+1}: ")
            try:
                x = float(Fraction(val)) if '/' in val else float(val)
                comparisons[j] = x
                break
            except (ValueError, ZeroDivisionError):
                print("Please enter a valid decimal or fraction (e.g., 0.333 or 1/3)")

    # Step 3. Highest vs lowest relative to median
    vals = [(i, comparisons[i]) for i in range(n) if i != median_idx]
    h_idx = max(vals, key=lambda x: x[1])[0]
    l_idx = min(vals, key=lambda x: x[1])[0]
    print(f"\nHighest: criterion #{h_idx+1} ({comparisons[h_idx]}); Lowest: criterion #{l_idx+1} ({comparisons[l_idx]})")

    while True:
        val = input(f"Compare Criterion #{h_idx+1} with #{l_idx+1}: ")
        try:
            ahl = float(Fraction(val)) if '/' in val else float(val)
            break
        except (ValueError, ZeroDivisionError):
            print("Please enter a valid decimal or fraction (e.g., 0.333 or 1/3)")

    print(f" a_hl = {ahl}\n")

    # Step 4. Formulate and solve the optimization problem
    # Build list of assigned pairs A = [(i,j,a_ij), ...]
    A = []
    # Pairs from Step 2: criterion j vs median
    for j, a in enumerate(comparisons):
        if j == median_idx:
            continue
        A.append((j, median_idx, a)) # a_{j,median}

    # Pair from step 3: highest vs lowest
    A.append((h_idx, l_idx, ahl))

    # Objective: z(w) = sum_{(i,j) in A} (a_ij * w[j] - w[i])^2
    def objective(w):
        z = 0.0
        for i, j, aij in A:
            z += (aij * w[j] - w[i])**2
        return z

    # Constraints:
    # 1) sum(w) = 1
    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1},)
    # 2) bounds 0 <= w_i <= 1
    bounds = [(0.0, 1.0)] * n
    # Initial guess: uniform
    w0 = np.full(n, 1.0/n)

    # Solve with SciPy
    res = minimize(objective, w0, bounds=bounds, constraints=cons)

    if res.success:
        weights = res.x
        print("Optimal subjective weights (w^s):")
        for idx, val in enumerate(weights):
            print(f"  w^s_{idx+1} = {val:.4f}")
        print(f"Objective value z = {res.fun:.6f}")
    else:
        print("Optimization failed:", res.message)

    return weights

# ----- Part II -----
def somit_ii(ACM):
    m, n = ACM.shape

    # Step 5: normalization 
    f_min = ACM.min(axis=0)
    f_max = ACM.max(axis=0)
    denom = f_max - f_min

    # avoid division by zero if a column is constant
    denom[denom == 0] = 1.0

    # broadcast subtraction/division
    F = (ACM - f_min) / denom 

    # Step 6: median and AADM r_j ---
    medians = np.median(F, axis=0)
    r = np.mean(np.abs(F - medians), axis=0)

    # Step 7: objective weights w^o_j ---
    w_o = r / np.sum(r)

    # print results for development
    # print("Normalized ACM (F):\n", np.round(F, 4))
    # print("\nMedians:\n", np.round(medians, 4))
    # print("\nAADM r_j:\n", np.round(r, 4))
    print("\nObjective weights w^o_j:\n", np.round(w_o, 4))

    return w_o

# ----- Part III -----
def somit_iii(w_s: np.ndarray, w_o: np.ndarray) -> np.ndarray:
    w_s = np.asarray(w_s, dtype=float)
    w_o = np.asarray(w_o, dtype=float)
    if w_s.shape != w_o.shape:
        raise ValueError("w_s and w_o must have the same shape")
    prod = w_s * w_o
    total = prod.sum()
    final_weights = prod / total
    return final_weights