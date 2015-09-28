var app = angular.module('weebl');

app.controller('bugsController', [
    '$scope', '$rootScope', 'buildsRetriever', 'bugsRetriever', 'SearchService',
    function($scope, $rootScope, buildsRetriever, bugsRetriever, SearchService) {
        binding = this;
        $scope.filters = SearchService.getEmptyFilter();
        $scope.bugs = {};

        $scope.start_date = null;
        $scope.finish_date = null;

        $scope.tabs = {}
        $scope.tabs.builds = {};
        $scope.tabs.builds.pagetitle = "Builds";
        $scope.tabs.builds.currentpage = "builds";
        $scope.tabs.bugs = {};
        $scope.tabs.bugs.pagetitle = "Bugs";
        $scope.tabs.bugs.currentpage = "bugs";
        $scope.tabs.patterns = {};
        $scope.tabs.patterns.pagetitle = "Patterns";
        $scope.tabs.patterns.currentpage = "patterns";

        function updateStats() {
            start_date = $scope.start_date;
            finish_date = $scope.finish_date;
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

        function updateBugs() {
            bugsRetriever.refresh($scope,
                $scope.start_date,
                $scope.finish_date);
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
            updateStats();
            updateBugs();
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

        $scope.updateFilter('date', 'Last Year', 'builds');
        $scope.toggleTab('builds');

    }]);
