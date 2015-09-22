var builds_app = angular.module('weebl', []);

builds_app.config(['$interpolateProvider', function ($interpolateProvider) {
$interpolateProvider.startSymbol('{$');
$interpolateProvider.endSymbol('$}');
}]);

builds_app.controller('buildsController', [
    '$scope', 'buildsRetriever',
    function($scope, buildsRetriever) {
        binding = this;

        function updateStats(start_date, finish_date) {
            buildsRetriever.refresh(binding, 'pipeline_count',
                                    'pipeline_deploy', start_date,
                                    finish_date);
            buildsRetriever.refresh(binding, 'pass_deploy_count',
                                    'pipeline_deploy', start_date,
                                    finish_date, 'success');
            buildsRetriever.refresh(binding, 'pass_prepare_count',
                                    'pipeline_prepare', start_date,
                                    finish_date, 'success');
            buildsRetriever.refresh(binding, 'pass_test_cloud_image_count',
                                    'test_cloud_image', start_date,
                                    finish_date, 'success');
        };

        updateStats('2015-01-01', '2016-01-01');

        function updateDates(value) {
            switch(value) {
                case "Last 24 Hours":
                    console.log("Updating to last 24 hours.");
                    break;
                case "Last 7 Days":
                    console.log("Updating to last 7 days.");
                    break;
                case "Last 30 Days":
                    console.log("Updating to last 30 days.");
                    break;
                default:
                    console.log("Bad date value: " + value);
            }
        }

        $scope.updateFilter = function(type, value, tab) {
            console.log("Updating filter! %s %s %s", type, value, tab);

            if (type == "date") {
                updateDates(value);
            }
        }
    }]);
