app.factory('bugsRetriever', ['$http', function($http) {
  var refresh = function(scope, pipeline_filters) {
    var url = "/api/v1/bug/";
    parameters = {};
    for (var filter in pipeline_filters) {
        key = "knownbugregex__bug_occurrences__build__pipeline__" + filter;
        parameters[key] = pipeline_filters[filter];
    }
    return $http.get(url, {'params': parameters}).success(function(data) {
        scope.bugs.count = data.meta.total_count;
        scope.bugs.objects = data.objects;
    });
  };

  return {
    refresh: refresh
  };
}]);
