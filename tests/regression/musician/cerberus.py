rules = {
    "Musician": {
        "first_name": {
            "type": "string",
        },
        "last_name": {
            "type": "string",
        },
        "instruments": {
            "type": "list",
            "schema": {
                "type": "dict",
                "schema": {
                    "name": {
                        "type": "string",
                    },
                },
            },
        },
    },
    "Album": {
        "artist": {
            "type": "dict",
            "schema": {
                "first_name": {
                    "type": "string",
                },
                "last_name": {
                    "type": "string",
                },
                "instruments": {
                    "type": "list",
                    "schema": {
                        "type": "dict",
                        "schema": {
                            "name": {
                                "type": "string",
                            },
                        },
                    },
                },
            },
        },
        "name": {
            "type": "string",
        },
        "release_date": {
            "type": "datetime",
        },
        "num_stars": {
            "type": "integer",
        },
    },
    "Instrument": {
        "name": {
            "type": "string",
        },
    },
}
