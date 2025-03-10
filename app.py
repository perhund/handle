from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

SHOPPING_LIST_FILE = "shopping_list.json"
ITEM_CATEGORIES_FILE = "item_categories.json"
CATEGORY_ORDERS_FILE = "category_orders.json"


def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def save_data(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def get_sorted_shopping_list(category_order):
    items = load_data(SHOPPING_LIST_FILE)

    # Define a custom sort key: first by the category order index, then by item name (alphabetically)
    def sort_key(item):
        try:
            idx = category_order.index(item.get("category"))
        except ValueError:
            idx = len(category_order)
        return (idx, item["name"].lower())

    return sorted(items, key=sort_key)


@app.route("/")
def index():
    selected_store = request.args.get("store", "rema1000")
    category_orders = load_data(CATEGORY_ORDERS_FILE)
    stores = category_orders.keys()
    category_order = category_orders.get(selected_store, [])
    sorted_items = get_sorted_shopping_list(category_order)

    return render_template(
        "index.html", items=sorted_items, store=selected_store, stores=stores
    )


@app.route("/add", methods=["POST"])
def add_item():
    # Get the form-encoded data sent by htmx
    item_name_quantity = request.form.get("item", "").strip()
    selected_store = request.form.get("store", "rema1000")
    parts = item_name_quantity.rsplit(" ", 1)

    # If the last word is a number, treat it as quantity.
    if len(parts) > 1 and parts[1].isdigit():
        item_name = parts[0]
        quantity = int(parts[1])
    else:
        item_name = item_name_quantity
        quantity = 1

    if item_name:
        shopping_list = load_data(SHOPPING_LIST_FILE)
        lookup_name = item_name.lower()
        item_categories = load_data(ITEM_CATEGORIES_FILE)
        category = item_categories.get(lookup_name, "Uncategorized")
        new_item = {"name": item_name, "quantity": quantity, "category": category}
        shopping_list.append(new_item)
        save_data(shopping_list, SHOPPING_LIST_FILE)

    # Get the sorted items list for the currently selected store
    category_orders = load_data(CATEGORY_ORDERS_FILE)
    category_order = category_orders.get(selected_store, [])
    sorted_items = get_sorted_shopping_list(category_order)

    # Return the updated items partial (HTML fragment)
    return render_template("_items.html", items=sorted_items)


@app.route("/remove/<removed_item>")
def remove_item(removed_item):
    # Update shopping list
    shopping_list = load_data(SHOPPING_LIST_FILE)
    shopping_list = [item for item in shopping_list if item["name"] != removed_item]
    save_data(shopping_list, SHOPPING_LIST_FILE)

    # Sort shopping list
    selected_store = request.args.get("store", "rema1000")
    category_orders = load_data(CATEGORY_ORDERS_FILE)
    category_order = category_orders.get(selected_store, [])
    sorted_items = get_sorted_shopping_list(category_order)

    return render_template("_items.html", items=sorted_items)


@app.route("/items_partial")
def items_partial():
    selected_store = request.args.get("store", "rema1000")
    category_orders = load_data(CATEGORY_ORDERS_FILE)
    category_order = category_orders.get(selected_store, [])
    sorted_items = get_sorted_shopping_list(category_order)

    return render_template("_items.html", items=sorted_items)


if __name__ == "__main__":
    app.run(debug=True)
