from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ShoppingListItem(db.Model):
    __tablename__ = "shopping_list_item"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    category = db.relationship("Category", backref="shopping_list_item")

    def __repr__(self):
        return f"<ShoppingListItem {self.name} ({self.quantity}) in {self.category}>"


class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Category {self.name}>"


class Store(db.Model):
    __tablename__ = "store"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f"<Store {self.name}>"


class StoreCategory(db.Model):
    __tablename__ = "store_category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    order_index = db.Column(db.Integer, nullable=False)

    store = db.relationship("Store", backref="store_category_association")
    category = db.relationship("Category", backref="store_category_association")

    def __repr__(self):
        return f"<StoreCategory store_id={self.store_id} category_id={self.category_id} order={self.order_index}>"


class ItemDefaultCategory(db.Model):
    __tablename__ = "item_default_category"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_name = db.Column(db.String(100), unique=True, nullable=False)
    default_category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    default_category = db.relationship("Category", backref="default_item")

    def __repr__(self):
        return f"<ItemDefaultCategory {self.item_name} => {self.default_category.name}>"
