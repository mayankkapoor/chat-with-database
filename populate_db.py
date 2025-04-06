import os
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from dotenv import load_dotenv
from supabase import create_client, Client
# Import the specific error type if you want finer-grained error handling
# from postgrest.exceptions import APIError  # Adjust import based on library version if needed

# --- Configuration ---
load_dotenv() # Load environment variables from .env file

SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in the .env file")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Initialize Faker for generating test data
fake = Faker()

# Define how much data to generate
NUM_USERS = 200
NUM_PRODUCTS = 500
NUM_ORDERS = 2500
BATCH_SIZE = 100 # Adjust based on performance and potential timeouts

# --- Data Generation Functions ---

def generate_users(count):
    """Generates a list of fake user data."""
    users = []
    for _ in range(count):
        # Generate the date object first
        signup_date_obj = fake.date_between(start_date='-2y', end_date='today')
        users.append({
            'name': fake.name(),
            'email': fake.unique.email(), # Ensure emails are unique
            'city': fake.city(),
            # Convert the date object to an ISO 8601 string (YYYY-MM-DD)
            'signup_date': signup_date_obj.isoformat() # <--- FIX IS HERE
        })
    # Reset uniqueness for email if you run the script multiple times in one session
    fake.unique.clear()
    return users

def generate_products(count):
    """Generates a list of fake product data."""
    products = []
    # Expanded list of categories for more variety
    categories = ['Electronics', 'Books', 'Clothing', 'Home Goods', 'Grocery', 'Toys', 'Sports', 'Outdoors', 'Beauty', 'Automotive']
    for _ in range(count):
        products.append({
            # --- FIX IS HERE ---
            # Replace fake.ecommerce_name() with a combination of standard methods
            # Example: Combine capitalized words for a product-like feel
            'name': f"{fake.bs().capitalize()} {fake.word().capitalize()}",
            # Alternative: fake.catch_phrase()
            # Alternative: f"{fake.word().capitalize()} {fake.word().capitalize()} {fake.word()}"

            'description': fake.paragraph(nb_sentences=3),
            # Ensure price is non-negative
            'price': max(0.01, round(random.uniform(1.0, 2500.0), 2)),
            'category': random.choice(categories),
            # Ensure stock is non-negative
            'stock_quantity': random.randint(0, 250)
        })
    return products

def generate_orders(count, user_ids, product_ids):
    """Generates a list of fake order data using existing user and product IDs."""
    orders = []
    statuses = ['pending', 'shipped', 'delivered', 'cancelled', 'returned']

    if not user_ids or not product_ids:
        print("Error: Cannot generate orders without valid user_ids or product_ids.")
        return []

    for _ in range(count):
        # Generate an order date within the last year, ensure timezone aware
        order_date = fake.date_time_between(start_date='-1y', end_date='now', tzinfo=timezone.utc)
        orders.append({
            'user_id': random.choice(user_ids),
            'product_id': random.choice(product_ids),
            # Ensure quantity is at least 1
            'quantity': random.randint(1, 8),
            'order_status': random.choice(statuses),
            # Format timestamp with timezone for Supabase TIMESTAMPTZ
            'order_date': order_date.isoformat()
        })
    return orders

# --- Helper Function for Batch Insertion ---

def insert_in_batches(table_name, data, batch_size):
    """Inserts data into a Supabase table in batches."""
    inserted_data = []
    total_inserted = 0
    print(f"\nAttempting to insert {len(data)} records into '{table_name}' in batches of {batch_size}...")

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        try:
            # '.execute()' is implicit in newer versions, but can be explicit for clarity
            response = supabase.table(table_name).insert(batch).execute()
            
            # Check if response contains data (successful insertion)
            # Note: Response structure might vary slightly between versions or based on settings (e.g., return=representation)
            if hasattr(response, 'data') and response.data:
                inserted_data.extend(response.data)
                total_inserted += len(response.data)
                print(f"  Batch {i // batch_size + 1}: Inserted {len(response.data)} records.")
            else:
                # Handle cases where insertion might succeed but return no data, or potential errors
                # Check for explicit errors if possible (depends on library version)
                # Example check (may need adjustment):
                if hasattr(response, 'error') and response.error:
                     print(f"  Batch {i // batch_size + 1}: Failed. Error: {response.error}")
                # else: # If no error but also no data, log it
                #    print(f"  Batch {i // batch_size + 1}: Succeeded but returned no data (may be expected).")

        except Exception as e: # Catch potential exceptions during the API call
             print(f"  Batch {i // batch_size + 1}: FAILED. Exception: {e}")
             # Optionally: break or continue based on desired error handling

    print(f"Finished inserting into '{table_name}'. Total successfully inserted records (based on response data): {total_inserted}")
    return inserted_data

# --- Main Execution Logic ---

if __name__ == "__main__":
    print("Starting database population...")

    # 1. Generate and Insert Users
    users_to_insert = generate_users(NUM_USERS)
    inserted_users_response = insert_in_batches('users', users_to_insert, BATCH_SIZE)
    # Extract IDs ONLY from successfully inserted records (those present in the response data)
    user_ids = [user['id'] for user in inserted_users_response if 'id' in user]
    if not user_ids:
        print("CRITICAL: No users were inserted or IDs could not be retrieved. Aborting further insertions.")
        exit() # Stop if we can't proceed with dependencies


    # 2. Generate and Insert Products
    products_to_insert = generate_products(NUM_PRODUCTS)
    inserted_products_response = insert_in_batches('products', products_to_insert, BATCH_SIZE)
    product_ids = [product['id'] for product in inserted_products_response if 'id' in product]
    if not product_ids:
        print("CRITICAL: No products were inserted or IDs could not be retrieved. Aborting order insertion.")
        exit() # Stop if we can't proceed


    # 3. Generate and Insert Orders (using retrieved user and product IDs)
    print(f"\nGenerating {NUM_ORDERS} orders using {len(user_ids)} users and {len(product_ids)} products...")
    orders_to_insert = generate_orders(NUM_ORDERS, user_ids, product_ids)
    if orders_to_insert: # Only insert if orders were generated
        insert_in_batches('orders', orders_to_insert, BATCH_SIZE)
    else:
        print("Skipping order insertion as no orders were generated (likely due to missing user/product IDs).")


    print("\n------------------------------------")
    print("Database population script finished.")
    print("------------------------------------")