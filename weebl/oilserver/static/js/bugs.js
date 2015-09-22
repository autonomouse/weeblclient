var bugs_app = angular.module('bugs', []);

bugs_app.controller('bugsController', ['bugsRetriever', function(bugsRetriever) {
    bugsRetriever.refresh(this);
 }]);
