rules = {
    "Blog": {
        "title": {"type": "String"},
        "posts": {"type": "List"},
    },
    "Post": {
        "title": {"type": "String"},
        "body": {"type": "Text"},
        "tags": {"type": "List"},
    },
    "Tag": {
        "name": {"type": "String"},
    },
}
