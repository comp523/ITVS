(function(app){
"use strict";

    var configFactory = function(database) {

        var config = {
            Item: database.ConfigItem
            },

            types = {
                ARRAY: 0,
                BOOLEAN: 1,
                NUMBER: 2
            },

            fields = {
                subreddits: {
                    type: types.ARRAY,
                    name: "subreddit"
                },
                entryWeight: {
                    type: types.NUMBER,
                    name: "entryWeight"
                },
                totalWeight: {
                    type: types.NUMBER,
                    name: "totalWeight"
                },
                blacklist: {
                    type: types.ARRAY,
                    name: "blacklist"
                },
                serverBlacklist: {
                    type: types.ARRAY,
                    name: "serverBlacklist"
                }
            },

            nameToGetter = function(name) {
                return 'get' +
                    name.substring(0, 1).toUpperCase() +
                    name.substring(1);
            };

        angular.forEach(fields, function(properties, field){
            config[nameToGetter(field)] = function(){
                return database.ConfigItem.query({
                    name: properties.name
                }).$promise.then(function(results) {
                    switch (properties.type) {
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