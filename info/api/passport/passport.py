from . import passport_print
from flask import jsonify
from info.utils.response_code import RET


@passport_print.route('/session', methods=['post'])
def session():
    return jsonify({
        'errno': RET.OK
    })
