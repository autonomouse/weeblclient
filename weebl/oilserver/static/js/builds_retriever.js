builds_app.factory('buildsRetriever', ['$http', function($http) {
  var refresh = function(scope, field_name, job_type_name, created_at_start, created_at_end, build_status_name) {
    var url = "/api/v1/build/";
    var parameters = [];
    if (job_type_name)
        parameters['job_type__name'] = job_type_name;
    if (created_at_start)
        parameters['created_at__gte'] = created_at_start;
    if (created_at_end)
        parameters['created_at__lte'] = created_at_end;
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
