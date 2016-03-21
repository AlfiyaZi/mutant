rules = {
    "Blog": {
        "title": {
            "type": "string",
        },
        "posts": {
            "type": "list",
            "schema": {
                "title": {
                    "type": "string",
                },
                "body": {
                    "type": "string",
                },
                "tags": {
                    "type": "list",
                    "schema": {
                        "name": {
                            "type": "string",
                            "required": True,
                        },
                    },
                },
            },
        },
    },
    "Post": {
        "title": {
            "type": "string",
        },
        "body": {
            "type": "string",
        },
        "tags": {
            "type": "list",
            "schema": {
                "name": {
                    "type": "string",
                    "required": True,
                },
            },
        },
    },
    "Tag": {
        "name": {
            "type": "string",
            "required": True,
        },
    },
}
