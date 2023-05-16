from flask import jsonify

STATUS_SUCCESS = 'success'
STATUS_FAIL = 'fail'


def create_response(status=STATUS_SUCCESS, message="", data={}):
    return jsonify({
        'status': status,
        'message': message,
        'data': data,
    })
