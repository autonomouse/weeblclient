app.factory('bugsRetriever', ['$http', function($http) {
  var refresh = function(scope) {
    var url = "/api/v1/bug/";
    return $http.get(url).success(function(data) {
       scope.count = data.meta.total_count;
    });
  };

  return {
    refresh: refresh
  };
}]);
