angular.module('oil_builds', [])
.factory('buildsRetriever', ['$http', function($http) {
  var refresh = function(scope) {
    var url = "/api/v1/build/";
    return $http.get(url).success(function(data) {
       scope.count = data.meta.total_count;
    });
  };

  return {
    refresh: refresh
  };
}]);
