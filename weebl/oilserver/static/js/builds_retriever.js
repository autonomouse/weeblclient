app.factory('buildsRetriever', ['$http', function($http) {
  var refresh = function(scope, field_name, job_type_name, pipeline_filters, build_status_name) {
    var url = "/api/v1/build/";
    var parameters = {
        'meta_only': true,
        'limit': 1};
    if (job_type_name)
        parameters['job_type__name'] = job_type_name;
    if (build_status_name)
        parameters['build_status__name'] = build_status_name;

    for (var filter in pipeline_filters) {
        parameters["pipeline__" + filter] = pipeline_filters[filter];
    }

    return $http.get(url, {'params': parameters}).success(function(data) {
       scope[field_name] = data.meta.total_count;
    });
  };

  return {
    refresh: refresh
  };
}]);
