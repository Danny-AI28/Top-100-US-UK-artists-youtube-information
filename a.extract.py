import billboard
import pandas as pd

chart = billboard.ChartData('artist-100')

print(f"--- Bảng xếp hạng Billboard Artist 100 (Ngày: {chart.date}) ---")
data = []
for i, artist in enumerate(chart, start=1):
    data.append({
        'Rank': i,
        'Name': artist
    })

df = pd.DataFrame(data)

def clean_name(raw_value):
    if pd.isna(raw_value):
        return raw_value
    raw_value = str(raw_value).strip()
    if " by " in raw_value.lower():
        clean = raw_value.split(" by ")[-1]
    else:
        clean = raw_value.strip("'")
    return clean.strip()

df["artist_name"] = df["Name"].apply(clean_name)

df.to_csv("Top100artists.csv", index = False, encoding= 'utf-8')