var app = angular.module('stats', []);

app.controller('buildsController', ['buildsRetriever', function(buildsRetriever) {
    buildsRetriever.refresh(this, 'pipeline_deploy', '2015-01-01', '2016-01-01');
 }]);

app.controller('bugsController', ['bugsRetriever', function(bugsRetriever) {
    bugsRetriever.refresh(this);
 }]);

