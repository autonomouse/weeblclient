var builds_app = angular.module('weebl', []);

builds_app.config(['$interpolateProvider', function ($interpolateProvider) {
$interpolateProvider.startSymbol('{$');
$interpolateProvider.endSymbol('$}');
}]);

builds_app.controller('buildsController', [
    '$scope', 'buildsRetriever',
    function($scope, buildsRetriever) {
        start_date = '2015-01-01';
        finish_date = '2016-01-01';
        buildsRetriever.refresh(this, 'pipeline_count', 'pipeline_deploy', start_date, finish_date);
        buildsRetriever.refresh(this, 'pass_deploy_count', 'pipeline_deploy', start_date, finish_date, 'success');
        buildsRetriever.refresh(this, 'pass_prepare_count', 'pipeline_prepare', start_date, finish_date, 'success');
        buildsRetriever.refresh(this, 'pass_test_cloud_image_count', 'test_cloud_image', start_date, finish_date, 'success');

        $scope.updateFilter = function(type, value, tab) {
            console.log("Updating filter!")
        }
    }]);
