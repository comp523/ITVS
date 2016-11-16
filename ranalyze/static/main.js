(function(angular){
    "use strict";

    var searchController = function($scope, database) {

        var self = this;

        $scope.form = {
            subreddit: []
        };

        $scope.table = {
            limit: 10,
            page: 1,
            order: 'time_submitted'
        };

        self.highlight = [];

        self.entries = [];

        database.getSubreddits()
            .then(function(subreddits){
                self.subreddits = subreddits;
            });

        self.filterSubs = function(sub) {

            var results = self.subreddits.filter(function(item){
                return item.toLowerCase().indexOf(sub.toLowerCase()) === 0;
            });

            return results || [];

        };

        self.search = function(){
            database.search($scope.form)
                .then(function(data){
                    self.entries = data.map(function(item){
                        item.type = item.permalink ? "Post" : "Comment";
                        return item;
                    });
                });
            if ($scope.form.advanced) {
                var regex = /(["'])(.*?)\1/g;
                $scope.highlight = [];
                var match;
                while ( (match = regex.exec($scope.form.query) ) !== null ) {
                    self.highlight.push(match[2]);
                }
            }
            else {
                self.highlight = $scope.form.query.split(" ");
            }
        };

        $scope.$on('search.simple', function(event, args) {
            angular.extend($scope.form, args);
            self.search();
        });

    },

    cloudController = function($scope, $rootScope, database, tabs) {

        database.frequency(database.granularity.DAY, new Date(), 150)
            .then(function(data){
                $scope.words = data.map(function(item){
                    return {
                        text: item.word,
                        weight: item.total + (4 * item.entries),
                        html: {
                            class: 'clickable'
                        },
                        handlers: {
                            "click": function() {
                                tabs.setTab(0);
                                $rootScope.$broadcast('search.simple', {
                                    query: item.word,
                                    advanced: false,
                                    subreddit: []
                                });
                            }
                        }
                    };
                });
            });

    },

    mainController = function($scope, tabs) {

        $scope.selectedIndex = 0;

        tabs.setObserver(function(index) {
            $scope.$apply(function(){
                $scope.selectedIndex = index;
            });
        });

    },

    databaseService = function($http, $httpParamSerializer) {

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

            var query = $httpParamSerializer(parameters);
            return $http.get('/search?' + query)
                .then(function(response) {
                    return response.data;
                });

        };

        /**
         *
         * @param granularity {('year'|'month'|'day')}
         * @param date {Date}
         * @param limit {number}
         */
        self.frequency = function(granularity, date, limit) {

            var query = $httpParamSerializer({
                gran: granularity,
                day: date.getDate(),
                month: date.getMonth() + 1,
                year: date.getFullYear(),
                limit: limit
            });

            return $http.get('/frequency?' + query)
                .then(function(response) {
                    return response.data;
                });

        }

        self.getSubreddits = function(){

            return $http.get('/subreddits')
                .then(function(response) {
                    return response.data;
                });

        }

    },

    tabsService = function() {

        var self = this,
            observer;

        self.setTab = function(tabIndex) {
            if (observer) {
                observer(tabIndex);
            }
        };

        self.setObserver = function(func) {

            observer = func;

        }

    };


    angular.module("RanalyzeApp", ['ngMaterial', 'md.data.table', 'angular-jqcloud'])
        .controller("searchController", searchController)
        .controller("cloudController", cloudController)
        .controller("mainController", mainController)
        .service("database", databaseService)
        .service("tabs", tabsService);

})(angular);