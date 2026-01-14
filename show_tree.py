import requests

response = requests.get(
    "https://onebby-api.onrender.com/api/v1/categories",
    params={"limit": 200},
    timeout=30
)

data = response.json()['data']

print(f"Total categories: {len(data)}\n")

# Group by parent
parents = {}
for cat in data:
    parent_id = cat.get('parent_id')
    if parent_id is None:
        if cat['id'] not in parents:
            parents[cat['id']] = {'name': cat['name'], 'children': []}
    else:
        if parent_id not in parents:
            parents[parent_id] = {'name': '???', 'children': []}
        parents[parent_id]['children'].append(cat['name'])

print("=" * 80)
print("Category Tree Structure:")
print("=" * 80)
for parent_id, info in sorted(parents.items()):
    print(f"\n[{parent_id}] {info['name']} ({len(info['children'])} children)")
    for child in info['children'][:5]:
        print(f"  • {child}")
    if len(info['children']) > 5:
        print(f"  ... and {len(info['children']) - 5} more")
