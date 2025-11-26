from flask import Flask, request, jsonify
from threading import Lock
import os


app = Flask(__name__)

_lock = Lock()
_products = {}
_next_id = 1


def _create_product(name: str, price: float) -> dict:
    global _next_id
    with _lock:
        pid = _next_id
        _next_id += 1
        prod = {"id": pid, "name": name, "price": float(price)}
        _products[pid] = prod
        return prod


@app.get("/products")
def list_products():
    with _lock:
        return jsonify(list(_products.values())), 200


@app.post("/products")
def create_product():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    price = data.get("price")
    if not isinstance(name, str) or name == "":
        return jsonify({"error": "name is required"}), 400
    try:
        price_val = float(price)
    except Exception:
        return jsonify({"error": "price must be a number"}), 400
    prod = _create_product(name, price_val)
    return jsonify(prod), 201


@app.get("/products/<int:pid>")
def get_product(pid: int):
    with _lock:
        prod = _products.get(pid)
        if not prod:
            return jsonify({"error": "not found"}), 404
        return jsonify(prod), 200


@app.put("/products/<int:pid>")
def update_product(pid: int):
    data = request.get_json(silent=True) or {}
    with _lock:
        prod = _products.get(pid)
        if not prod:
            return jsonify({"error": "not found"}), 404
        if "name" in data:
            if not isinstance(data["name"], str) or data["name"] == "":
                return jsonify({"error": "invalid name"}), 400
            prod["name"] = data["name"]
        if "price" in data:
            try:
                prod["price"] = float(data["price"])
            except Exception:
                return jsonify({"error": "invalid price"}), 400
        return jsonify(prod), 200


@app.delete("/products/<int:pid>")
def delete_product(pid: int):
    with _lock:
        if pid in _products:
            del _products[pid]
            return "", 204
        return jsonify({"error": "not found"}), 404


def main() -> None:
    port = int(os.environ.get("PORT", "8001"))
    # threaded=True to allow concurrent requests during load test
    app.run(host="127.0.0.1", port=port, threaded=True)


if __name__ == "__main__":
    main()


