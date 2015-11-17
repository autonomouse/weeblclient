app.factory('UserService', function ($resource) {
    //return $resource('/api/v1/knownbugregex/?username=DarrenHoyland\&api_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx:regex_uuid', {regex_uuid: "@regex_uuid"});
    return $resource('/api/v1/jobtype/:name?username=DarrenHoyland\&api_key=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', {name: "@name"});
});
