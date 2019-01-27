from . import order_print
from flask import request, jsonify, current_app, g
from info.models import Order, House
from info import db
from info.utils.response_code import RET, error_map
from info.utils.commons import login_required
from datetime import datetime


@order_print.route('/orders', methods=['POST', 'GET', 'PUT'])
@login_required
def order():
    if request.method == 'GET':
        role = request.args.get('role')
        # by user id get houses
        # by houses get order
        if not role:
            return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')
        user = g.user
        _l = []
        # orders = []
        if role == 'landlord':
            houses = user.houses
            for house in houses:
                orders = Order.query.filter(Order.house_id == house.id)
                for order in orders:
                    _l.append(order.to_dict())
        else:
            orders = user.orders
            for order in orders:
                _l.append(order.to_dict())
        res_data = dict(orders=_l)
        return jsonify(errno=RET.OK, errmsg='OK', data=res_data)
    if request.method == 'PUT':
        action = request.json.get('action')
        order_id = request.json.get('order_id')
        reason = request.json.get('reason')
        if not all([action, order_id]):
            return jsonify(
                errno=RET.PARAMERR, errmsg=error_map.get(RET.PARAMERR))
        order = Order.query.filter(Order.id == order_id).first()
        order.order_id = order_id
        if action == 'reject':
            order.comment = reason
            order.status = 'REJECTED'
        elif action == 'accept':
            order.status = 'COMPLETE'
        try:
            order.user_id = g.user.id
            db.session.add(order)
            db.session.commit()
            return jsonify(errno=RET.OK, errmsg='OK')
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='订单保存失败')
    house_id = request.json.get('house_id')
    start_date = request.json.get('start_date')
    end_date = request.json.get('end_date')
    if not all([house_id, start_date, end_date]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])
    order = Order()
    order.house_id = house_id
    order.user_id = g.user.id
    order.begin_date = start_date
    order.end_date = end_date
    s_d = datetime.strptime(start_date, "%Y-%m-%d")
    e_d = datetime.strptime(end_date, "%Y-%m-%d")
    day = (e_d - s_d).days
    print('--' * 10, day)
    try:
        day = int(day)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='日期格式错误')
    order.days = day
    house = House.query.filter(House.id == house_id).first()
    if not house:
        return jsonify(errno=RET.PARAMERR, errmsg='找不到房屋')
    order_price = house.price * day if house.price * day else house.price
    order.house_price = house.price
    order.amount = order_price
    print('*' * 100, day)
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='订单保存失败')
    res_data = {'order_id': order.id}
    return jsonify(errno=RET.OK, errmsg='OK', data=res_data)

    @order.print.route('/orders/comment', methods=['PUT'])
    def order_comment():
        comment = request.json.get('comment')
        order_id = request.json.get('order_id')
        if not all([comment, order_id]):
            return jsonify(
                errno=RET.PARAMERR, errmsg=error_map.get(RET.PARAMERR))
        order = Order.query.filter(Order.id == order_id)
        if not order:
            return jsonify(errno=RET.PARAMERR, errmsg='订单未找到')
        order.comment = comment
        try:
            db.session.add(order)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='订单保存失败')
        return jsonify(errno=RET.OK, errmsg='OK')
