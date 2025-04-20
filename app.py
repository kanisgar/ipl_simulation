import pandas as pd
import random
from collections import defaultdict
import time
import csv
import json
from tabulate import tabulate
from itertools import product

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
    completed_matches = df[df['Result'].notnull()]
    for _, match in completed_matches.iterrows():
        result = match['Result']
        if result == 'TIE':
            points_table[match['Home Team']] += 1
            points_table[match['Away Team']] += 1
        elif result in points_table:
            points_table[result] += 2
    # Save current points table to JSON file
    sorted_points = dict(sorted(points_table.items(), key=lambda x: x[1], reverse=True))
    with open('current_points_table.json', 'w') as f:
        json.dump(sorted_points, f, indent=4)
    print("Current points table saved to current_points_table.json")
    if upcoming_matches.empty:
        print("No matches left for simulating.")
        return None, None
    return upcoming_matches, points_table

# Simulate using all combinations (if match count is low)
def run_all_combinations(matches, base_points, qualifying_points):
    qualification_counts = defaultdict(int)
    team_scenarios = defaultdict(list)

    match_list = list(matches.iterrows())
    total_combinations = 2 ** len(match_list)

    print(f"Total possible combinations: {total_combinations:,}")

    for sim_num, outcomes in enumerate(product(['Home', 'Away'], repeat=len(match_list))):
        sim_points = base_points.copy()
        game_results = []

        for (idx, match), outcome in zip(match_list, outcomes):
            home_team = match['Home Team']
            away_team = match['Away Team']

            if outcome == 'Home':
                sim_points[home_team] += 2
                winner = home_team
            else:
                sim_points[away_team] += 2
                winner = away_team

            game_results.append(f"{home_team} vs {away_team}, Winner predicted: {winner}")

        # Now check qualification
        qualified_teams = [team for team, points in sim_points.items() if points >= qualifying_points]

        for team in qualified_teams:
            qualification_counts[team] += 1
            team_scenarios[team].append({
                'Simulation Number': sim_num,
                'Points': sim_points[team],
                'Game Results': game_results
            })

    qualification_percentages = {
        team: (count / total_combinations) * 100
        for team, count in qualification_counts.items()
    }

    return qualification_percentages, team_scenarios

# Simulate using random seeds (Monte Carlo fallback for large n)
def simulate_tournament_with_results(matches, base_points, seed):
    points = base_points.copy()
    game_results = []
    random.seed(seed)

    for _, match in matches.iterrows():
        home_team = match['Home Team']
        away_team = match['Away Team']
        result = random.choice(['Home', 'Away'])

        if result == 'Home':
            points[home_team] += 2
            winner = home_team
        else:
            points[away_team] += 2
            winner = away_team

        game_results.append(f"{home_team} vs {away_team}, Winner predicted: {winner}")

    return points, game_results

def get_game_results_for_simulation(matches):
    results = []
    for _, match in matches.iterrows():
        home_team = match['Home Team']
        away_team = match['Away Team']
        result = random.choice(['Home', 'Away'])
        winner = home_team if result == 'Home' else away_team
        results.append(f"{home_team} vs {away_team}, Winner predicted: {winner}")
    return results

def run_monte_carlo(matches, base_points, qualifying_points, simulations=50000):
    qualification_counts = defaultdict(int)
    team_scenarios = defaultdict(list)
    for sim_num in range(simulations):
        sim_points, game_results = simulate_tournament_with_results(matches, base_points, sim_num)
        #game_results = get_game_results_for_simulation(matches)
        # Now check qualification
        qualified_teams = [team for team, points in sim_points.items() if points >= qualifying_points]
        for team in qualified_teams:
            qualification_counts[team] += 1
            team_scenarios[team].append({
                'Simulation Number': sim_num,
                'Points': sim_points[team],
                'Game Results': game_results
            })
    qualification_percentages = {
        team: (count / simulations) * 100
        for team, count in qualification_counts.items()
    }
    return qualification_percentages, team_scenarios

def save_qualifying_scenarios_to_csv(team_scenarios, team_name, file_name, qualifying_points):
    if team_name not in team_scenarios:
        print(f"No qualifying scenarios found for {team_name}.")
        return

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Simulation Number', 'Match', 'Winner'])

        for scenario in team_scenarios[team_name]:
            if scenario['Points'] < qualifying_points:
                continue  # skip non-qualifying ones

            simulation_num = scenario['Simulation Number']
            game_results = scenario['Game Results']
            for match_result in game_results:
                match_info = match_result.split(', Winner predicted: ')
                match = match_info[0].strip()
                winner = match_info[1].strip()
                writer.writerow([simulation_num, match, winner])

    print(f"Qualifying scenarios for {team_name} (with ≥ {qualifying_points} points) saved to {file_name}")


def save_all_simulations_to_csv(team_scenarios, file_name):
    # Use a set to track already saved simulation numbers
    seen_simulations = set()

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Simulation Number', 'Match', 'Winner'])

        for scenarios in team_scenarios.values():
            for scenario in scenarios:
                sim_num = scenario['Simulation Number']

                if sim_num in seen_simulations:
                    continue  # already saved this simulation

                seen_simulations.add(sim_num)

                for match_result in scenario['Game Results']:
                    match_info = match_result.split(', Winner predicted: ')
                    match = match_info[0].strip()
                    winner = match_info[1].strip()
                    writer.writerow([sim_num, match, winner])

    print(f"All unique simulations saved to {file_name}")

# Main logic
def main():
    file_path = "C:\\Kani_Personal\\Cricket_Study\\ipl_simulation\\ipl_2025_schedule.csv"
    qualifying_points = int(input("Enter the qualifying points (e.g., 16): "))
    matches, base_points = load_data(file_path)

    if matches is None:
        return

    match_count = len(matches)
    print(f"\nSimulating {match_count} matches...\n")

    start_time = time.time()

    if match_count <= 15:
        print("Using all combinations method...")
        qualification_percentages, team_scenarios = run_all_combinations(matches, base_points, qualifying_points)
    else:
        print("Too many matches left. Falling back to Monte Carlo simulations.")
        num_simulations = int(input("Enter the number of simulations: "))
        qualification_percentages, team_scenarios = run_monte_carlo(matches, base_points, qualifying_points, num_simulations)

    end_time = time.time()

    # Display
    table_data = []
    for team, percentage in sorted(qualification_percentages.items(), key=lambda x: x[1], reverse=True):
        table_data.append([team, f"{percentage:.2f}%"])

    print(f"\nQualification Probabilities (Teams with ≥ {qualifying_points} points):")
    print(tabulate(table_data, headers=["Team", "Qualification Probability"], tablefmt="pretty"))
    print(f"\nCompleted in {end_time - start_time:.2f} seconds.\n")

    # Save results
    save_all_simulations = input("Do you want to store all simulations to a CSV file? (yes/no): ").strip().lower()
    if save_all_simulations == 'yes':
        file_name = input("Enter the name of the file to save simulations (e.g., all_simulations.csv): ").strip()
        save_all_simulations_to_csv(team_scenarios, file_name)

    specific_team = input("Do you want to see the qualifying scenarios for a specific team? (yes/no): ").strip().lower()
    if specific_team == 'yes':
        team_name = input("Enter the team name (e.g., Chennai Super Kings): ").strip()
        if team_name in team_scenarios:
            save_file_input = input(f"Do you want to save the qualifying scenarios for {team_name} to a file? (yes/no): ").strip().lower()
            if save_file_input == 'yes':
                file_name = input("Enter the name of the file to save results (e.g., qualifying_scenarios.csv): ").strip()
                save_qualifying_scenarios_to_csv(team_scenarios, team_name, file_name, qualifying_points)
        else:
            print(f"No qualifying scenarios found for {team_name}.")

if __name__ == "__main__":
    main()
