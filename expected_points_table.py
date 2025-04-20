import pandas as pd
import json

def generate_combined_simulation_html(sim_csv_path, points_json_path, output_html_path):
    # Load base points table from JSON
    with open(points_json_path, 'r') as f:
        base_points = json.load(f)

    # Read the simulation match results CSV
    df = pd.read_csv(sim_csv_path)

    # Start building the HTML content
    html_content = """
    <html>
    <head>
        <title>All Simulations</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            h1 { color: #222; }
            h2 { margin-top: 40px; color: #333; }
            table { border-collapse: collapse; width: 60%; margin-bottom: 40px; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>Simulated Points Table Results</h1>
    """

    # === Insert current points table before simulations ===
    base_points_df = pd.DataFrame(base_points.items(), columns=["Team", "Points"])
    base_points_df = base_points_df.sort_values(by="Points", ascending=False).reset_index(drop=True)
    base_table_html = base_points_df.to_html(index=False, border=0)
    html_content += "<h2>Current Points Table (Before Simulations)</h2>\n" + base_table_html + "\n"

    # === Process each simulation ===
    for sim_number in sorted(df['Simulation Number'].unique()):
        sim_df = df[df['Simulation Number'] == sim_number]

        # Start with a fresh copy of the base points
        points_table = base_points.copy()

        # Update points based on match results
        for _, row in sim_df.iterrows():
            winner = row["Winner"]
            if winner in points_table:
                points_table[winner] += 2
            else:
                print(f"⚠️ Warning: '{winner}' not in base points table")

        # Create sorted points table
        points_df = pd.DataFrame(points_table.items(), columns=["Team", "Points"])
        points_df = points_df.sort_values(by="Points", ascending=False).reset_index(drop=True)

        # Convert to HTML and append to the main content
        table_html = points_df.to_html(index=False, border=0)
        html_content += f"<h2>Simulation {sim_number}</h2>\n{table_html}\n"

    # Finish HTML
    html_content += "</body></html>"

    # Write the output to the specified HTML file
    with open(output_html_path, "w") as f:
        f.write(html_content)

    print(f"✅ Combined simulation output saved to {output_html_path}")


# === USAGE EXAMPLE ===
generate_combined_simulation_html(
    sim_csv_path="csk.csv",  # Replace with your CSV filename
    points_json_path="current_points_table.json",  # Replace with your JSON filename
    output_html_path="simulated.html"  # Output HTML file name
)
