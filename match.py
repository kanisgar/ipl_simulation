import pandas as pd
from collections import defaultdict

# File paths (make sure to use raw strings)
actual_file = r'C:\Kani_Personal\Cricket_Study\ipl_simulation\ipl_2024_schedule.csv'
simulation_file = r'C:\Kani_Personal\Cricket_Study\ipl_simulation\all.csv'

# Load data
actual_df = pd.read_csv(actual_file)
simulation_df = pd.read_csv(simulation_file)

# Filter actual results from Match 56 onward and drop NA (results not yet filled)
actual_df = actual_df[actual_df['Match Number'] >= 56]
actual_df = actual_df.dropna(subset=['Result'])

# Build actual results mapping: "Home vs Away" => Winner
actual_results = {
    f"{row['Home Team']} vs {row['Away Team']}": row['Result']
    for _, row in actual_df.iterrows()
}

# Group simulations by simulation number
simulation_groups = simulation_df.groupby('Simulation Number')

matched_simulations = []

# Compare each simulation
for sim_number, sim_data in simulation_groups:
    total = 0
    correct = 0
    for _, row in sim_data.iterrows():
        match = row['Match'].strip()
        predicted_winner = row['Winner'].strip()

        # Exclude the matches with 'TIE' result from the actual data
        if match in actual_results and actual_results[match] != 'TIE':
            total += 1
            if actual_results[match] == predicted_winner:
                correct += 1

    if total > 0:
        match_percentage = (correct / total) * 100
        if match_percentage >= 95:
            matched_simulations.append((sim_number, match_percentage))

# Display matched simulations
if matched_simulations:
    print("Simulations with ≥ 70% match:")
    for sim_number, percent in matched_simulations:
        print(f"Simulation {sim_number}: {percent:.2f}% match")
else:
    print("No simulations matched ≥ 70% of actual results.")
