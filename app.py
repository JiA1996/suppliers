import os
import logging
from typing import Tuple
from flask import Flask, jsonify, Response, request
from models.supplier import Supplier
from exceptions.supplier_exception import MissingContactInfo, MissingProductId, WrongArgType, OutOfRange
from database.database import Database

######################################################################
# Get bindings from the environment
######################################################################
DEBUG = os.getenv("DEBUG", "False") == "True"
PORT = os.getenv("PORT", "5000")


######################################################################
# Create Flask application
######################################################################
app = Flask(__name__)
if DEBUG:
    app.logger.setLevel(logging.DEBUG)
else:
    app.logger.setLevel(logging.INFO)


######################################################################
# Storage for Suppliers
######################################################################
suppliers = {}
database = Database()


######################################################################
# Application Routes
######################################################################
@app.route("/")
def index() -> Tuple[Response, int]:
    """ Returns a message about the service """
    app.logger.info("Request for Index page")
    return (
        jsonify(
            name="Supplier"
        ),
        200,
    )


@app.route("/supplier", methods=["PUT"])
def create_supplier() -> Tuple[Response, int]:
    """ Creates a supplier and returns the ID """
    request_body = request.json
    app.logger.info("request body: {}".format(request_body))
    if request_body is None:
        app.logger.info("bad request")
        return error_response("no request body", 400)
    if "name" not in request_body:
        return error_response("missing name", 400)
    new_name = request_body["name"]
    new_email = request_body["email"] if "email" in request_body else ""
    new_address = request_body["address"] if "address" in request_body else ""
    new_products = list(request_body["products"].values()) if "products" in request_body else []
    try:
        new_supplier = Supplier(
            name=new_name,
            email=new_email,
            address=new_address,
            products=new_products
        )
        created_supplier = database.create_supplier(new_supplier)
        app.logger.info(
            "created new supplier with id {}".format(created_supplier.id))
    except (MissingContactInfo, MissingProductId, WrongArgType, OutOfRange) as e:
        return error_response(str(e), 400)
    return jsonify(id=created_supplier.id), 201


@app.route("/supplier/<int:supplier_id>", methods=["GET"])
def read_supplier(supplier_id) -> Tuple[Response, int]:
    """ Reads a supplier by the id. """
    app.logger.info('Reads a supplier with id: {}'.format(supplier_id))
    supplier = database.find(supplier_id)
    if not supplier:
        not_found_msg = "Supplier with id: {} was not found".format(supplier_id)
        app.logger.info(not_found_msg)
        return error_response(not_found_msg, 404)
    # if found
    found_msg = "Supplier with id: {} was found".format(supplier_id)
    app.logger.info(found_msg)
    return jsonify(id=supplier.id), 200


@app.route("/supplier/<int:supplier_id>", methods=["POST"])
def update_supplier(supplier_id) -> Tuple[Response, int]:
    """ Updates a supplier by the id and returns the id """
    app.logger.info('Updates a supplier with id: {}'.format(supplier_id))
    supplier = database.find(supplier_id)
    if not supplier:
        not_found_msg = "Supplier with id: {} was not found".format(supplier_id)
        app.logger.info(not_found_msg)
        return error_response(not_found_msg, 404)
    # if found, update the supplier
    found_msg = "Supplier with id: {} was found".format(supplier_id)
    app.logger.info(found_msg)
    request_body = request.json
    app.logger.info("request body: {}".format(request_body))
    if request_body is None:
        app.logger.info("bad request")
        return error_response("no request body", 400)
    if "name" not in request_body:
        return error_response("missing name", 400)
    new_name = request_body["name"]
    new_email = request_body["email"] if "email" in request_body else ""
    new_address = request_body["address"] if "address" in request_body else ""
    new_products = list(request_body["products"].values()) if "products" in request_body else []
    try:
        supplier.name = new_name
        # if the new property is not empty, update the corresponding property
        if new_email:
            supplier.email = new_email
        if new_address:
            supplier.address = new_address
        if new_products:
            supplier.products = new_products
        app.logger.info("updated the supplier with id {}".format(supplier_id))
    except (MissingContactInfo, MissingProductId, WrongArgType, OutOfRange) as e:
        return error_response(str(e), 400)
    return jsonify(id=supplier_id), 200

######################################################################
#   Convenience functions
######################################################################


def error_response(msg: str, error_code: int) -> Tuple[Response, int]:
    return jsonify(
        error=msg
    ), error_code


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    app.logger.info("*" * 70)
    app.logger.info("   Seleton Flask For Supplier   ".center(70, "*"))
    app.logger.info("*" * 70)
    app.run(host="0.0.0.0", port=int(PORT), debug=DEBUG)
