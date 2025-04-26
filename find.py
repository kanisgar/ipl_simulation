from bs4 import BeautifulSoup

# Load your full HTML content into this variable
html = open("simulated.html", "r").read()

soup = BeautifulSoup(html, "html.parser")
simulations = soup.find_all("h2")  # each simulation starts with an <h2>

csk_top4_count = 0

for sim in simulations:
    sim_number = sim.text.strip().replace("Simulation ", "")
    table = sim.find_next("table")
    rows = table.find_all("tr")[1:5]  # get top 4 rows (excluding header)
    
    for row in rows:
        team = row.find_all("td")[0].text.strip()
        if team == "Chennai Super Kings":
            print(f"Chennai Super Kings is in Top 4 in Simulation {sim_number}")
            csk_top4_count += 1
            break

print(f"\nTotal Simulations where CSK is in Top 4: {csk_top4_count}")