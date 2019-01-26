from . import passport_print
from flask import jsonify
from info.utils.response_code import RET


@passport_print.route('/session')
def session():
    return jsonify({
        'status': RET.UNKOWNERR
    })
