function CheckListCtrl($scope) {
    $scope.checks = [
        {
            "name": "HTTP Poller: http://www.google.co.uk",
            "uuid": "00000000000000000000000000000000",
            "url": "/checks/00000000000000000000000000000000/",
            "state": "up",
            "data": "HTTP 200 OK (20ms)",
            "class": "success",
        },
        {
            "name": "HTTP Poller: http://www.badwebsite.co.uk",
            "uuid": "00000000000000000000000000000001",
            "url": "/checks/00000000000000000000000000000001/",
            "state": "down",
            "data": "No response from server",
            "class": "danger",
        },
        {
            "name": "HTTP Poller: http://www.okwebsite.co.uk",
            "uuid": "00000000000000000000000000000002",
            "url": "/checks/00000000000000000000000000000002/",
            "state": "warning",
            "data": "HTTP 200 OK (523ms)",
            "class": "warning",
        },
        {
            "name": "HTTP Poller: http://www.disabledwebsite.co.uk",
            "uuid": "00000000000000000000000000000003",
            "url": "/checks/00000000000000000000000000000003/",
            "state": "disabled",
            "data": "",
            "class": "muted",
        },
        {
            "name": "HTTP Poller: http://www.unknownwebsite.co.uk",
            "uuid": "00000000000000000000000000000004",
            "url": "/checks/00000000000000000000000000000004/",
            "state": "unknown",
            "data": "Not checked",
            "class": "muted",
        },
    ];
}
