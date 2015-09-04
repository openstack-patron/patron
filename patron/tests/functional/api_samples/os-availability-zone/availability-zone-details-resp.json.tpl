{
    "availabilityZoneInfo": [
        {
            "zoneName": "zone-1",
            "zoneState": {
                "available": true
            },
            "hosts": {
                "fake_host-1": {
                    "patron-compute": {
                        "active": true,
                        "available": true,
                        "updated_at": "2012-12-26T14:45:25.000000"
                    }
                }
            }
        },
        {
            "zoneName": "internal",
            "zoneState": {
                "available": true
            },
            "hosts": {
                "fake_host-1": {
                    "patron-sched": {
                        "active": true,
                        "available": true,
                        "updated_at": "2012-12-26T14:45:25.000000"
                    }
                },
                "fake_host-2": {
                    "patron-network": {
                        "active": true,
                        "available": false,
                        "updated_at": "2012-12-26T14:45:24.000000"
                    }
                }
            }
        },
        {
            "zoneName": "zone-2",
            "zoneState": {
                "available": false
            },
            "hosts": null
        }
    ]
}