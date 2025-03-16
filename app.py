from flask import Flask, render_template, request, redirect, url_for
from models import db, ShoppingListItem, Category, Store, StoreCategory, ItemDefaultCategory
import os

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "shopping_list.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def get_sorted_shopping_list(selected_store):
    store = Store.query.filter_by(name=selected_store).first()
    if store:
        order_map = {assoc.category.name: assoc.order_index for assoc in store.store_categories}
    else:
        order_map = {}

    items = ShoppingListItem.query.all()

    def sort_key(item):
        order = order_map.get(item.category, float("inf"))
        return (order, item.name.lower())

    return sorted(items, key=sort_key)


@app.route("/")
def index():
    selected_store = request.args.get("store", "Rema 1000")
    sorted_items = get_sorted_shopping_list(selected_store)
    stores = Store.query.all()

    return render_template("index.html", items=sorted_items, store=selected_store, stores=stores)


@app.route("/add", methods=["POST"])
def add_item():
    item_name_quantity = request.form.get("item", "").strip()
    parts = item_name_quantity.rsplit(" ", 1)

    if len(parts) > 1 and parts[1].isdigit():
        item_name = parts[0]
        quantity = int(parts[1])
    else:
        item_name = item_name_quantity
        quantity = 1

    if item_name:
        default_mapping = ItemDefaultCategory.query.filter_by(item_name=item_name.lower()).first()
        if default_mapping:
            category = default_mapping.default_category.name
        else:
            category = "Uncategorized"

        new_item = ShoppingListItem(name=item_name, quantity=quantity, category=category)
        db.session.add(new_item)
        db.session.commit()

    return redirect(url_for("items_partial", store=request.form.get("store")))


@app.route("/remove/<string:removed_item>")
def remove_item(removed_item):
    item = ShoppingListItem.query.filter_by(name=removed_item).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("items_partial", store=request.args.get("store")))


@app.route("/items_partial")
def items_partial():
    if not request.headers.get("HX-Request"):
        return redirect(url_for("index"))
    selected_store = request.args.get("store", "Rema 1000")
    sorted_items = get_sorted_shopping_list(selected_store)
    return render_template("_items.html", items=sorted_items)


if __name__ == "__main__":
    app.run(debug=True)
