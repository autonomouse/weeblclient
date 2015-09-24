var builds_app = angular.module('weebl', []);

builds_app.config(['$interpolateProvider', function ($interpolateProvider) {
$interpolateProvider.startSymbol('{$');
$interpolateProvider.endSymbol('$}');
}]);

builds_app.controller('buildsController', [
    '$scope', '$rootScope', 'buildsRetriever', 'SearchService',
    function($scope, $rootScope, buildsRetriever, SearchService) {
        binding = this;
        $scope.filters = SearchService.getEmptyFilter();
        $scope.currentpage = "stats";

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

        var dateSymbolToDays = {
            'Last 24 Hours': 1,
            'Last 7 Days': 7,
            'Last 30 Days': 30,
            'Last Year': 365
        };

        function updateDates(value) {
            var days_offset = dateSymbolToDays[value];
            console.log("Updating to last %d days.", days_offset);
            today = new Date();
            prior_date = new Date(new Date().setDate(today.getDate()-days_offset));
            start_date = dateToString(prior_date);
            finish_date = dateToString(today);
            updateStats(start_date, finish_date);
        };

        $scope.updateFilter = function(type, value, tab) {
            console.log("Updating filter! %s %s %s", type, value, tab);

            if (type == "date") {
                updateDates(value);
                // Only one date can be set at a time.
                $scope.filters["date"] = ["=" + value];
            } else {
                $scope.filters = SearchService.toggleFilter(
                    $scope.filters, type, value, true);
            }
        };

        $scope.isFilterActive = function(type, value, tab) {
            return SearchService.isFilterActive(
                $scope.filters, type, value, true);
        };

        $scope.tabs = {}
        $scope.tabs.stats = {};
        $scope.tabs.stats.pagetitle = "Stats";
        $scope.tabs.stats.currentpage = "Stats";
        $scope.tabs.bugs = {};
        $scope.tabs.bugs.pagetitle = "Bugs";
        $scope.tabs.bugs.currentpage = "Bugs";

        // Toggles between the current tab.
        $scope.toggleTab = function(tab) {
            $rootScope.title = $scope.tabs[tab].pagetitle;
            $scope.currentpage = tab;
        };

        $scope.updateFilter('date', 'Last Year', 'builds');

    }]);
