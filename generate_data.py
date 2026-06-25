import pandas as pd

data = []

zones = ["Residential_A", "Commercial_B", "Industrial_C"]

for i in range(180):
    for zone in zones:
        base_pop = {"Residential_A":5000, "Commercial_B":3000, "Industrial_C":4000}[zone]
        
        temp = 22 + (i % 15)
        rain = 0 if i % 10 != 0 else 10
        weekend = 1 if i % 7 in [5,6] else 0
        festival = 1 if i % 30 == 0 else 0
        
        demand = base_pop * 20 + temp*500 - rain*200
        
        if weekend:
            demand += 5000 if zone=="Residential_A" else -5000
        if festival:
            demand += 10000
        
        data.append([
            f"2024-01-{(i%30)+1}",
            zone,
            base_pop,
            temp,
            rain,
            weekend,
            festival,
            int(demand)
        ])

df = pd.DataFrame(data, columns=[
    "date","zone","population","temperature",
    "rainfall","is_weekend","is_festival","water_supply"
])

df.to_csv("water_data_big.csv", index=False)

print("Dataset created!")