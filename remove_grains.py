"""
Script to remove all Grains & Pulses products except Rice and Wheat
"""
from database import products_col

# Find all Grains & Pulses products except Rice and Wheat
grains_to_remove = products_col.find({
    "category": "Grains & Pulses",
    "name": {
        "$not": {
            "$regex": "^(Rice|Wheat)",
            "$options": "i"
        }
    }
})

# Display products that will be removed
print("Products to be removed:")
print("-" * 50)
count = 0
for product in grains_to_remove:
    count += 1
    print(f"{count}. {product['name']}")

# Remove the products
result = products_col.delete_many({
    "category": "Grains & Pulses",
    "name": {
        "$not": {
            "$regex": "^(Rice|Wheat)",
            "$options": "i"
        }
    }
})

print("-" * 50)
print(f"\n✅ Successfully removed {result.deleted_count} products!")

# Show remaining products
remaining = list(products_col.find({"category": "Grains & Pulses"}))
print(f"\n📦 Remaining Grains & Pulses products:")
for product in remaining:
    print(f"  - {product['name']}")
