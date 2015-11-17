app.factory('bugsRetriever', ['$http', function($http) {

  var refresh = function(scope, pipeline_filters) {
    var url = "/api/v1/bug/?username=" + scope.user + "&api_key=" + scope.apikey;
    parameters = {};
    for (var filter in pipeline_filters) {
        key = "knownbugregex__bugoccurrences__build__pipeline__" + filter;
        parameters[key] = pipeline_filters[filter];
    }
    // uuid_gte check ensures only bugs with bug occurrences are returned.
    parameters['knownbugregex__bugoccurrences__uuid__gte'] = 0;
    return $http.get(url, {'params': parameters}).success(function(data) {
        scope.bugs.count = data.meta.total_count;
        scope.bugs.objects = data.objects;
    });
  };

  return {
    refresh: refresh
  };
}]);
