from flask import Flask, render_template, request, redirect, url_for
from models import db, ShoppingListItem, Category, Store, StoreCategory, ItemDefaultCategory
from sqlalchemy import select, case, func
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
            case((StoreCategory.order_index.is_(None), 1), else_=0),
            StoreCategory.order_index,
            StoreCategory.category_id,
            func.lower(ShoppingListItem.name),
        )
    )
    result = db.session.scalars(stmt).all()
    return result


@app.route("/")
def index():
    selected_store = request.args.get("store", 1)
    print(selected_store)
    items = get_sorted_shopping_list(selected_store)
    stores = db.session.scalars(select(Store)).all()

    return render_template("index.html", items=items, selected_store=selected_store, stores=stores)


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
            category_id = default_mapping.default_category.id
        else:
            category_id = None

        new_item = ShoppingListItem(name=item_name, quantity=quantity, category_id=category_id)
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
    selected_store = request.args.get("store", 1)
    items = get_sorted_shopping_list(selected_store)
    return render_template("_items.html", items=items)


@app.route("/category_order")
def category_order():
    selected_store_name = request.args.get("store", "Rema 1000")
    stores = Store.query.all()
    selected_store = Store.query.filter_by(name=selected_store_name).first()

    return render_template(
        "category_order.html",
        stores=stores,
        selected_store=selected_store,
        associations=selected_store.store_category_association,
    )


if __name__ == "__main__":
    app.run(debug=True)
