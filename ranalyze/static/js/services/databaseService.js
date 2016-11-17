(function(app){
"use strict";

    var databaseService = function($http, $httpParamSerializer, $q) {

        var self = this;

        /** @enum {String} */
        self.granularity = {
            YEAR: "year",
            MONTH: "month",
            DAY: "day"
        };

        /**
         *
         * @param parameters {object}
         * @returns {promise}
         */
        self.search = function(parameters) {

            var localParameters = {};
            angular.extend(localParameters, parameters);

            angular.forEach(["before", "after"], function(dateKey) {
                if (localParameters[dateKey]) {
                    localParameters[dateKey] = (new Date(localParameters[dateKey]))
                        .toISOString().slice(0, 10);
                }
            });

            var query = $httpParamSerializer(localParameters);
            return $http.get('/search?' + query)
                .then(function(response) {
                    return response.data;
                });

        };

        /**
         *
         * @param parameters {object}
         * @returns {promise}
         */
        self.frequency = function(parameters) {

            var query = $httpParamSerializer(parameters);
            return $http.get('/frequency?' + query)
                .then(function(response) {
                    return response.data;
                });

        };

        self.getSubreddits = function(){

            return $http.get('/subreddits')
                .then(function(response) {
                    return response.data;
                });

        };

        self.getCloudParamDefaults = function(){

            return $q(function(resolve){
                resolve({
                    "entryWeight": 4,
                    "totalWeight": 1
                });
            });

        };

    };

    app.service('database', databaseService);

})(app);