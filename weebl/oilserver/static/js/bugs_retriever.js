app.factory('bugsRetriever', ['$http', function($http) {
  var refresh = function(scope, completed_at_start, completed_at_end) {
    var url = "/api/v1/bug/";
    parameters = {};
    if (completed_at_start)
        parameters['knownbugregex__bug_occurrences__build__pipeline__completed_at__gte'] = completed_at_start;
    if (completed_at_end)
        parameters['knownbugregex__bug_occurrences__build__pipeline__completed_at__lte'] = completed_at_end;
    return $http.get(url, {'params': parameters}).success(function(data) {
        scope.bugs.count = data.meta.total_count;
        scope.bugs.objects = data.objects;
    });
  };

  return {
    refresh: refresh
  };
}]);
