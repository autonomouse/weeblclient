app.factory('metadataRetriever', ['$http', function($http) {
    var enum_fields = {
        'openstack_releases': 'openstack_version',
        'ubuntu_releases': 'ubuntu_version',
        'networking': 'sdn',
        'compute': 'compute',
        'block_storage': 'block_storage',
        'image_storage': 'image_storage',
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
        refresh: refresh
    };
}]);
