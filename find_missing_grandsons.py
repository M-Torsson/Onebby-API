import pandas as pd

# Read Excel file
df = pd.read_excel('app/excel/prezzoforte_category_tree.xlsx')

# All grandsons in Excel
all_grandsons = set(df['Grandson'].dropna())

# Grandsons we've added
added = {
    8412, 8413, 8414,  # Lavatrici
    8455, 8456, 8457, 8458, 8459, 8460, 8461, 8462,  # Home Cinema
    8452, 8453,  # Condizionatori
    8427, 8318,  # Riscaldamento
    8431, 8432, 8433, 8434, 8435, 8436, 8437, 8438, 8439,  # Preparazione cibi
    8323, 8332, 8324, 8428, 8429, 8329, 8430,  # Cottura cibi
    8442, 8443, 8440, 8441,  # Computer portatili
    8444, 8445  # Tablet e accessori
}

# Find missing grandsons
missing = all_grandsons - added

print(f"إجمالي الأحفاد في Excel: {len(all_grandsons)}")
print(f"الأحفاد المضافة: {len(added)}")
print(f"الباقي: {len(missing)}\n")

print("الأحفاد المتبقية:")
for grandson_id in sorted(missing):
    rows = df[df['Grandson'] == grandson_id]
    if not rows.empty:
        child = rows.iloc[0]['Child']
        grandson = rows.iloc[0]['Grandson']
        print(f"  • {grandson} (تحت: {child})")
