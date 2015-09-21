var app = angular.module('stats', []);

app.controller('buildsController', ['buildsRetriever', function(buildsRetriever) {
    start_date = '2015-01-01';
    finish_date = '2016-01-01';
    buildsRetriever.refresh(this, 'pipeline_count', 'pipeline_deploy', start_date, finish_date);
    buildsRetriever.refresh(this, 'pass_deploy_count', 'pipeline_deploy', start_date, finish_date, 'success');
    buildsRetriever.refresh(this, 'pass_prepare_count', 'pipeline_prepare', start_date, finish_date, 'success');
    buildsRetriever.refresh(this, 'pass_test_cloud_image_count', 'test_cloud_image', start_date, finish_date, 'success');
 }]);

app.controller('bugsController', ['bugsRetriever', function(bugsRetriever) {
    bugsRetriever.refresh(this);
 }]);
