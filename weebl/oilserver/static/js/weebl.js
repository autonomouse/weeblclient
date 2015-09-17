angular.module('weebl', ['oil_builds'])
.controller('weeblController', ['buildsRetriever', function(buildsRetriever) {
   buildsRetriever.refresh(this);
}]);

angular.module('oil_builds', [])
.factory('buildsRetriever', ['$http', function($http) {
  var build_count = -1;
  var refresh = function(scope) {
    var url = "/api/v1/build/";
    return $http.get(url).success(function(data) {
       scope.count = data.meta.total_count;
    });
  };

  return {
    total_count: build_count,
    refresh: refresh
  };
}]);
