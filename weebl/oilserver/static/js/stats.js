stats = angular.module('stats', ['oil_builds'])

stats.controller('statsController', ['buildsRetriever', function(buildsRetriever) {
   buildsRetriever.refresh(this);
}]);
