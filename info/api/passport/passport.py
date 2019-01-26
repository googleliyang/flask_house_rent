from . import passport_print
from flask import jsonify, request, make_response, session, current_app
from info.utils.response_code import RET, error_map
from info.models import User
from info.utils.captcha.captcha import captcha
# todo this db how to work for multiple import
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
import random


@passport_print.route('/session', methods=['post'])
def res_session():
    # todo: front json.stringnify data & get data origin type
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    if not all([mobile, password]):
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map.get(RET.PARAMERR)
        })
    # query data base
    return jsonify({'errno': RET.OK})


@passport_print.route('/imagecode')
def imagecode():
    img_code_id = request.args.get('cur')
    if not img_code_id:
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map.get(RET.PARAMERR)
        })
    _, text, img = captcha.generate_captcha()
    try:
        redis_store.setex('image_code_%s' % img_code_id,
                          constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno': RET.DBERR, 'errmsg': error_map[RET.DBERR]})
    res = make_response(img)
    # if not this, browser or postman will get image flow, only work on html img tag which always compile to imgage
    res.headers['Content-Type'] = 'image/jpg'
    return res


@passport_print.route('/smscode/')
def smscode():
    mobile = request.json.get('mobile')
    img_code_id = request.json.get('image_code')
    captcha_text = request.json.get('image_code_id')
    if not all([mobile, img_code_id, captcha_text]):
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map.get(RET.PARAMERR)
        })
    redis_captcha_text = redis_store.get('image_code_%s' % img_code_id)
    if not redis_captcha_text:
        return jsonify({
            'errno': RET.NODATA,
            'errmsg': error_map.get(RET.NODATA)
        })
    if redis_captcha_text.lower() != captcha_text.lower():
        return jsonify({'errno': RET.DATAERR, 'errmsg': '验证码错误'})
    # chcek if the mobile already register
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno': RET.DATAERR, 'errmsg': '查询用户失败'})
    # todo : same if user ?
    if user is not None:
        return jsonify({'errno': RET.DATAEXIST, 'errmsg': '用户已存在'})
    # send sms
    sms_code = '%6d' % random.randint(0, 999999)
    current_app.logger.info(('The %s sms code is %s' % mobile, sms_code))
    # todo: try ouside can get result ?
    try:
        ccp = CCP()
        # todo: what's the useful of the expires ? just info msg
        result = ccp.send_template_sms(
            mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno': RET.THIRDERR, 'errmsg': '发送短信异常'})
    if result is 0:
        return jsonify(errno=RET.OK, errmsg='发送成功')
    else:
        return jsonify(errno=RET.THIRDERR, errmsg='发送失败')


@passport_print.route('', methods=['post'])
def register():
    _params = ('mobile', 'phonecode', 'passwod')
    # todo: python func pass param
    [mobile, phonecode, password] = check_param(request, _params)
    # omit valit phone ...
    user = User.query.filter(User.mobile == mobile).first()
    if user:
        return jsonify({'errno': RET.DATAEXIST, 'errmsg': '手机号已注册'})
    mobile = redis_store.get(mobile)
    # todo: set get sms code
    user = User()
    user.mobile = mobile
    # todo hash ?
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno': RET.DBERR, 'errmsg': '保存数据失败'})
    return jsonify({'errno': RET.OK, 'errmsg': '注册成功'})


# todo: python param
def check_param(req, method='json', *args):
    assert args != None, 'The params at least two params'
    _params = []
    if method is 'json':
        for arg in args:
            param = req.json.get(arg)
            if param is None:
                return jsonify({
                    'errno': RET.PARAMERR,
                    'errmsg': error_map.get(RET.PARAMERR)
                })
            _params.append(param)
    return _params
