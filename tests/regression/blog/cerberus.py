rules = {
    "Blog": {
        "title": {"type": "string"},
        "posts": {"type": "list"},
    },
    "Post": {
        "title": {"type": "string"},
        "body": {"type": "string"},
        "tags": {"type": "list"},
    },
    "Tag": {
        "name": {"type": "string", "required": True},
    },
}
