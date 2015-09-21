app.factory('buildsRetriever', ['$http', function($http) {
  var refresh = function(scope, job_type_name, created_at_start, created_at_end) {
    var url = "/api/v1/build/";
    var parameters = [];
    if (job_type_name)
        parameters['job_type__name'] = job_type_name;
    if (created_at_start)
        parameters['created_at__gte'] = created_at_start;
    if (created_at_end)
        parameters['created_at__lte'] = created_at_end;

    return $http.get(url, {'params': parameters}).success(function(data) {
       scope.count = data.meta.total_count;
    });
  };

  return {
    refresh: refresh
  };
}]);
