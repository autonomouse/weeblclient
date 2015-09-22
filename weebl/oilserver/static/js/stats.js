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
            console.log("Filtering dates from %s to %s", start_date, finish_date);
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

        function dateToString(date) {
            return date.getFullYear() + "-" + date.getMonth() + "-" + date.getDate();
        }

        function updateDates(value) {
            var days_offset = 0;
            switch(value) {
                case "Last 24 Hours":
                    days_offset = 1;
                    break;
                case "Last 7 Days":
                    days_offset = 7;
                    break;
                case "Last 30 Days":
                    days_offset = 30;
                    break;
                case "Last Year":
                    days_offset = 365;
                    break;
                default:
                    console.log("Bad date value: " + value);
            }
            console.log("Updating to last %d days.", days_offset);
            today = new Date();
            prior_date = new Date(new Date().setDate(today.getDate()-days_offset));
            start_date = dateToString(prior_date);
            finish_date = dateToString(today);
            updateStats(start_date, finish_date);
        }

        updateDates('Last Year');

        $scope.updateFilter = function(type, value, tab) {
            console.log("Updating filter! %s %s %s", type, value, tab);

            if (type == "date") {
                updateDates(value);
            }
        }
    }]);
