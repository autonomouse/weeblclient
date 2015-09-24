app.factory('bugsRetriever', ['$http', function($http) {
  var refresh = function(scope) {
    var url = "/api/v1/bug/";
    return $http.get(url).success(function(data) {
        scope.bugs.count = data.meta.total_count;
        scope.bugs.objects = data.objects;
    });
  };

  return {
    refresh: refresh
  };
}]);
