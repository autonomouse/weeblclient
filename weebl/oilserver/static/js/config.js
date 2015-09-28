
var app = angular.module('weebl');

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/builds', {
            controller: 'buildsController',
            templateUrl: 'static/partials/builds.html'
        })
        .when('/bugs', {
            controller: 'bugsController',
            templateUrl: 'static/partials/bugs.html'
        })
        .when('/patterns', {
            controller: 'patternsController',
            templateUrl: 'static/partials/patterns.html'
        })
        .otherwise({redirectTo: '/builds'});
  }]);

app.config(['$interpolateProvider', function ($interpolateProvider) {
$interpolateProvider.startSymbol('{$');
$interpolateProvider.endSymbol('$}');
}]);
