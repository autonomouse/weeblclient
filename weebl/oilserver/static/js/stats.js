var app = angular.module('weebl', []);

app.config(['$interpolateProvider', function ($interpolateProvider) {
$interpolateProvider.startSymbol('{$');
$interpolateProvider.endSymbol('$}');
}]);

app.controller('buildsController', [
    '$scope', '$rootScope', 'buildsRetriever', 'bugsRetriever', 'SearchService', 'metadataRetriever',
    function($scope, $rootScope, buildsRetriever, bugsRetriever, SearchService, metadataRetriever) {
        binding = this;
        $scope.filters = SearchService.getEmptyFilter();
        $scope.bugs = {};

        $scope.metadata = {};

        $scope.tabs = {};
        $scope.tabs.builds = {};
        $scope.tabs.builds.pagetitle = "Builds";
        $scope.tabs.builds.currentpage = "builds";
        $scope.tabs.bugs = {};
        $scope.tabs.bugs.pagetitle = "Bugs";
        $scope.tabs.bugs.currentpage = "bugs";

        function generatePipelineFilters() {
            var pipeline_filters = {};

            if ($scope.start_date)
                pipeline_filters['completed_at__gte'] = $scope.start_date;
            if ($scope.finish_date)
                pipeline_filters['completed_at__lte'] = $scope.finish_date;

            for (var enum_field in $scope.filters) {
                if (!(enum_field in $scope.metadata))
                    continue;

                enum_values = [];
                $scope.filters[enum_field].forEach(function(enum_value) {
                    enum_values.push(enum_value.substr(1));
                });
                api_enum_name = metadataRetriever.enum_fields[enum_field];
                pipeline_filters[api_enum_name + '__name__in'] = enum_values;
            }

            return pipeline_filters;
        }

        function updateStats(pipeline_filters) {
            buildsRetriever.refresh(binding, 'pipeline_count',
                                    'pipeline_deploy', pipeline_filters);
            buildsRetriever.refresh(binding, 'pass_deploy_count',
                                    'pipeline_deploy', pipeline_filters,
                                    'success');
            buildsRetriever.refresh(binding, 'pass_prepare_count',
                                    'pipeline_prepare', pipeline_filters,
                                    'success');
            buildsRetriever.refresh(binding, 'pass_test_cloud_image_count',
                                    'test_cloud_image', pipeline_filters,
                                    'success');
        };

        function updateBugs(pipeline_filters) {
            bugsRetriever.refresh($scope, pipeline_filters);
        }

        function dateToString(date) {
            return date.getUTCFullYear() + "-" + (date.getUTCMonth() + 1) + "-" + date.getUTCDate();
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
            $scope.start_date = dateToString(prior_date);
            $scope.finish_date = dateToString(today);
        };

        function updateFromServer() {
            pipeline_filters = generatePipelineFilters();
            updateStats(pipeline_filters);
            updateBugs(pipeline_filters);
        }

        // Clear the search bar.
        $scope.clearSearch = function() {
            $scope.search = "";
            $scope.start_date = null;
            $scope.finish_date = null;
            $scope.updateSearch();
        };

        // Update the filters object when the search bar is updated.
        $scope.updateSearch = function() {
            var filters = SearchService.getCurrentFilters(
                $scope.search);
            if(filters === null) {
                $scope.filters = SearchService.getEmptyFilter();
                $scope.searchValid = false;
            } else {
                $scope.filters = filters;
                $scope.searchValid = true;
            }
            updateFromServer();
        };

        $scope.updateFilter = function(type, value, tab) {
            console.log("Updating filter! %s %s %s", type, value, tab);

            if (type == "date") {
                // Only one date can be set at a time.
                new_value = "=" + value;
                if ($scope.filters["date"] && $scope.filters["date"][0] == new_value) {
                    $scope.filters["date"] = [];
                    $scope.start_date = null;
                    $scope.finish_date = null;
                } else {
                    updateDates(value);
                    $scope.filters["date"] = [new_value];
                }
            } else {
                $scope.filters = SearchService.toggleFilter(
                    $scope.filters, type, value, true);
            }
            $scope.search = SearchService.filtersToString($scope.filters);
            updateFromServer();
        };

        $scope.isFilterActive = function(type, value, tab) {
            return SearchService.isFilterActive(
                $scope.filters, type, value, true);
        };

        // Toggles between the current tab.
        $scope.toggleTab = function(tab) {
            $rootScope.title = $scope.tabs[tab].pagetitle;
            $scope.currentpage = tab;
        };

        metadataRetriever.refresh($scope);
        $scope.updateFilter('date', 'Last 24 Hours', 'builds');
        $scope.toggleTab('builds');

    }]);
