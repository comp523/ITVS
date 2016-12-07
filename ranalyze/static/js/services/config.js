(function(app){
"use strict";

    /**
     * The config service provides getters for retrieving configuration
     * parameters from the server. Getters return a promise which will be
     * resolved once the request to the server is completed.
     */
    var configFactory = function($resource) {

        var config = {
            Item: $resource('/config/:id', {
                id: '@id'
            })
        },

        types = {
            ARRAY: 0,
            BOOLEAN: 1,
            NUMBER: 2
        },

        fields = {
            entryWeight: types.NUMBER,
            totalWeight: types.NUMBER,
            blacklist: types.ARRAY,
            serverBlacklist: types.ARRAY
        },

        nameToGetter = function(name) {
            return 'get' +
                name.substring(0, 1).toUpperCase() +
                name.substring(1);
        };

        angular.forEach(fields, function(type, field){
            config[nameToGetter(field)] = function(){
                return config.Item.query({
                    name: field
                }).$promise.then(function(results) {
                    switch (type) {
                        case types.ARRAY:
                            return results;
                        case types.BOOLEAN:
                            results[0].value = (results[0].value === "1" ||
                                                results[0].value.toLowerCase() === "true");
                            break;
                        case types.NUMBER:
                            results[0].value = parseFloat(results[0].value);
                    }
                    return results[0];
                });
            };
        });

        return config;

    };

    app.factory("config", configFactory);

})(app);