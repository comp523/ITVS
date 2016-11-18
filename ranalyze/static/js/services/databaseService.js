(function(app){
"use strict";

    var databaseService = function($http, $httpParamSerializer, $q) {

        var self = this;

        self.entry = new (function(){

            /**
             *
             * @param parameters {object}
             * @returns {promise}
             */
            this.search = function(parameters) {

                var localParameters = {};
                angular.extend(localParameters, parameters);

                angular.forEach(["before", "after"], function(dateKey) {
                    if (localParameters[dateKey]) {
                        localParameters[dateKey] = (new Date(localParameters[dateKey]))
                            .toISOString().slice(0, 10);
                    }
                });

                var query = $httpParamSerializer(localParameters);
                return $http.get('/entry/search?' + query)
                    .then(function(response) {
                        return response.data;
                    });

            };

            this.getSubreddits = function(){

                return $http.get('/entry/subreddits')
                    .then(function(response) {
                        return response.data;
                    });

            };

        });

        self.frequency = new (function(){

            /** @enum {String} */
            this.granularity = {
                YEAR: "year",
                MONTH: "month",
                DAY: "day"
            };

            /**
             *
             * @param parameters {object}
             * @returns {promise}
             */
            this.overview = function(parameters) {

                var query = $httpParamSerializer(parameters);
                return $http.get('/frequency/overview?' + query)
                    .then(function(response) {
                        return response.data;
                    });

            };

        });

        self.config = new (function(){

            var Subreddit = function(parameters) {
                angular.extend(this, parameters);
            };

            this.getCloudParams = function(){

                // Temporary data
                // TODO: implement fetch from database
                return $q(function(resolve){
                    resolve({
                        "entryWeight": 4,
                        "totalWeight": 1
                    });
                });

            };

            this.getSubreddits = function() {

                return $http.get('/config/subreddits')
                    .then(function(response){
                        return response.data.map(function(item){
                            return new Subreddit(item);
                        });
                    })

            };

        });

    };

    app.service('database', databaseService);

})(app);