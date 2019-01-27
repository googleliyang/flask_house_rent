from . import user_blue
from info.utils.commons import login_required
from flask import jsonify, g, request, current_app
from info.utils.response_code import RET, error_map
from info.utils.image_storage import storage
from info import constants 
from info import db


@user_blue.route('/name')
@login_required
def _user():
    # check if login use decorator
    user = g.user
    return jsonify({
        "errmsg": 'OK',
        "errno": RET.OK,
        "data": {
            "avatar_url": user.avatar_url,
            "mobile": user.mobile,
            "name": user.name
        }
    })


@user_blue.route('/user/name', methods=['POST'])
@login_required
def _name():
    user = g.user
    user_name = request.json.get('name')
    if not user_name:
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map[RET.PARAMERR]
        })
    user.name = user_name
    db.session.add(user)
    db.session.commit()
    return jsonify({'errno': RET.OK, 'errmsg': 'OK'})


@user_blue.route('/user/avatar', methods=['POST'])
@login_required
def avatar():
    user = g.user
    avatar = request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
    try:
        # read img data
        img_data = avatar.read()
        img_name = storage(img_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传云平台失败')
    user.avatar_url = img_name
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.errror(e)
        return jsonify(errno=RET.DBERR, errmsg='数据存储失败')
    return jsonify(errno=RET.OK, errmsg='OK', data={
        'avatar_url': constants.QINIU_DOMIN_PREFIX+img_name
    }) 


# if work not split low and upper
@user_blue.route('/user/auth', methods=['get', 'post'])
@login_required
def user_real_name():
    user = g.user
    method = request.method
    if method == 'GET':
        return jsonify({
            'errno': RET.OK,
            'errmsg': 'OK',
            'data': {
                'real_name': user.real_name,
                'id_card': user.id_card
            }
        })
    real_name = request.json.get('real_name')
    id_card = request.json.get('id_card')
    if not all([real_name, id_card]):
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map.get(RET.PARAMERR)
        })
    user.real_name = real_name
    user.id_card = id_card
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存数据失败')
    return jsonify(errno=RET.OK, errmsg='OK')
