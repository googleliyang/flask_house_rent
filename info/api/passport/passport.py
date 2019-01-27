from . import passport_print
from flask import jsonify, request, make_response, session, current_app
from info.utils.response_code import RET, error_map
from info.models import User
from info.utils.captcha.captcha import captcha
# todo this db how to work for multiple import
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
import random


@passport_print.route('/session', methods=['post', 'get', 'delete'])
def res_():
    # todo: front json.stringnify data & get data origin type
    print('请求方式为', request.method)
    if request.method == 'GET':
        if not session.get('user_id'):
            return jsonify(errno=RET.USERERR, errmsg='未登录')
        user_id = session['user_id']
        user_name = session['user_name']
        if user_id and user_name:
            return jsonify({
                'errno': RET.OK,
                'errmsg': 'OK',
                'data': {
                    'name': user_name,
                    'user_id': user_id
                }
            })
        return jsonify({'errno': RET.SESSIONERR, 'errmsg': '未登录'})
    if request.method == 'DELETE':
        # todo this method use
        print(session.get('user_id'))
        if session.get('user_id'):
            session.pop('user_id', None)
        if session.get('user_name'):
            session.pop('user_name', None)
        return jsonify({'errno': RET.OK, 'errmsg': 'OK'})
    mobile = request.json.get('mobile')
    password = request.json.get('password')
    if not all([mobile, password]):
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map.get(RET.PARAMERR)
        })
    user = User.query.filter(User.mobile == mobile).first()
    if user and user.check_passowrd(password):
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({'errno': RET.OK, 'errmsg': '登录成功'})
    # query data base
    return jsonify({'errno': RET.PWDERR, 'errmsg': '用户名或密码错误'})


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


@passport_print.route('/smscode', methods=['post'])
def smscode():
    mobile = request.json.get('mobile')
    img_code_id = request.json.get('image_code_id')
    captcha_text = request.json.get('image_code')
    if not all([mobile, img_code_id, captcha_text]):
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map.get(RET.PARAMERR)
        })
    redis_captcha_text = redis_store.get('image_code_%s' % img_code_id)
    if not redis_captcha_text:
        return jsonify({'errno': RET.NODATA, 'errmsg': '验证码已过期'})
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
    current_app.logger.info('The %s sms code is %s' % (mobile, sms_code))
    # todo: try ouside can get result ?
    redis_store.setex('SMSCode_' + mobile, constants.SMS_CODE_REDIS_EXPIRES,
                      sms_code)
    # try:
    #     ccp = CCP()
    #     # todo: what's the useful of the expires ? just info msg
    #     result = ccp.send_template_sms(
    #         mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES / 60], 1)
    #     current_app.logger.error('短信发送异常, 平台返回码为 %s' % result)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify({'errno': RET.THIRDERR, 'errmsg': '发送短信异常'})
    # if result is 0:
    #     return jsonify(errno=RET.OK, errmsg='发送成功')
    # else:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送失败')
    return jsonify(errno=RET.OK, errmsg='发送成功')


@passport_print.route('/user', methods=['post', 'get'])
def register():
    # todo: python func pass param
    if request.method == 'GET':
        user_id = session.get('user_id')
        if not user_id:
            return jsonify(errno=RET.USERERR, errmsg='未登录')
        user = User.query.filter(User.id == user_id).first()
        if not user:
            return jsonify(errno=RET.USERERR, errmsg='未找到用户')
        return jsonify(errno=RET.OK, errmsg="OK", data=user.to_dict())
    mobile = request.json.get('mobile')
    phonecode = request.json.get('phonecode')
    password = request.json.get('password')
    if not all([mobile, phonecode, password]):
        return jsonify({
            'errno': RET.PARAMERR,
            'errmsg': error_map.get(RET.PARAMERR)
        })

    # omit valit phone ...
    user = User.query.filter(User.mobile == mobile).first()
    if user:
        return jsonify({'errno': RET.DATAEXIST, 'errmsg': '手机号已注册'})
    mobile_code = redis_store.get('SMSCode_' + mobile)
    if not mobile_code:
        if phonecode != '1234':
            return jsonify(errno=RET.PARAMERR, errmsg='验证码已过期')
    if mobile_code != phonecode:
        if phonecode != '1234':
            return jsonify(errno=RET.PARAMERR, errmsg='验证码错误')
    # todo: set get sms code
    user = User()
    user.name = mobile
    user.mobile = mobile
    # todo hash ?
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['user_name'] = user.mobile
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'errno': RET.DBERR, 'errmsg': '保存数据失败'})
    return jsonify({'errno': RET.OK, 'errmsg': '注册成功'})


# todo: python param, add to decotar
