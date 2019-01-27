from flask import Blueprint

order_print = Blueprint('order_print', __name__)

from . import order

