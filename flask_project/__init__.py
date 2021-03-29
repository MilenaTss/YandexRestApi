from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime
import dateutil.parser

# The application that I will run and connection to database
app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///delivery.db'
delivery = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


# models with data which I will use
class CourierModel(delivery.Model):
    courier_id = delivery.Column(delivery.Integer, primary_key=True)
    courier_type = delivery.Column(delivery.String, nullable=False)
    regions = delivery.Column(delivery.String, nullable=False)
    working_hours = delivery.Column(delivery.String, nullable=False)

    # Sum of times in region and number of times in region (to calculate average time).
    # Also we remember minimal average time
    amount_per_district = delivery.Column(delivery.String, nullable=False)
    num_of_orders_per_district = delivery.Column(delivery.String, nullable=False)
    min_average_time = delivery.Column(delivery.Integer, nullable=True)

    earnings = delivery.Column(delivery.Integer, nullable=False)

    # We need to remember the type of courier, if we did patch to courier
    # Because we have to remove the salary that has not yet been received,
    # if the courier has not yet finished his orders
    # and we remove exactly the salary that was given to him at the very beginning
    was_type_of_courier = delivery.Column(delivery.String, nullable=True)

    def __repr__(self):
        return f'courier({self.courier_id})'


class OrderModel(delivery.Model):
    order_id = delivery.Column(delivery.Integer, primary_key=True)
    weight = delivery.Column(delivery.Numeric, nullable=False)
    region = delivery.Column(delivery.Integer, nullable=False)
    delivery_hours = delivery.Column(delivery.String, nullable=False)
    courier_id = delivery.Column(delivery.Integer, nullable=True)

    # I keep the time of assign order, the time then orders/assign was requested
    # And completed time. If order wasn't assigned assign_time is None
    assign_time = delivery.Column(delivery.String, nullable=True)
    complete_time = delivery.Column(delivery.String, nullable=True)


delivery.create_all()

# Parsers of given json object
orders_assign_fields = reqparse.RequestParser()
orders_assign_fields.add_argument('courier_id', type=int)

orders_complete_fields = reqparse.RequestParser()
orders_complete_fields.add_argument('courier_id', type=int)
orders_complete_fields.add_argument('order_id', type=int)
orders_complete_fields.add_argument('complete_time', type=str)

# Json for marshal_with, to return correct data
courier_get_fields = {
    'courier_id': fields.Integer,
    'courier_type': fields.String,
    'regions': fields.List(fields.Integer),
    'working_hours': fields.List(fields.String),
    'rating': fields.Float,
    'earnings': fields.Integer
}

courier_patch_fields = {
    'courier_id': fields.Integer,
    'courier_type': fields.String,
    'regions': fields.List(fields.Integer),
    'working_hours': fields.List(fields.String)
}

order_get_fields = {
    'order_id': fields.Integer,
    'weight': fields.Float,
    'region': fields.Integer,
    'courier_id': fields.Integer,
    'assign_time': fields.String,
    'complete_time': fields.String
}


def salary_ratio(s1):
    if s1 == 'foot':
        return 2
    if s1 == 'bike':
        return 5
    if s1 == 'car':
        return 9


def max_weight_from_type(s1):
    if s1 == 'foot':
        return 10
    if s1 == 'bike':
        return 15
    if s1 == 'car':
        return 50
    return 0


def time_from_string(s1, now):
    date = s1.split('-')
    datetime_begin = datetime.strptime(date[0], "%H:%M")
    datetime_end = datetime.strptime(date[1], "%H:%M")
    datetime_begin = datetime_begin.replace(year=now.year, month=now.month, day=now.day)
    datetime_end = datetime_end.replace(year=now.year, month=now.month, day=now.day)
    if datetime_begin <= now < datetime_end:
        return True
    return False


courier_types = ['foot', 'bike', 'car']


class Courier(Resource):
    @marshal_with(courier_get_fields)
    def get(self, courier_id):
        courier = CourierModel.query.filter_by(courier_id=courier_id).first()
        if not courier:
            abort(404, message='There are no courier with this id')
        min_average_time = courier.min_average_time
        # if there are no completed orders and else
        rating = None
        if min_average_time is not None:
            rating = (60 * 60 - min(min_average_time, 60 * 60)) / (60 * 60) * 5
            rating = round(rating, 2)

        # if there are incomplete orders then we need to decrease earnings because we increased it in assign
        orders = OrderModel.query.filter_by(courier_id=courier_id).filter(OrderModel.assign_time.isnot(None)).filter(
            OrderModel.complete_time.is_(None)).all()
        earnings_now = courier.earnings
        if len(orders) > 0:
            if courier.was_type_of_courier is not None:
                earnings_now -= 500 * salary_ratio(courier.was_type_of_courier)
            else:
                earnings_now -= 500 * salary_ratio(courier.courier_type)
        res_json = {
            'courier_id': courier_id,
            'courier_type': courier.courier_type,
            'regions': json.loads(courier.regions),
            'working_hours': json.loads(courier.working_hours),
            'rating': rating,
            'earnings': earnings_now
        }
        return res_json, 200

    @marshal_with(courier_patch_fields)
    def patch(self, courier_id):
        args = request.get_json(force=True)
        courier = CourierModel.query.filter_by(courier_id=courier_id).first()
        # We need to calculate num of arguments to find out if there are any extra arguments
        # And with that we change data in tables
        num_of_args = 0
        if not courier:
            abort(400, message='Bad request')
        if 'courier_type' in args:
            if args['courier_type'] not in courier_types:
                abort(400, message='Bad request')
            courier.courier_type = args['courier_type']
            num_of_args += 1
        if 'regions' in args:
            courier.regions = json.dumps(args['regions'])
            num_of_args += 1
        if 'working_hours' in args:
            courier.working_hours = json.dumps(args['working_hours'])
            num_of_args += 1
        if num_of_args < len(args):
            abort(400)

        # Now we need to remove unnecessary orders that are now not suitable by weight, region, time
        # We choose orders that are assign but not completed and belong to this courier
        courier_regions = json.loads(courier.regions)
        sum_weight = 0
        max_weight = max_weight_from_type(courier.courier_type)
        current_orders = OrderModel.query.filter_by(courier_id=courier_id).filter(
            OrderModel.assign_time.isnot(None)).filter(
            OrderModel.complete_time.is_(None)).order_by(OrderModel.weight).all()
        now = datetime.now()

        current_time_courier = 0
        for i in json.loads(courier.working_hours):
            if time_from_string(i, now):
                current_time_courier = i
                break

        for order in current_orders:
            delivery_hours = json.loads(order.delivery_hours)
            current_time_order = 0
            for i in delivery_hours:
                if time_from_string(i, now):
                    current_time_order = i
                    break
            if current_time_order != 0 and current_time_courier != 0 and order.region in courier_regions \
                    and sum_weight + order.weight <= max_weight:
                sum_weight += order.weight
            else:
                order.assign_time = None
        # We need to understand does the courier have salary or not
        if len(current_orders) > 0 and sum_weight == 0:
            finished_orders = OrderModel.query.filter_by(assign_time=current_orders[0].assign_time).filter(
                OrderModel.complete_time.isnot(None)).all()
            if len(finished_orders) == 0:
                # Забрать у него зарплату
                if courier.was_type_of_courier is None:
                    courier.earnings -= 500 * salary_ratio(courier.courier_type)
                else:
                    courier.earnings -= 500 * salary_ratio(courier.was_type_of_courier)

        delivery.session.commit()
        res_json = {
            'courier_id': courier_id,
            'courier_type': courier.courier_type,
            'regions': json.loads(courier.regions),
            'working_hours': json.loads(courier.working_hours)
        }
        return res_json, 200


class PostCourier(Resource):
    def post(self):
        args = request.get_json(force=True)
        couriers = {'couriers': []}
        errors = {'couriers': []}

        if len(args) != 1 or 'data' not in args:
            abort(400, message='Bad request')

        for courier in args['data']:
            # We check the correctness of all the fields and that there are no extra fields
            if courier['courier_id'] and courier['courier_type'] and courier['regions'] \
                    and courier['working_hours'] and courier['courier_type'] in courier_types \
                    and len(courier) == 4:
                num_of_regions = len(courier['regions'])
                courier_ = CourierModel(courier_id=courier['courier_id'], courier_type=courier['courier_type'],
                                        regions=json.dumps(courier['regions']),
                                        working_hours=json.dumps(courier['working_hours']),
                                        amount_per_district=json.dumps([0] * num_of_regions),
                                        num_of_orders_per_district=json.dumps([0] * num_of_regions), earnings=0)
                couriers['couriers'].append({'id': courier['courier_id']})
                delivery.session.add(courier_)
            else:
                errors['couriers'].append({'id': courier['courier_id']})
        # If there are no errors in given data
        if len(errors['couriers']) == 0:
            delivery.session.commit()
            return couriers, 201
        else:
            er = {'validation_error': errors}
            return er, 400


class PostOrder(Resource):
    def post(self):
        args = request.get_json(force=True)
        orders = {'orders': []}
        errors = {'orders': []}

        if len(args) != 1 or 'data' not in args:
            abort(400, message='Bad request')

        for order in args['data']:
            # We check the correctness of all the fields and that there are no extra fields
            if order['order_id'] and order['weight'] and order['region'] and order['delivery_hours'] \
                    and 0.01 <= order['weight'] <= 50 and len(order) == 4:
                order_ = OrderModel(order_id=order['order_id'], weight=round(order['weight'],2), region=order['region'],
                                    delivery_hours=json.dumps(order['delivery_hours']))
                orders['orders'].append({'id': order['order_id']})
                delivery.session.add(order_)
            else:
                errors['orders'].append({'id': order['order_id']})
        # If there are no errors in given data
        if len(errors['orders']) == 0:
            delivery.session.commit()
            return orders, 201
        else:
            er = {'validation_error': errors}
            return er, 400


class OrdersAssign(Resource):
    def post(self):
        args = orders_assign_fields.parse_args()
        courier_id = args['courier_id']

        courier = CourierModel.query.filter_by(courier_id=courier_id).first()
        if not courier:
            abort(400, message='Bad request')

        result_json = {'orders': [], 'assign_time': ''}

        # The handler must be idempotent. And because of this I think that we can't assign new order
        # if there are incomplete orders. And if we try this we need to return assigned and incomplete orders
        incomplete_orders = OrderModel.query.filter_by(courier_id=courier_id).filter(
            OrderModel.assign_time.isnot(None)).filter(
            OrderModel.complete_time.is_(None)).all()
        if len(incomplete_orders) > 0:
            for i in incomplete_orders:
                result_json['orders'].append({'id': i.order_id})
                result_json['assign_time'] = i.assign_time
            return result_json, 200

        # Another case if there are no assigned (and incomplete) orders
        regions = json.loads(courier.regions)
        working_hours = json.loads(courier.working_hours)

        now = datetime.now()
        current_time_courier = 0
        # I think that we need to assign orders only in current time interval
        # And because of this I choose in all courier working intervals the one that continues now
        for i in working_hours:
            if time_from_string(i, now):
                current_time_courier = i
                break
        # If courier doesn't work now
        if current_time_courier == 0:
            return {'orders': []}

        sum_weight = 0
        max_weight = max_weight_from_type(courier.courier_type)

        orders = OrderModel.query.filter(OrderModel.region.in_(regions)).filter(
            OrderModel.assign_time.is_(None)).order_by(OrderModel.weight).all()

        # We chose not assigned orders and try to assign them to this courier if they're suitable
        for order in orders:
            delivery_hours = json.loads(order.delivery_hours)

            current_time_order = 0
            for i in delivery_hours:
                if time_from_string(i, now):
                    current_time_order = i
                    break

            if current_time_order != 0 and sum_weight + order.weight <= max_weight:
                sum_weight += order.weight

                order.assign_time = now.isoformat('T') + 'Z'
                order.courier_id = courier_id
                result_json['orders'].append({'id': order.order_id})

                if sum_weight + order.weight > max_weight:
                    break
        # We assigned all orders and need to return them

        result_json['assign_time'] = now.isoformat('T') + 'Z'
        if len(result_json['orders']) == 0:
            return {'orders': []}
        # Giving a salary for this order.
        courier.was_type_of_courier = None
        courier.earnings += 500 * salary_ratio(courier.courier_type)

        if courier.was_type_of_courier is None:
            courier.was_type_of_courier = courier.courier_type

        delivery.session.commit()
        return result_json, 200


class OrdersComplete(Resource):
    def post(self):
        args = orders_complete_fields.parse_args()
        order = OrderModel.query.filter_by(order_id=args['order_id']).first()

        # Check that everything in data is correct
        if not order or order.courier_id != args['courier_id'] or order.assign_time is None:
            abort(400, message='Bad Request')

        # We need to find the last completed order to know when the delivery of this order starts
        last_order = OrderModel.query.order_by(OrderModel.complete_time.desc()).first()

        if last_order.complete_time is None:
            time_of_start = order.assign_time
        else:
            time_of_start = max(last_order.complete_time, order.assign_time)

        time_of_start = dateutil.parser.isoparse(time_of_start)
        time_of_end = dateutil.parser.isoparse(args['complete_time'])

        time_of_delivery = time_of_end - time_of_start
        seconds_in_day = 24 * 60 * 60
        time_of_delivery = time_of_delivery.days * seconds_in_day + time_of_delivery.seconds

        # We need to remember how long the order lasted, and add it to the data for curr region
        # This is necessary in order to correctly calculate the rating.
        courier = CourierModel.query.filter_by(courier_id=args['courier_id']).first()
        regions = json.loads(courier.regions)
        index_of_region = regions.index(order.region)

        # Sum of delivery times in region
        amount_per_district_ = json.loads(courier.amount_per_district)
        amount_per_district_[index_of_region] += time_of_delivery
        courier.amount_per_district = json.dumps(amount_per_district_)

        # Number of orders in region
        num_of_orders_per_district_ = json.loads(courier.num_of_orders_per_district)
        num_of_orders_per_district_[index_of_region] += 1
        courier.num_of_orders_per_district = json.dumps(num_of_orders_per_district_)

        new_average_time = amount_per_district_[index_of_region] / num_of_orders_per_district_[index_of_region]

        # Update min average time among the region
        if courier.min_average_time is None:
            courier.min_average_time = new_average_time
        else:
            courier.min_average_time = min(courier.min_average_time, new_average_time)

        order.complete_time = args['complete_time']
        delivery.session.commit()
        return {'order_id': args['order_id']}, 200


class GetOrder(Resource):
    @marshal_with(order_get_fields)
    def get(self, order_id):
        order = OrderModel.query.filter_by(order_id=order_id).first()
        if order is None:
            abort(404, message='Something went wrong')
        res = {
            'order_id': order.order_id,
            'weight': order.weight,
            'region': order.region,
            'courier_id': order.courier_id,
            'assign_time': order.assign_time,
            'complete_time': order.complete_time
        }
        return res, 200


class Deleted(Resource):
    def delete(self):
        orders = OrderModel.query.all()
        for order in orders:
            delivery.session.delete(order)
        couriers = CourierModel.query.all()
        for cour in couriers:
            delivery.session.delete(cour)
        delivery.session.commit()
        return '', 204


api.add_resource(Courier, "/couriers/<int:courier_id>")
api.add_resource(PostCourier, "/couriers")
api.add_resource(PostOrder, "/orders")
api.add_resource(OrdersAssign, '/orders/assign')
api.add_resource(OrdersComplete, '/orders/complete')
api.add_resource(GetOrder, "/orders/<int:order_id>")
api.add_resource(Deleted, '/delete')

if __name__ == '__main__':
    app.run(debug=False)
