app.factory('buildsRetriever', ['$http', '$q', function($http, $q) {

  var refresh = function(scope, pipeline_filters) {
    var url = "/api/v1/build/?username=" + scope.user + "&api_key=" + scope.apikey;

    function create_params(jobtype_name, buildstatus_name) {
        var parameters = {
            'meta_only': true,
            'limit': 1}

        if (jobtype_name)
            parameters['jobtype__name'] = jobtype_name;

        for (var filter in pipeline_filters) {
            parameters["pipeline__" + filter] = pipeline_filters[filter];
        }

        if (buildstatus_name)
            parameters['buildstatus__name'] = buildstatus_name;

        return parameters;
    }
    function calcPercentage(value, total) {
        var percentage = d3.format(',.2f')(((value / total) * 100))
        if (percentage == "NaN"){
            return "0%";
        } else {
            return percentage + "%";
        }

    }

    function updateChartData(total, pass_deploy_count, pass_prepare_count, pass_test_cloud_image_count) {
        var stack_bar_config = {
            visible: true,
            extended: false,
            disabled: false,
            autorefresh: true,
            refreshDataOnly: false,
            debounce: 10
        };
        scope.stack_bar_config = stack_bar_config;

        var stack_bar_options = {
            chart: {
                type: 'discreteBarChart',
                height: 450,
                x: function(d){return d.label;},
                y: function(d){return d.value;},
                showValues: true,
                valueFormat: function(d){
                    return calcPercentage(d, total)
                },
                transitionDuration: 500,
                xAxis: {
                    axisLabel: 'Job Name'
                },
                yAxis: {
                    axisLabel: 'Test Run Count',
                    tickFormat: function(d) {
                        return d3.format(',d')(d);
                    }
                },
                yDomain: [0, total]
            },
            title: {
                enable: true,
                text: "Showing successes per job of " + total + " matching test runs.",
                css: {
                    width: "nullpx",
                    textAlign: "center"
                }
            }
        };
        scope.stack_bar_options = stack_bar_options;

        var stack_bar_data = [
            {
                key: "Test Run Success",
                values: [
                    {
                        "label" : "Deploy Openstack" ,
                        "value" : pass_deploy_count,
                        "color" : "#77216F"
                    } ,
                    {
                        "label" : "Configure Openstack for test" ,
                        "value" : pass_prepare_count,
                        "color" : "#6E3C61"
                    } ,
                    {
                        "label" : "SSH to guest instance",
                        "value" : pass_test_cloud_image_count,
                        "color" : "#411934"
                    }
                ]
            }
        ]
        scope.stack_bar_data = stack_bar_data;

    }

    var all_parameters = create_params('pipeline_deploy', null);
    var deploy_parameters = create_params('pipeline_deploy', 'success');
    var prepare_parameters = create_params('pipeline_prepare', 'success');
    var guestos_parameters = create_params('test_cloud_image', 'success');

    var total_builds = $http.get(url, {'params': all_parameters}).success(function(data) {
        scope['pipeline_count'] = data.meta.total_count;});
    var deploy = $http.get(url, {'params': deploy_parameters}).success(function(data) {
        scope['pass_deploy_count'] = data.meta.total_count;});
    var prepare = $http.get(url, {'params': prepare_parameters}).success(function(data) {
        scope['pass_prepare_count'] = data.meta.total_count;});
    var guestos = $http.get(url, {'params': guestos_parameters}).success(function(data) {
        scope['pass_test_cloud_image_count'] = data.meta.total_count;});

    $q.all([total_builds, deploy, prepare, guestos]).then(function(arrayOfResults) {
        updateChartData(
            scope['pipeline_count'],
            scope['pass_deploy_count'],
            scope['pass_prepare_count'],
            scope['pass_test_cloud_image_count']
        )
      })
  };

  return {
    refresh: refresh
  };
}]);
