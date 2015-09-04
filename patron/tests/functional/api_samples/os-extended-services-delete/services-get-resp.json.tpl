{
    "services": [
        {
            "id": 1,
            "binary": "patron-scheduler",
            "host": "host1",
            "state": "up",
            "status": "disabled",
            "updated_at": "%(strtime)s",
            "zone": "internal"
        },
        {
            "id": 2,
            "binary": "patron-compute",
            "host": "host1",
            "state": "up",
            "status": "disabled",
            "updated_at": "%(strtime)s",
            "zone": "patron"
        },
        {
            "id": 3,
            "binary": "patron-scheduler",
            "host": "host2",
            "state": "down",
            "status": "enabled",
            "updated_at": "%(strtime)s",
            "zone": "internal"
        },
        {
            "id": 4,
            "binary": "patron-compute",
            "host": "host2",
            "state": "down",
            "status": "disabled",
            "updated_at": "%(strtime)s",
            "zone": "patron"
        }
    ]
}
