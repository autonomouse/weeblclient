app.factory('buildsRetriever', ['$http', function($http) {
  var refresh = function(scope, field_name, job_type_name, completed_at_start, completed_at_end, build_status_name) {
    var url = "/api/v1/build/";
    var parameters = [];
    if (job_type_name)
        parameters['job_type__name'] = job_type_name;
    if (completed_at_start)
        parameters['pipeline__completed_at__gte'] = completed_at_start;
    if (completed_at_end)
        parameters['pipeline__completed_at__lte'] = completed_at_end;
    if (build_status_name)
        parameters['build_status__name'] = build_status_name;

    return $http.get(url, {'params': parameters}).success(function(data) {
       scope[field_name] = data.meta.total_count;
    });
  };

  return {
    refresh: refresh
  };
}]);
