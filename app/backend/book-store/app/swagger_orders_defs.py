# swagger_orders_defs.py

orders_get_all_doc = {
    'tags': ['Orders'],
    'summary': '获取所有订单',
    'description': '管理员权限。返回所有用户的订单列表。',
    'responses': {
        200: {
            'description': '订单列表',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string', 'example': 'user1'},
                        'book_id': {'type': 'string', 'example': 'BK000123'},
                        'created_at': {'type': 'string', 'format': 'date-time', 'example': '2025-07-10T12:34:56Z'}
                    }
                }
            }
        },
        500: {
            'description': '服务器错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'details': {'type': 'string'}
                }
            }
        }
    },
    'security': [{'BearerAuth': []}]
}

orders_get_my_doc = {
    'tags': ['Orders'],
    'summary': '获取当前用户的订单',
    'description': '返回当前登录用户的所有订单。',
    'responses': {
        200: {
            'description': '当前用户订单列表',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'book_id': {'type': 'string', 'example': 'BK000123'},
                        'created_at': {'type': 'string', 'format': 'date-time', 'example': '2025-07-10T12:34:56Z'}
                    }
                }
            }
        },
        500: {
            'description': '服务器错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'details': {'type': 'string'}
                }
            }
        }
    },
    'security': [{'BearerAuth': []}]
}

orders_create_doc = {
    'tags': ['Orders'],
    'summary': '创建新订单',
    'description': '为当前用户创建一个新的书籍订单。',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['book_id'],
                'properties': {
                    'book_id': {'type': 'string', 'example': 'BK000123'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': '订单创建成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string', 'example': 'user1'},
                    'book_id': {'type': 'string', 'example': 'BK000123'},
                    'created_at': {'type': 'string', 'format': 'date-time'}
                }
            }
        },
        400: {
            'description': '请求错误或订单已存在',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Order already exists'}
                }
            }
        },
        500: {
            'description': '服务器错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'details': {'type': 'string'}
                }
            }
        }
    },
    'security': [{'BearerAuth': []}]
}

orders_delete_doc = {
    'tags': ['Orders'],
    'summary': '删除当前用户的订单',
    'description': '删除当前用户对指定 book_id 的订单。',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'required': True,
            'type': 'string',
            'description': '要取消订单的书籍 ID'
        }
    ],
    'responses': {
        200: {
            'description': '订单删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Order deleted'}
                }
            }
        },
        404: {
            'description': '未找到订单',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Order not found'}
                }
            }
        },
        500: {
            'description': '服务器错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'},
                    'details': {'type': 'string'}
                }
            }
        }
    },
    'security': [{'BearerAuth': []}]
}
