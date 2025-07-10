# books
books_get_doc = {
    'tags': ['Books'],
    'summary': '获取所有书籍',
    'responses': {
        200: {
            'description': '返回所有书籍列表',
            'schema': {
                'type': 'object',
                'properties': {
                    'books': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'book_id': {
                                    'type': 'string',
                                    'example': '60f7b0b6e13a4b3e2f4a6789'
                                },
                                'title': {
                                    'type': 'string',
                                    'example': 'Book Title'
                                },
                                'author': {
                                    'type': 'string',
                                    'example': 'Author Name'
                                },
                                'description': {
                                    'type': 'string',
                                    'example': 'This is a book about...'
                                }
                            }
                        }
                    }
                }
            }
        },
        504: {
            'description': '查询超时',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Query timed out'
                    }
                }
            }
        },
        500: {
            'description': '数据库错误',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'MongoDB query error'
                    }
                }
            }
        }
    }
}

books_id_get_doc = {
    'tags': ['Books'],
    'summary': '获取指定书籍详情',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '书籍的 MongoDB ID'
        }
    ],
    'responses': {
        200: {
            'description': '成功返回书籍详情',
            'schema': {
                'type': 'object',
                'properties': {
                    'book_id': {'type': 'string', 'example': '60f7b0b6e13a4b3e2f4a6789'},
                    'title': {'type': 'string', 'example': 'Book Title'},
                    'author': {'type': 'string', 'example': 'Author Name'},
                    'description': {'type': 'string', 'example': 'This is a book about...'}
                }
            }
        },
        400: {
            'description': '无效的书籍 ID',
            'schema': {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        },
        404: {
            'description': '未找到书籍',
            'schema': {'type': 'object', 'properties': {'error': {'type': 'string'}}}
        }
    }
}

books_post_doc = {
    'tags': ['Books'],
    'summary': '添加新书籍',
    'description': '添加一本新书，要求提供 title 和 author 字段。',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['title', 'author'],
                'properties': {
                    'title': {'type': 'string', 'example': 'Book Title'},
                    'author': {'type': 'string', 'example': 'Author Name'},
                    'description': {'type': 'string', 'example': 'This is a book about...'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': '创建成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'book_id': {'type': 'string', 'example': '60f7b0b6e13a4b3e2f4a6789'},
                    'title': {'type': 'string', 'example': 'Book Title'},
                    'author': {'type': 'string', 'example': 'Author Name'},
                    'description': {'type': 'string', 'example': 'This is a book about...'}
                }
            }
        },
        400: {
            'description': '缺少 title 或 author 字段',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'The new book must have a title and author'}
                }
            }
        },
        500: {
            'description': '数据库插入失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Failed to add book'}
                }
            }
        }
    }
}

books_delete_doc = {
    'tags': ['Books'],
    'summary': '根据书籍ID删除书籍',
    'parameters': [
        {
            'name': 'book_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': '书籍的 MongoDB ID'
        }
    ],
    'responses': {
        200: {
            'description': '书籍删除成功',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {'type': 'string', 'example': 'Book deleted'}
                }
            }
        },
        400: {
            'description': '无效的书籍 ID',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Invalid book ID'}
                }
            }
        },
        404: {
            'description': '未找到书籍',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Book not found'}
                }
            }
        },
        500: {
            'description': '删除书籍失败',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string', 'example': 'Failed to delete book'}
                }
            }
        }
    }
}
