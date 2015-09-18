var app = angular.module('stats', []);

app.controller('buildsController', ['buildsRetriever', function(buildsRetriever) {
    buildsRetriever.refresh(this);
 }]);

app.controller('bugsController', ['bugsRetriever', function(bugsRetriever) {
    bugsRetriever.refresh(this);
 }]);

