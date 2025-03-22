from flask import Flask, render_template, request, redirect, url_for
from models import db, ShoppingListItem, Category, Store, StoreCategory, ItemDefaultCategory
from sqlalchemy import select, delete
import os

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "shopping_list.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


def get_sorted_shopping_list(selected_store_id):
    stmt = (
        select(ShoppingListItem)
        .outerjoin(
            StoreCategory,
            (ShoppingListItem.category_id == StoreCategory.category_id)
            & (StoreCategory.store_id == selected_store_id),
        )
        .order_by(
            StoreCategory.order_index.nulls_last(),
            StoreCategory.category_id,
            ShoppingListItem.name.collate("NOCASE"),
        )
    )
    result = db.session.scalars(stmt).all()
    return result


@app.route("/")
def index():
    selected_store = int(request.args.get("store", 1))
    items = get_sorted_shopping_list(selected_store)
    stores = db.session.scalars(select(Store)).all()

    return render_template("index.html", items=items, stores=stores)


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
        default_mapping = db.session.scalar(
            select(ItemDefaultCategory).where(ItemDefaultCategory.item_name == item_name.lower())
        )
        if default_mapping:
            category_id = default_mapping.default_category_id
        else:
            category_id = None

        new_item = ShoppingListItem(name=item_name, quantity=quantity, category_id=category_id)
        db.session.add(new_item)
        db.session.commit()

    return redirect(url_for("items_partial", store=request.form.get("store")))


@app.route("/remove/<int:removed_item>")
def remove_item(removed_item):
    item = db.session.scalar(select(ShoppingListItem).where(ShoppingListItem.id == removed_item))
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for("items_partial", store=request.args.get("store")))


@app.route("/items_partial")
def items_partial():
    if not request.headers.get("HX-Request"):
        return redirect(url_for("index"))
    selected_store = request.args.get("store", 1)
    items = get_sorted_shopping_list(selected_store)
    return render_template("_items.html", items=items)


@app.route("/category_order", methods=["GET"])
def category_order():
    selected_store = int(request.args.get("store", 1))
    stores = db.session.scalars(select(Store)).all()
    associations = db.session.scalars(
        select(StoreCategory).where(StoreCategory.store_id == selected_store).order_by(StoreCategory.order_index)
    ).all()

    return render_template(
        "category_order.html", stores=stores, selected_store=selected_store, associations=associations
    )


@app.route("/category_order", methods=["PUT"])
def category_order_put():
    selected_store = int(request.form.get("store"))
    category_ids = request.form.getlist("category_id")
    db.session.execute(delete(StoreCategory).where(StoreCategory.store_id == selected_store))
    for i, category_id in enumerate(category_ids):
        new_association = StoreCategory(store_id=selected_store, category_id=category_id, order_index=i + 1)
        db.session.add(new_association)
    db.session.commit()
    return ""


if __name__ == "__main__":
    app.run(debug=True)
