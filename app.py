import pandas as pd
import random
from collections import defaultdict
import time
import csv
from tabulate import tabulate  # Importing tabulate module

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


# Run Monte Carlo simulations for qualification probabilities
def run_monte_carlo(matches, base_points, qualifying_points, simulations=50000):
    qualification_counts = defaultdict(int)
    team_scenarios = defaultdict(list)

    for sim_num in range(simulations):
        sim_points = simulate_tournament(matches, base_points)

        # Track qualification for all teams
        for team, points in sim_points.items():
            if points >= qualifying_points:
                qualification_counts[team] += 1
                team_scenarios[team].append({
                    'Simulation Number': sim_num,
                    'Points': points,
                    'Game Results': get_game_results_for_simulation(matches, sim_points)
                })

    # Ensure that all teams are tracked, even those with 0% qualification probability
    all_teams = set(base_points.keys())  # Get the list of all teams
    for team in all_teams:
        if team not in qualification_counts:
            qualification_counts[team] = 0  # Set to 0% if no qualification found

    # Calculate qualification percentages
    qualification_percentages = {
        team: (count / simulations) * 100
        for team, count in qualification_counts.items()
    }

    return qualification_percentages, team_scenarios


# Function to get game results in each simulation
def get_game_results_for_simulation(matches, sim_points):
    game_results = []
    for _, match in matches.iterrows():
        home_team = match['Home Team']
        away_team = match['Away Team']
        winner = home_team if sim_points.get(home_team, 0) > sim_points.get(away_team, 0) else away_team
        game_results.append(f"{home_team} vs {away_team}, Winner predicted: {winner}")
    return game_results


# Save qualifying scenarios to CSV
def save_qualifying_scenarios_to_csv(team_scenarios, team_name, file_name):
    if team_name not in team_scenarios:
        print(f"No qualifying scenarios found for {team_name}.")
        return

    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)

        # Write the headers
        writer.writerow(['Simulation Number', 'Match', 'Winner'])

        # Write each simulation result
        for scenario in team_scenarios[team_name]:
            simulation_num = scenario['Simulation Number']
            game_results = scenario['Game Results']

            # Write each match result as a new line
            for match_result in game_results:
                match_info = match_result.split(', Winner predicted: ')
                match = match_info[0].strip()
                winner = match_info[1].strip()

                writer.writerow([simulation_num, match, winner])

    print(f"Qualifying scenarios for {team_name} saved to {file_name}")


# Main entry point
def main():
    file_path = "/Users/kanisgar/Documents/ipl_simulation/ipl_2025_schedule.csv"
    qualifying_points = int(input("Enter the qualifying points (e.g., 16): "))

    # Ask for number of simulations
    num_simulations = int(input("Enter the number of simulations: "))

    matches, base_points = load_data(file_path)

    print(f"\nRunning {num_simulations:,} tournament simulations... Please wait.\n")
    start_time = time.time()

    qualification_percentages, team_scenarios = run_monte_carlo(matches, base_points, qualifying_points,
                                                                num_simulations)

    end_time = time.time()

    # Prepare the data for tabulation
    table_data = []
    for team, percentage in sorted(qualification_percentages.items(), key=lambda x: x[1], reverse=True):
        table_data.append([team, f"{percentage:.2f}%"])

    # Display the qualification probability in tabular form using tabulate
    print(f"\nQualification Probabilities (Teams with ≥ {qualifying_points} points):")
    print(tabulate(table_data, headers=["Team", "Qualification Probability"], tablefmt="pretty"))

    print(f"\nCompleted in {end_time - start_time:.2f} seconds.\n")

    # Ask user if they want to see a specific team's qualifying scenarios
    specific_team = input(
        "\nDo you want to see the qualifying scenarios for a specific team? (yes/no): ").strip().lower()
    if specific_team == 'yes':
        team_name = input("Enter the team name (e.g., Chennai Super Kings): ").strip()
        if team_name in team_scenarios:
            save_file_input = input(
                f"\nDo you want to save the qualifying scenarios for {team_name} to a file? (yes/no): ").strip().lower()
            if save_file_input == 'yes':
                file_name = input(
                    "Enter the name of the file to save results (e.g., qualifying_scenarios.csv): ").strip()
                save_qualifying_scenarios_to_csv(team_scenarios, team_name, file_name)
        else:
            print(f"\nNo qualifying scenarios found for {team_name}.")


if __name__ == "__main__":
    main()
