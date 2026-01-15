import requests
import json

API_URL = "https://onebby-api.onrender.com/api/v1/categories"
API_KEY = "OnebbyAPIKey2025P9mK7xL4rT8nW2qF5vB3cH6jD9zYaXbRcGdTeUf1MwNyQsV"

headers = {
    "X-API-Key": API_KEY
}

print("=" * 80)
print("Testing API with parent_only=true")
print("=" * 80)

# Test with parent_only=true
response = requests.get(f"{API_URL}?parent_only=true", headers=headers)
data = response.json()

print(f"\nStatus Code: {response.status_code}")
print(f"Total categories: {data['meta']['total']}")
print(f"Returned: {len(data['data'])}")
print(f"Parent only: {data['meta']['parent_only']}")

# Check if any has parent_id
non_parents = [cat for cat in data['data'] if cat['parent_id'] is not None]
print(f"\nCategories with parent_id (should be 0): {len(non_parents)}")

if non_parents:
    print("\n❌ ERROR: Found categories with parent_id:")
    for cat in non_parents[:5]:
        print(f"  ID: {cat['id']}, Name: {cat['name']}, Parent: {cat['parent_id']}")
else:
    print("\n✅ All returned categories are main categories (parent_id = null)")

print(f"\nAll {len(data['data'])} categories:")
for cat in data['data']:
    has_children = "✅" if cat.get('has_children') else "❌"
    print(f"  {has_children} {cat['id']:5d} - {cat['name']}")
