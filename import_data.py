import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///shopping_list.db")


def import_data(csv_path, table):
    df = pd.read_csv(csv_path, delimiter=";")
    df.to_sql(table, con=engine, if_exists="append", index=False)


import_data("csv/category.csv", "category")
import_data("csv/item_default_category.csv", "item_default_category")
import_data("csv/store_category.csv", "store_category")
import_data("csv/store.csv", "store")
