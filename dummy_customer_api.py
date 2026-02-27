"""
Dummy Customer API - Simulates a messy, unstructured customer order system.
Returns order data as raw text strings that an AI agent must parse.
"""

import logging
from flask import Flask, request, jsonify

logger = logging.getLogger(__name__)

app = Flask(__name__)

ORDERS = [
    "Order 1001: Buyer=John Davis, Location=Columbus, OH, Total=$742.10, Items: laptop, hdmi cable",
    "Order 1002: Buyer=Sarah Liu, Location=Austin, TX, Total=$156.55, Items: headphones",
    "Order 1003: Buyer=Mike Turner, Location=Cleveland, OH, Total=$1299.99, Items: gaming pc, mouse",
    "Order 1004: Buyer=Rachel Kim, Location=Seattle, WA, Total=$89.50, Items: coffee maker",
    "Order 1005: Buyer=Chris Myers, Location=Cincinnati, OH, Total=$512.00, Items: monitor, desk lamp",
    "Order 1006: Buyer=Amanda Foster, Location=Chicago, IL, Total=$67.25, Items: phone case, screen protector",
    "Order 1007: Buyer=David Park, Location=Portland, OR, Total=$899.99, Items: 4k television",
    "Order 1008: Buyer=Jessica Wang, Location=Dayton, OH, Total=$234.50, Items: wireless keyboard, webcam",
    "Order 1009: Buyer=Brian Kelly, Location=Miami, FL, Total=$1750.00, Items: macbook pro, usb-c hub",
    "Order 1010: Buyer=Lisa Hernandez, Location=Denver, CO, Total=$45.99, Items: notebook, pens",
    "Order 1011: Buyer=Tom Richardson, Location=Akron, OH, Total=$623.00, Items: tablet, stylus, case",
    "Order 1012: Buyer=Emily Chen, Location=San Francisco, CA, Total=$349.99, Items: smart watch",
    "Order 1013: Buyer=James Wilson, Location=Toledo, OH, Total=$178.75, Items: bluetooth speaker, aux cable",
    "Order 1014: Buyer=Maria Santos, Location=Phoenix, AZ, Total=$2100.50, Items: desktop computer, dual monitors, keyboard",
    "Order 1015: Buyer=Kevin O'Brien, Location=Boston, MA, Total=$55.00, Items: mouse pad, cable organizer",
    "Order 1016: Buyer=Priya Patel, Location=Indianapolis, IN, Total=$445.00, Items: noise-canceling headphones, dac",
    "Order 1017: Buyer=Nathan Scott, Location=Columbus, OH, Total=$987.50, Items: drone, extra batteries",
    "Order 1018: Buyer=Hannah Lee, Location=Nashville, TN, Total=$129.99, Items: portable charger, lightning cable",
    "Order 1019: Buyer=Robert Chang, Location=Detroit, MI, Total=$1550.00, Items: gaming laptop, cooling pad",
    "Order 1020: Buyer=Sophie Martin, Location=Minneapolis, MN, Total=$72.30, Items: usb hub, ethernet adapter",
]


@app.route("/api/orders", methods=["GET"])
def get_orders():

    limit = request.args.get("limit", type=int)
    orders = ORDERS[:limit] if limit else ORDERS
    logger.info("Serving %d orders (limit=%s)", len(orders), limit)
    return jsonify({
        "status": "ok",
        "raw_orders": orders
    })


@app.route("/api/order/<order_id>", methods=["GET"])
def get_order_by_id(order_id):
    """
    Fetch a single order by scanning the text.
    """
    for text in ORDERS:
        if order_id in text:
            logger.info("Found order %s", order_id)
            return jsonify({
                "status": "ok",
                "raw_order": text
            })

    logger.warning("Order %s not found", order_id)
    return jsonify({"status": "not_found"}), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
