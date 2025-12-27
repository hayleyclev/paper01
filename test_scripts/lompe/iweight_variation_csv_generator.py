import numpy as np
import itertools
import pandas as pd

# Define instrument names
instruments = ["sd_kod", "pfisr", "super_mag", "swarm_mag", "swarm_tii"]

# Step 1: Gather user input for each instrument
weight_ranges = {}
for instr in instruments:
    min_val = float(input(f"Enter minimum weight for {instr} (e.g., 0.1): "))
    max_val = float(input(f"Enter maximum weight for {instr} (e.g., 1.0): "))
    if min_val > max_val or min_val < 0.1 or max_val > 1.0:
        raise ValueError(f"Invalid range for {instr}: {min_val}–{max_val}")
    weight_ranges[instr] = np.round(np.arange(min_val, max_val + 0.01, 0.1), 1)

# Step 2: Generate all combinations
all_combinations = list(itertools.product(*weight_ranges.values()))

# Step 3: Create a DataFrame
df = pd.DataFrame(all_combinations, columns=instruments)

# Step 4: Save to CSV
output_filename = "/Users/clevenger/Projects/paper01/events/20230227/lompe/iweight_sensitivity_test/weight_combinations.csv"
df.to_csv(output_filename, index=False)
print(f"\nGenerated {len(df)} combinations.")
print(f"Saved to {output_filename}")
