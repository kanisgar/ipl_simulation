import pandas as pd
from collections import defaultdict

# Load your all.csv
df = pd.read_csv("all.csv")

# Group by Simulation Number
simulation_groups = df.groupby("Simulation Number")

# Create a dictionary where key = tuple of match results, value = list of simulation numbers with that result
result_map = defaultdict(list)

for sim_number, group in simulation_groups:
    results = tuple(group["Winner"].tolist())  # tuple ensures order
    result_map[results].append(sim_number)

# Count total duplicate simulations (excluding the first occurrence in each group)
duplicate_sim_count = sum(len(sims) - 1 for sims in result_map.values() if len(sims) > 1)

# Number of unique sets that were duplicated
distinct_duplicates = sum(1 for sims in result_map.values() if len(sims) > 1)

print(f"Total simulations: {len(simulation_groups)}")
print(f"Duplicated simulations (excluding firsts): {duplicate_sim_count}")
print(f"Number of distinct result sets that were duplicated: {distinct_duplicates}")
print("Total unique result sets:", len(result_map))