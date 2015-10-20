app.factory('metadataRetriever', ['$http', function($http) {
    var enum_fields = {
        'openstack_release': 'openstackversion',
        'ubuntu_release': 'ubuntuversion',
        'networking': 'sdn',
        'compute': 'compute',
        'blockstorage': 'blockstorage',
        'imagestorage': 'imagestorage',
        'database': 'database'
    }

    var refresh = function(scope) {
        for (var key in enum_fields) {
            var url = "/api/v1/" + enum_fields[key] + "/";
            (function(actual_key) {
                $http.get(url).success(function(data) {
                    scope.metadata[actual_key] = data.objects;
                });
            }(key));
        }
    };

    return {
        refresh: refresh,
        enum_fields: enum_fields,
    };
}]);
