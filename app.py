import json
import logging
import os

from flask import Flask, jsonify

from parse import URL, collect_items, get_data

app = Flask(__name__)
logger = logging.getLogger(__name__)


@app.route("/all_products/", methods=["GET"])
def get_all_products():
    with open("menu_items.json", "r", encoding="utf-8") as file:
        menu_items = json.load(file)
    return jsonify(menu_items)


@app.route("/products/<string:product_name>", methods=["GET"])
def get_product_by_name(product_name):
    with open("menu_items.json", "r", encoding="utf-8") as file:
        menu_items = json.load(file)
    for _, product in menu_items.items():
        if product["name"] == product_name:
            return jsonify(product)
    return jsonify({"error": "Product not found"}), 404


@app.route("/products/<string:product_name>/<string:product_field>", methods=["GET"])
def get_product_field(product_name, product_field):
    with open("menu_items.json", "r", encoding="utf-8") as file:
        menu_items = json.load(file)
    for _, product in menu_items.items():
        if product["name"] == product_name:
            if product_field in product:
                return jsonify({product_field: product[product_field]})
            else:
                return jsonify({"error": "Field not found"}), 404
    return jsonify({"error": "Product not found"}), 404


if __name__ == "__main__":
    if not os.path.exists("menu_items.json") or os.stat("menu_items.json").st_size == 0:
        with open("menu_items.json", "w") as json_file:
            json.dump(
                collect_items(get_data(URL)), json_file, ensure_ascii=False, indent=4
            )

    app.run(debug=True, port=5000)
    logger.info("Flask server started")
