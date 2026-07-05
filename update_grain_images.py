"""
Script to update grain and pulse product images in the database
"""
from database import products_col
from app import get_product_image

# Update all products in the Grains & Pulses category
grains_products = products_col.find({"category": "Grains & Pulses"})

updated_count = 0
for product in grains_products:
    # Get the corrected image URL based on the product name
    correct_image = get_product_image(product['name'])
    
    # Update the product with the new image
    result = products_col.update_one(
        {"_id": product["_id"]},
        {"$set": {"image": correct_image}}
    )
    
    if result.modified_count > 0:
        updated_count += 1
        print(f"Updated: {product['name']} -> {correct_image}")

print(f"\n✅ Successfully updated {updated_count} grain and pulse products!")
