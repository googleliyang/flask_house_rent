from . import house_print
from info.utils.commons import login_required
from flask import g, jsonify, request, current_app
from info.utils.response_code import RET
from info.models import Area, House, Facility
from info.utils.image_storage import storage
from sqlalchemy import and_
from info import db
from info import constants
from sqlalchemy import asc, desc
from datetime import datetime


@house_print.route('/houses', methods=['GET', 'POST'])
@login_required
def house():
    if request.method == 'GET':
        aid = request.args.get('aid')
        sd = request.args.get('sd')
        ed = request.args.get('ed')
        sk = request.args.get('sk')
        print(sk)
        # build query condition
        query = House.query
        if aid:
            query = House.query.filter(House.area_id == aid)
        if sk:
            if sk == 'price-inc':
                query = query.order_by(asc('price'))
            if sk == 'price-des':
                query = query.order_by(desc('price'))
            if sk == 'booking':
                query = query.order_by('orders')
            else:
                query = query.order_by(desc('id'))
        if all([sd, ed]):
            s_d = datetime.strptime(sd, "%Y-%m-%d")
            e_d = datetime.strptime(ed, "%Y-%m-%d")
            day = (e_d - s_d).days
            day = int(day)
            print('day is', day)
            query = query.filter(House.min_days <= day, House.max_days >= day)
        houses = query.all()
        # todo: here maybe should convert to list, forbidden return obj to front
        _l = []
        for i in houses:
            _l.append(i.to_basic_dict())
        res_data = dict(houses=_l)
        return jsonify(errno=RET.OK, errmsg='OK', data=res_data)

    title = request.json.get('title')
    price = request.json.get('price')
    area_id = request.json.get('area_id')
    address = request.json.get('address')
    room_count = request.json.get('room_count')
    acreage = request.json.get('acreage')
    capacity = request.json.get('capacity')
    unit = request.json.get('unit')
    beds = request.json.get('beds')
    deposit = request.json.get('deposit')
    min_days = request.json.get('min_days')
    max_days = request.json.get('max_days')
    facility = request.json.get('facility')
    house = House()
    house.user_id = g.user.id
    house.title = title
    house.price = price
    house.area_id = area_id
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.capacity = capacity
    house.unit = unit
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days
    for fac_id in facility:
        facility = Facility.query.get(fac_id)
        house.facilities.append(facility)
    # house.facilities = facility
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='存储房屋信息失败')
        # todo: if this house.id can workd ?
    return jsonify(errno=RET.OK, errmsg='OK', data={'house_id': house.id})


@house_print.route('/areas')
def area():
    areas = Area.query.all()
    # todo: here maybe should convert to list, forbidden return obj to front
    _l = []
    for i in areas:
        _l.append(i.to_dict())
    return jsonify(errno=RET.OK, errmsg='OK', data=_l)


@house_print.route('/houses/<id>/images', methods=['POST'])
def upload_house_img(id):
    print('ope id is %s' % id)
    house = House.query.filter(House.id == id).first()
    if not house:
        return jsonify(errno=RET.PARAMERR, errmsg='房屋未找到')
    img = request.files.get('house_image')
    if not img:
        return jsonify(errno=RET.PARAMERR, errmsg='请上传图片')
    try:
        img_name = storage(img.read())
    except Exception as e:
        current_app.looger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='图片上传云平台失败')
    house.index_image_url = img_name
    db.session.add(house)
    db.session.commit()
    data = {'url': constants.QINIU_DOMIN_PREFIX + img_name}
    return jsonify(errno=RET.OK, errmsg='OK', data=data)


@house_print.route('/houses/<id>')
def house_detail(id):
    house = House.query.filter(id == House.id).first()
    if not house:
        return jsonify(errno=RET.PARAMERR, errmsg='房屋未找到')
    res_data = dict(house=house.to_full_dict())
    return jsonify(errno=RET.OK, errmsg='OK', data=res_data)


@house_print.route('/houses/index')
def house_index():
    houses = House.query.all()
    _l = []
    for i in houses:
        _l.append(i.to_simple_dict())
    return jsonify(errno=RET.OK, errmsg='OK', data=_l)


@house_print.route('/houses')
def filter_house():
    aid = request.args.get('aid')
    sd = request.args.get('sd')
    ed = request.args.get('ed')
    sk = request.args.get('sk')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    try:
        page, per_page = int(page), int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数类型错误')
    _order = 'booking' if sk else ''
    # todo: order by & date deal
    paginate = House.query.filter(
        # todo defalut page return
        and_(House.aid == aid, House.create_time > sd,
             House.create_time < ed)).order_by(_order).paginate(
                 page, per_page, False).all()
    data = paginate.items
    total_page = paginate.pages
    current_page = paginate.page
    res_data = {
        'total_page': total_page,
        'current_page': current_page,
        'data': data
    }
    return jsonify(errno=RET.OK, errmsg='OK', data=res_data)


@house_print.route('/user/houses')
@login_required
def self_houses():
    user = g.user
    houses = House.query.filter(House.user_id == user.id).all()
    _l = []
    for i in houses:
        _l.append(i.to_basic_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data=_l)
