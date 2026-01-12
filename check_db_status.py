import requests

API_KEY = "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE"

# Check products stats
response = requests.get(
    "https://onebby-api.onrender.com/api/admin/stats/products",
    headers={"X-API-KEY": API_KEY}
)

print("Status:", response.status_code)
if response.status_code == 200:
    data = response.json()
    print("\n=== Current Database Status ===")
    print(f"Total Products: {data['total_products']}")
    print(f"Active Products: {data['active_products']}")
    print(f"Total Categories: {data['total_categories']}")
    print(f"Total Brands: {data['total_brands']}")
    print(f"\nProducts by Type:")
    for ptype, count in data['products_by_type'].items():
        print(f"  {ptype}: {count}")
else:
    print("Error:", response.text)
