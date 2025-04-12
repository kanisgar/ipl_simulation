import pandas as pd
import random
from collections import defaultdict
import time

# Load data from CSV file
def load_data(file_path):
    df = pd.read_csv(file_path)
    upcoming_matches = df[df['Result'].isnull()]
    points_table = {
        'Kolkata Knight Riders': 0,
        'Royal Challengers Bengaluru': 0,
        'Delhi Capitals': 0,
        'Mumbai Indians': 0,
        'Chennai Super Kings': 0,
        'Rajasthan Royals': 0,
        'Sunrisers Hyderabad': 0,
        'Punjab Kings': 0,
        'Lucknow Super Giants': 0,
        'Gujarat Titans': 0,
    }

    # Add points from completed matches
    completed_matches = df[df['Result'].notnull()]
    for _, match in completed_matches.iterrows():
        result = match['Result']
        if result in points_table:
            points_table[result] += 2  # Each win = 2 points

    return upcoming_matches, points_table


# Simulate one full tournament
def simulate_tournament(matches, base_points):
    points = base_points.copy()
    for _, match in matches.iterrows():
        home_team = match['Home Team']
        away_team = match['Away Team']
        winner = random.choice([home_team, away_team])
        if winner in points:
            points[winner] += 2
    return points


# Run Monte Carlo simulations
def run_monte_carlo(matches, base_points, qualifying_points, simulations=50000):
    qualification_counts = defaultdict(int)

    for _ in range(simulations):
        sim_points = simulate_tournament(matches, base_points)
        for team, pts in sim_points.items():
            if pts >= qualifying_points:
                qualification_counts[team] += 1

    qualification_percentages = {
        team: round((count / simulations) * 100, 2)
        for team, count in qualification_counts.items()
    }

    # Ensure all teams are present in result
    for team in base_points:
        qualification_percentages.setdefault(team, 0.0)

    return qualification_percentages


# Main entry point
def main():
    file_path = "/Users/kanisgar/Documents/ipl_simulation/ipl_2025_schedule.csv"
    qualifying_points = int(input("Enter the qualifying points (e.g., 16): "))
    simulations = int(input("Enter the number of simulations: "))

    matches, base_points = load_data(file_path)

    print(f"\nRunning {simulations:,} tournament simulations... Please wait.\n")
    start_time = time.time()

    result = run_monte_carlo(matches, base_points, qualifying_points, simulations)

    end_time = time.time()

    print("Qualification Probabilities (teams with ≥ {} points):".format(qualifying_points))
    for team, percentage in sorted(result.items(), key=lambda x: x[1], reverse=True):
        print(f"{team}: {percentage}%")

    print(f"\nCompleted in {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()
