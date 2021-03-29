from datetime import timedelta
import requests
from _datetime import datetime
import dateutil.parser

Base = 'http://178.154.211.238/'


def delete_everything():
    res = requests.delete(Base + '/delete')

    answer_status_code = res.status_code
    right_answer_code = 204

    assert answer_status_code == right_answer_code, answer_status_code


def test_couriers_1():
    res = requests.post(Base + '/couriers',
                        json={
                            "data": [
                                {
                                    "courier_id": 1,
                                    "courier_type": "foot",
                                    "regions": [1, 12, 22],
                                    "working_hours": ["11:35-14:05",
                                                      "09:00-11:00"]
                                },
                                {
                                    "courier_id": 2,
                                    "courier_type": "bike",
                                    "regions": [22],
                                    "working_hours": ["09:00-18:00"]
                                },
                                {
                                    "courier_id": 3,
                                    "courier_type": "car",
                                    "regions": [12, 22, 23, 33],
                                    "working_hours": ["10:00-11:00"]
                                },

                            ]
                        }
                        )

    right_answer_json = {'couriers': [{'id': 1},
                                      {'id': 2},
                                      {'id': 3}
                                      ]
                         }

    assert res.status_code == 201, res.status_code
    assert res.json() == right_answer_json, res.json()


def test_couriers_2():
    res = requests.post(Base + '/couriers',
                        json={
                            "data": [
                                {
                                    "courier_id": 4,
                                    "courier_type": None,
                                    "regions": [22],
                                    "working_hours": ["09:00-18:00"]
                                },
                                {
                                    "courier_id": 5,
                                    "courier_type": "car",
                                    "regions": None,
                                    "working_hours": ["10:00-11:00"]
                                },
                                {
                                    "courier_id": 6,
                                    "courier_type": "car",
                                    "regions": [1, 13, 15],
                                    "working_hours": None
                                },
                                {
                                    "courier_id": 7,
                                    "courier_type": "foot",
                                    "regions": [1, 12, 22],
                                    "working_hours": ["11:35-14:05",
                                                      "09:00-11:00"]
                                },
                                {
                                    "courier_id": 8,
                                    "courier_type": "car",
                                    "regions": [1, 12, 22],
                                    "working_hours": ["11:35-14:05",
                                                      "09:00-11:00"]
                                },
                                {
                                    "courier_id": 9,
                                    "courier_type": "walk",
                                    "regions": [1, 12, 22],
                                    "working_hours": ["11:35-14:05",
                                                      "09:00-11:00"]
                                },
                                {
                                    "courier_id": 10,
                                    "courier_type": "foot",
                                    "regions": [1, 12, 22],
                                    "working_hours": ["11:35-14:05",
                                                      "09:00-11:00"]
                                },
                                {
                                    "courier_id": 11,
                                    "courier_type": "foot",
                                    "regions": [1, 12, 22],
                                    "working_hours": ["11:35-14:05",
                                                      "09:00-11:00"],
                                    'help': 123
                                },
                            ]
                        }
                        )
    expected_error_json = {'validation_error': {'couriers': [{'id': 4},
                                                             {'id': 5},
                                                             {'id': 6},
                                                             {'id': 9},
                                                             {'id': 11},
                                                             ]
                                                }
                           }

    assert res.status_code == 400, res.status_code
    assert res.json() == expected_error_json, res.json()

    res = requests.get(Base + '/couriers/3')
    assert res.status_code == 200, res.status_code

    res = requests.get(Base + '/couriers/4')
    assert res.status_code == 404, res.status_code

    res = requests.get(Base + '/couriers/7')
    assert res.status_code == 404, res.status_code


def test_orders_1():
    res = requests.post(Base + '/orders',
                        json={"data": [
                            {
                                "order_id": 1,
                                "weight": 0.23,
                                "region": 12,
                                "delivery_hours": ["09:00-18:00"]
                            },
                            {
                                "order_id": 2,
                                "weight": 15,
                                "region": 1,
                                "delivery_hours": ["09:00-18:00"]
                            },
                            {
                                "order_id": 3,
                                "weight": 0.01,
                                "region": 22,
                                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                            },
                            {
                                "order_id": 4,
                                "weight": 50,
                                "region": 22,
                                "delivery_hours": ["16:00-21:30"]
                            },
                        ]
                        })

    right_answer_json = {'orders': [{'id': 1},
                                    {'id': 2},
                                    {'id': 3},
                                    {'id': 4},
                                    ]
                         }

    assert res.status_code == 201, res.status_code
    assert res.json() == right_answer_json, res.json()


def test_orders_2():
    res = requests.post(Base + '/orders',
                        json={"data": [
                            {
                                "order_id": 5,
                                "weight": 0.001,
                                "region": 12,
                                "delivery_hours": ["09:00-18:00"]
                            },
                            {
                                "order_id": 6,
                                "weight": 59,
                                "region": 1,
                                "delivery_hours": ["09:00-18:00"]
                            },
                            {
                                "order_id": 7,
                                "weight": None,
                                "region": 22,
                                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                            },
                            {
                                "order_id": 8,
                                "weight": 13,
                                "region": None,
                                "delivery_hours": ["16:00-21:30"]
                            },
                            {
                                "order_id": 9,
                                "weight": 12,
                                "region": 80,
                                "delivery_hours": None
                            },
                            {
                                "order_id": 10,
                                "weight": 1.78,
                                "region": 81,
                                "delivery_hours": ["16:00-21:30"]
                            },
                            {
                                "order_id": 11,
                                "weight": 5.46,
                                "region": 48,
                                "delivery_hours": ["16:00-23:30"],
                                'help': 'help'
                            },
                        ]
                        })
    expected_error_json = {'validation_error': {'couriers': [{'id': 5},
                                                             {'id': 6},
                                                             {'id': 7},
                                                             {'id': 8},
                                                             {'id': 9},
                                                             {'id': 11},
                                                             ]
                                                }
                           }

    assert res.status_code == 400, res.status_code
    assert res.json() == expected_error_json, res.json()


def test_couriers_3():
    res = requests.post(Base + '/couriers',
                        json={
                            "data": [
                                {
                                    "courier_id": 1,
                                    "courier_type": "foot",
                                    "regions": [1, 12, 22, 33],
                                    "working_hours": ["11:35-14:05",
                                                      "09:00-11:00", "14:30-23:00", '00:00-06:00']
                                },
                                {
                                    "courier_id": 2,
                                    "courier_type": "bike",
                                    "regions": [22, 1, 23],
                                    "working_hours": ["09:00-23:00", '00:00-06:00']
                                },
                                {
                                    "courier_id": 3,
                                    "courier_type": "car",
                                    "regions": [12, 22, 23, 33, 1],
                                    "working_hours": ["08:00-23:00", '00:00-06:00']
                                },
                            ]
                        }
                        )
    right_answer_json = {'couriers': [{'id': 1},
                                      {'id': 2},
                                      {'id': 3}
                                      ]
                         }

    assert res.status_code == 201, res.status_code
    assert res.json() == right_answer_json, res.json()


def test_orders_3():
    res = requests.post(Base + '/orders',
                        json={"data": [
                            {
                                "order_id": 1,
                                "weight": 0.23,
                                "region": 12,
                                "delivery_hours": ["09:00-23:00", '00:00-06:00']
                            },
                            {
                                "order_id": 2,
                                "weight": 15,
                                "region": 1,
                                "delivery_hours": ["09:00-23:00", '00:00-06:00']
                            },
                            {
                                "order_id": 3,
                                "weight": 0.01,
                                "region": 22,
                                "delivery_hours": ["09:00-15:59", "16:00-22:30", '00:00-06:00']
                            },
                            {
                                "order_id": 4,
                                "weight": 50,
                                "region": 22,
                                "delivery_hours": ["18:01-22:30", '00:00-18:00']
                            },
                        ]
                        })
    right_answer_json = {'orders': [{'id': 1},
                                    {'id': 2},
                                    {'id': 3},
                                    {'id': 4},
                                    ]
                         }

    assert res.status_code == 201, res.status_code
    assert res.json() == right_answer_json, res.json()


def test_orders_assign_1():
    delete_everything()
    test_couriers_3()
    test_orders_3()
    res = requests.post(Base + '/orders/assign', json={"courier_id": 5})
    assert res.status_code == 400, res.status_code
    assert res.json() == {'message': 'Bad request'}, res.json()


def test_orders_assign_2():
    delete_everything()
    test_couriers_3()
    test_orders_3()
    now = datetime.now() - timedelta(hours=3)
    res = requests.post(Base + '/orders/assign', json={"courier_id": 1})
    right_answer_json = {
        "orders": [{"id": 3}, {"id": 1}],
        "assign_time": now.isoformat('T') + 'Z'
    }
    assert res.status_code == 200, res.status_code
    assert res.json()['orders'] == right_answer_json['orders'], res.json()
    minus = abs(dateutil.parser.isoparse(res.json()['assign_time']) - dateutil.parser.isoparse(
        right_answer_json['assign_time']))
    assert minus.seconds < 1, minus.seconds


def test_orders_assign_3():
    delete_everything()
    test_couriers_3()
    test_orders_3()
    now = datetime.now() - timedelta(hours=3)
    res = requests.post(Base + '/orders/assign', json={"courier_id": 2})
    answer_json = res.json()
    right_answer_json = {
        "orders": [{"id": 3}],
        "assign_time": now.isoformat('T') + 'Z'
    }
    assert res.status_code == 200, res.status_code
    assert answer_json['orders'] == right_answer_json['orders'], answer_json
    minus = abs(dateutil.parser.isoparse(answer_json['assign_time']) - dateutil.parser.isoparse(
        right_answer_json['assign_time']))
    assert minus.seconds < 1, answer_json['assign_time']


def test_orders_assign_4():
    delete_everything()
    test_couriers_3()
    test_orders_3()
    res = requests.post(Base + '/orders/assign', json={"courier_id": 1})
    assert res.status_code == 200, res.status_code

    now = datetime.now() - timedelta(hours=3)
    res = requests.post(Base + '/orders/assign', json={"courier_id": 2})
    answer_json = res.json()
    right_answer_json = {
        "orders": [{"id": 2}],
        "assign_time": now.isoformat('T') + 'Z'
    }
    assert res.status_code == 200, res.status_code
    assert answer_json['orders'] == right_answer_json['orders'], answer_json
    minus = abs(dateutil.parser.isoparse(answer_json['assign_time']) - dateutil.parser.isoparse(
        right_answer_json['assign_time']))
    assert minus.seconds < 1, 'something wrong with time'

    now = datetime.now() - timedelta(hours=3)
    res = requests.post(Base + '/orders/assign', json={"courier_id": 3})
    answer_json = res.json()
    right_answer_json = {
        "orders": [{"id": 4}],
        "assign_time": now.isoformat('T') + 'Z'
    }
    assert res.status_code == 200, res.status_code
    assert answer_json['orders'] == right_answer_json['orders'], answer_json
    minus = abs(dateutil.parser.isoparse(answer_json['assign_time']) - dateutil.parser.isoparse(
        right_answer_json['assign_time']))
    assert minus.seconds < 1, 'something wrong with time'


def test_orders_assign_5():
    delete_everything()
    test_couriers_3()
    test_orders_3()
    now = datetime.now() - timedelta(hours=3)
    res = requests.post(Base + '/orders/assign', json={"courier_id": 3})
    answer_json = res.json()
    right_answer_json = {
        "orders": [{"id": 3}, {"id": 1}, {"id": 2}],
        "assign_time": now.isoformat('T') + 'Z'
    }
    assert res.status_code == 200, res.status_code
    assert answer_json['orders'] == right_answer_json['orders'], answer_json
    minus = abs(dateutil.parser.isoparse(answer_json['assign_time']) - dateutil.parser.isoparse(
        right_answer_json['assign_time']))
    assert minus.seconds < 1, 'something wrong with time'


def test_orders_assign_6():
    delete_everything()
    test_couriers_3()
    res = requests.post(Base + '/orders/assign', json={"courier_id": 3})
    right_answer_json = {
        "orders": []
    }
    # There are no orders
    assert res.status_code == 200, res.status_code
    assert res.json() == right_answer_json, res.json()

    res = requests.post(Base + '/orders',
                        json={"data": [
                            {
                                "order_id": 1,
                                "weight": 0.233,
                                "region": 14,
                                "delivery_hours": ["09:00-23:00"]
                            }
                        ]
                        })
    # New one order
    assert res.status_code == 201, res.status_code
    assert res.json() == {'orders': [{'id': 1}]}, res.json()

    res = requests.post(Base + '/orders/assign', json={"courier_id": 3})
    right_answer_json = {
        "orders": []
    }
    # There are no orders because of the region and time
    assert res.status_code == 200, res.status_code
    assert res.json() == right_answer_json, res.json()

    res = requests.post(Base + '/orders',
                        json={"data": [
                            {
                                "order_id": 2,
                                "weight": 4.5,
                                "region": 33,
                                "delivery_hours": ["06:00-07:00"]
                            }
                        ]
                        })
    # New one order
    assert res.status_code == 201, res.status_code
    assert res.json() == {'orders': [{'id': 2}]}, res.json()

    res = requests.post(Base + '/orders/assign', json={"courier_id": 3})
    right_answer_json = {
        "orders": []
    }
    # There are no orders because of the time
    assert res.status_code == 200, res.status_code
    assert res.json() == right_answer_json, res.json()


def test_couriers():
    delete_everything()
    test_couriers_1()
    test_couriers_2()
    print('Everything is correct with POST couriers')


def test_orders():
    delete_everything()
    test_orders_1()
    print('Everything is correct with POST orders')


def test_orders_assign():
    test_orders_assign_1()
    test_orders_assign_2()
    test_orders_assign_3()
    test_orders_assign_4()
    test_orders_assign_5()
    test_orders_assign_6()
    print('Everything is correct with assign orders')


def test_orders_complete_1():
    delete_everything()
    test_couriers_3()
    test_orders_3()
    res = requests.post(Base + '/orders/complete', {
        "courier_id": 2,
        "order_id": 33,
        "complete_time": "2021-03-29T10:33:01.42Z"
    })
    # Order is not found
    right_answer_json = {
        'message': 'Bad Request'
    }
    assert res.status_code == 400, res.status_code
    assert res.json() == right_answer_json, res.json()

    res = requests.post(Base + '/orders/complete', {
        "courier_id": 2,
        "order_id": 1,
        "complete_time": "2021-03-29T10:33:01.42Z"
    })
    # Order is not assigned
    assert res.status_code == 400, res.status_code
    assert res.json() == right_answer_json, res.json()


def test_orders_complete_2():
    delete_everything()
    test_couriers_3()
    test_orders_3()
    res = requests.post(Base + '/orders/assign', json={"courier_id": 1})
    answer_json = res.json()
    right_answer_json = {
        "orders": [{"id": 3}, {"id": 1}]
    }
    assert res.status_code == 200, res.status_code
    assert answer_json['orders'] == right_answer_json['orders'], answer_json
    res = requests.post(Base + '/orders/complete', {
        "courier_id": 2,
        "order_id": 3,
        "complete_time": "2021-03-29T23:33:01.42Z"
    })
    # Order is assign to another courier
    right_answer_json = {
        'message': 'Bad Request'
    }
    assert res.status_code == 400, res.status_code
    assert res.json() == right_answer_json, res.json()

    res = requests.post(Base + '/orders/complete', {
        "courier_id": 1,
        "order_id": 3,
        "complete_time": "2021-03-29T23:58:01.42Z"
    })
    right_answer_json = {
        'order_id': 3
    }
    # Order is correct
    assert res.status_code == 200, res.status_code
    assert res.json() == right_answer_json, res.json()

    res = requests.get(Base + '/orders/3')
    assert res.status_code == 200, res.status_code
    assert res.json()['assign_time'] is not None, res.json()
    assert res.json()['complete_time'] is not None, res.json()


def test_orders_complete():
    test_orders_complete_1()
    test_orders_complete_2()
    print('Everything is correct with complete orders')


def test_couriers_patch_1():
    # Without assigned orders
    delete_everything()
    test_couriers_3()
    res = requests.patch(Base + '/couriers/3', json={
        "regions": [11, 33, 2]
    })
    answer_json = {
        "courier_id": 3,
        "courier_type": "car",
        "regions": [11, 33, 2],
        "working_hours": ["08:00-23:00", '00:00-06:00']
    }
    assert res.status_code == 200, res.status_code
    assert answer_json == res.json(), res.json()

    # there are no argument help in courier fields
    res = requests.patch(Base + '/couriers/3', json={
        "regions": [11, 33, 2, 5],
        'help': 123
    })
    assert res.status_code == 400, res.status_code

    res = requests.patch(Base + '/couriers/1', json={
        "courier_type": 'car',
        'working_hours': ["11:30-14:00", "09:00-11:20", "18:00-20:00"]
    })
    answer_json = {
        "courier_id": 1,
        "courier_type": "car",
        "regions": [1, 12, 22, 33],
        "working_hours": ["11:30-14:00", "09:00-11:20", "18:00-20:00"]
    }
    assert res.status_code == 200, res.status_code
    assert res.json() == answer_json, res.json()


def test_couriers_patch_2():
    delete_everything()
    # The same couriers and assigned orders number 1 and 3 for courier 1
    # order 2 for courier 2 and order 4 for courier 3
    test_orders_assign_4()

    # What if we change the region of courier 1
    # He may lose some of his orders, in this case he will lose order number 3
    res = requests.patch(Base + '/couriers/1', json={
        "regions": [12, 33]
    })
    assert res.status_code == 200, res.status_code
    # We can see what orders that courier have now
    res = requests.post(Base + '/orders/assign', json={"courier_id": 1})
    assert res.status_code == 200, res.status_code
    right_answer_json = {
        "orders": [{"id": 1}]
    }
    assert res.json()['orders'] == right_answer_json['orders'], res.json()

    # switch the type of courier 3 and assign to it new order
    res = requests.patch(Base + '/couriers/3', json={
        "courier_type": 'bike'
    })
    res = requests.get(Base + '/couriers/3')
    assert res.json()['earnings'] == 0, res.json()['earnings']
    assert res.status_code == 200, res.status_code

    # Check that order 4 is free
    res = requests.get(Base + '/orders/4')
    assert res.json()['assign_time'] is None, res.json()

    res = requests.post(Base + '/orders/assign', json={"courier_id": 3})
    right_answer_json = {
        "orders": [{'id': 3}]
    }
    assert res.status_code == 200, res.status_code
    assert res.json()['orders'] == right_answer_json['orders'], res.json()
    res = requests.get(Base + '/couriers/3')
    assert res.json()['earnings'] == 0, res.json()['earnings']


def test_couriers_patch_3():
    delete_everything()
    test_orders_assign_4()

    # We can switch time of 3rd courier and because of this he will lose his order
    res = requests.patch(Base + '/couriers/3', json={
        "courier_type": 'bike'
    })
    assert res.status_code == 200, res.status_code
    res = requests.post(Base + '/orders/assign', json={"courier_id": 3})
    assert res.status_code == 200, res.status_code
    right_answer_json = {
        "orders": []
    }
    assert res.json()['orders'] == right_answer_json['orders'], res.json()


def test_couriers_patch_4():
    delete_everything()
    test_orders_assign_4()

    # We can switch time of 3rd courier and because of this he will lose his order
    res = requests.patch(Base + '/couriers/2', json={
        "working_hours": ['7:00-8:00']
    })
    assert res.status_code == 200, res.status_code
    res = requests.post(Base + '/orders/assign', json={"courier_id": 2})
    assert res.status_code == 200, res.status_code
    right_answer_json = {
        "orders": []
    }
    assert res.json()['orders'] == right_answer_json['orders'], res.json()


def test_couriers_patch():
    test_couriers_patch_1()
    test_couriers_patch_2()
    test_couriers_patch_3()
    test_couriers_patch_4()
    print('Everything is correct with PATCH couriers')


def test_couriers_rating_1():
    delete_everything()
    now = datetime.now() - timedelta(hours=3)
    test_orders_assign_4()

    complete_time = now + timedelta(minutes=15)
    res = requests.post(Base + '/orders/complete', {
        "courier_id": 1,
        "order_id": 1,
        "complete_time": complete_time.isoformat('T') + 'Z'
    })
    right_answer_json = {
        'order_id': 1
    }
    assert res.status_code == 200, res.status_code
    assert res.json() == right_answer_json, res.json()

    res = requests.get(Base + '/couriers/1')

    assert res.status_code == 200, res.status_code
    assert abs(res.json()['rating'] - 3.75) < 0.1, res.json()['rating']
    assert res.json()['earnings'] == 0, res.json()['earnings']
    complete_time = now + timedelta(minutes=25)
    res = requests.post(Base + '/orders/complete', {
        "courier_id": 1,
        "order_id": 3,
        "complete_time": complete_time.isoformat('T') + 'Z'
    })
    right_answer_json = {
        'order_id': 3
    }
    assert res.status_code == 200, res.status_code
    assert res.json() == right_answer_json, res.json()

    res = requests.get(Base + '/couriers/1')
    assert res.status_code == 200, res.status_code
    assert abs(res.json()['rating'] - 4.16) < 0.1, res.json()['rating']
    assert res.json()['earnings'] == 1000, res.json()['earnings']


def test_couriers_rating():
    test_couriers_rating_1()
    print('Everything is correct with rating')


if __name__ == '__main__':
    test_couriers()
    test_orders()
    test_orders_assign()
    test_orders_complete()
    test_couriers_patch()
    test_couriers_rating()
