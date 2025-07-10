users_list_doc = {
    'tags': ['Users'],
    'summary': 'List all users',
    'responses': {
        200: {
            'description': 'A list of users',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'role': {'type': 'string'},
                        'created_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        }
    },
    'security': [{'BearerAuth': []}]
}

users_current_doc = {
    "tags": ["Users"],
    "summary": "Get current authenticated user",
    "description": "Returns information about the currently authenticated user.",
    "responses": {
        200: {
            "description": "Current user information",
            "examples": {
                "application/json": {
                    "username": "johndoe",
                    "role": "admin",
                    "created_at": "2024-07-01T12:34:56.000Z"
                }
            }
        },
        403: {
            "description": "User not found or unauthorized",
            "examples": {
                "application/json": {
                    "error": "User not found"
                }
            }
        },
        500: {
            "description": "Server error",
            "examples": {
                "application/json": {
                    "error": "Failed to retrieve current user",
                    "details": "Some internal error message"
                }
            }
        }
    },
    "security": [{"BearerAuth": []}]
}