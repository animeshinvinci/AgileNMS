function MonitorListCtrl($scope) {
    $scope.monitors = [
        {
            "name": "HTTP Poller: http://www.google.co.uk",
            "uuid": "00000000000000000000000000000000",
            "url": "/monitors/00000000000000000000000000000000/",
            "state": "ok",
            "check_states": {
                "ok": 7,
                "warning": 0,
                "critical": 0,
                "disabled": 0,
                "unknown": 0
            },
            "data": "HTTP 200 OK (20ms)",
            "class": "success",
        },
        {
            "name": "HTTP Poller: http://www.badwebsite.co.uk",
            "uuid": "00000000000000000000000000000001",
            "url": "/monitors/00000000000000000000000000000001/",
            "state": "critical",
            "check_states": {
                "ok": 10,
                "warning": 0,
                "critical": 1,
                "disabled": 0,
                "unknown": 0
            },
            "data": "No response from server",
            "class": "danger",
        },
        {
            "name": "HTTP Poller: http://www.okwebsite.co.uk",
            "uuid": "00000000000000000000000000000002",
            "url": "/monitors/00000000000000000000000000000002/",
            "state": "warning",
            "check_states": {
                "ok": 3,
                "warning": 6,
                "critical": 0,
                "disabled": 0,
                "unknown": 0
            },
            "data": "HTTP 200 OK (523ms)",
            "class": "warning",
        },
        {
            "name": "HTTP Poller: http://www.unknownwebsite.co.uk",
            "uuid": "00000000000000000000000000000004",
            "url": "/monitors/00000000000000000000000000000004/",
            "state": "unknown",
            "check_states": {
                "ok": 0,
                "warning": 0,
                "critical": 0,
                "disabled": 0,
                "unknown": 1
            },
            "data": "Not checked",
            "class": "primary",
        },
        {
            "name": "HTTP Poller: http://www.disabledwebsite.co.uk",
            "uuid": "00000000000000000000000000000003",
            "url": "/monitors/00000000000000000000000000000003/",
            "state": "disabled",
            "check_states": {
                "ok": 0,
                "warning": 0,
                "critical": 0,
                "disabled": 1,
                "unknown": 0
            },
            "data": "",
            "class": "muted",
        },
    ];
}
