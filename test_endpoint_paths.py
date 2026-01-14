import requests

headers = {
    "X-API-Key": "X9$eP!7wQ@3nZ8^tF#uL2rC6*mH1yB0_dV4+KpS%aGfJ5$qWzR!N7sT#hU9&bE",
    "Content-Type": "application/json"
}

# Test if endpoint exists
print("Testing endpoint...")
response = requests.post(
    "https://onebby-api.onrender.com/api/v1/admin/categories/recursive-delete",
    headers=headers,
    json={"category_ids": [8159]},
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

# Try different paths
paths = [
    "/api/v1/admin/categories/recursive-delete",
    "/admin/categories/recursive-delete",
    "/v1/admin/categories/recursive-delete",
]

for path in paths:
    print(f"\nTrying: {path}")
    resp = requests.post(
        f"https://onebby-api.onrender.com{path}",
        headers=headers,
        json={"category_ids": [8159]},
        timeout=10
    )
    print(f"  Status: {resp.status_code}")
