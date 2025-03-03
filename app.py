from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

FILE_NAME = "data.json"

def load_data():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)

@app.route("/")
def index():
    # Get the selected store from the query parameters; default to "rema1000"
    selected_store = request.args.get("store", "rema1000")
    # Load the shopping list items
    items = load_data()

    # Load the store category order from stores.json
    with open("stores.json", "r", encoding="utf-8") as f:
        stores = json.load(f)
    
    # Get the category order for the selected store (empty list if not found)
    category_order = stores.get(selected_store, [])
    
    # Define a custom sort key: first by the category order index, then by item name (alphabetically)
    def sort_key(item):
        try:
            # Find the index of the item category in the store's category order
            idx = category_order.index(item.get("category", "Uncategorized"))
        except ValueError:
            # If the category is not found, put it at the end
            idx = len(category_order)
        return (idx, item["name"].lower())
    
    sorted_items = sorted(items, key=sort_key)
    
    # Pass the sorted items, the current store, and available stores to the template
    return render_template("index.html", items=sorted_items, store=selected_store, stores=stores.keys())

@app.route("/add", methods=["POST"])
def add_item():
    item_name_quantity = request.form.get("item", "").strip()
    parts = item_name_quantity.rsplit(" ", 1)
    
    # The text before the last space is the item name; 
    # the text after the last space (if numeric) is the quantity.
    item_name = parts[0] if len(parts) > 1 and parts[1].isdigit() else item_name_quantity
    quantity = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
    
    # Only proceed if there's an actual item name
    if item_name_quantity:
        # Load your main data list (shopping list items)
        data = load_data()
        
        # Load your item/category mapping from items.json
        with open("items.json", "r", encoding="utf-8") as f:
            items_map = json.load(f)
        
        # Normalize the user’s item name for lookup (e.g., lowercase)
        lookup_name = item_name.lower()
        
        # Look up the category in items.json; default to "Uncategorized" if not found
        category = items_map.get(lookup_name, "Uncategorized")
        
        # Add the new item with category to your data
        data.append({
            "name": item_name,
            "quantity": quantity,
            "category": category
        })
        
        # Save the updated data
        save_data(data)
    
    # Redirect back to the index page
    return redirect(url_for("index"))

@app.route("/remove/<item_name>")
def remove_item(item_name):
    data = load_data()
    data = [item for item in data if item["name"] != item_name]
    save_data(data)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
