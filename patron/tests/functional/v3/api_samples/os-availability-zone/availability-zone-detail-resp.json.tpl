{
    "availabilityZoneInfo": [
        {
            "hosts": {
                "consoleauth": {
                    "patron-consoleauth": {
                        "active": true,
                        "available": true,
                        "updated_at": %(strtime_or_none)s
                    }
                },
                "cert": {
                    "patron-cert": {
                        "active": true,
                        "available": true,
                        "updated_at": %(strtime_or_none)s
                    }
                },
                "conductor": {
                    "patron-conductor": {
                        "active": true,
                        "available": true,
                        "updated_at": %(strtime_or_none)s
                    }
                },
                "cells": {
                    "patron-cells": {
                        "active": true,
                        "available": true,
                        "updated_at": %(strtime_or_none)s
                    }
                },
                "scheduler": {
                    "patron-scheduler": {
                        "active": true,
                        "available": true,
                        "updated_at": %(strtime_or_none)s
                    }
                },
                "network": {
                    "patron-network": {
                        "active": true,
                        "available": true,
                        "updated_at": %(strtime_or_none)s
                    }
                }
            },
            "zoneName": "internal",
            "zoneState": {
                "available": true
            }
        },
        {
            "hosts": {
                "compute": {
                    "patron-compute": {
                        "active": true,
                        "available": true,
                        "updated_at": %(strtime_or_none)s
                    }
                }
            },
            "zoneName": "patron",
            "zoneState": {
                "available": true
            }
        }
    ]
}
