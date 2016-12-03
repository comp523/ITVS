(function(app){
"use strict";

    var cloudController = function($scope, $rootScope, database, config, tabs) {

        var self = this;

        $scope.cloudParams = {};
        $scope.cloudParams.date = new Date();
        self.cloudMode = true;


        $scope.tableOrder = "-weight";

        $scope.selectedWords = [];

        var entryPromise = config.getEntryWeight().then(function success(item) {
            $scope.cloudParams.entryWeight = item.value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `entryWeight` from server."
            });
        });

        var totalPromise = config.getTotalWeight().then(function success(item) {
            $scope.cloudParams.totalWeight = item.value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `totalWeight` from server."
            });
        });

        var blacklistPromise;

        var updateBlacklist = function() {
            blacklistPromise = config.getBlacklist().then(function success(items) {
                $scope.cloudParams.blacklist = items.map(function (item) {
                    return item.value;
                });
            }, function failure() {
                $scope.$emit('ranalyze.error', {
                    textContent: "Couldn't get cloud parameter `blacklist` from server."
                });
            });
        };

        updateBlacklist();

        $scope.$on('ranalyze.blacklist.change', function(){
            updateBlacklist();
            self.updateWeights();
        });

        self.search = function(word) {
            tabs.setTab(0);
            $rootScope.$broadcast('search', {
                query: word,
                advanced: false,
                subreddit: []
            });
        };

        self.updateWeights = function(){
            var _updateWeights = function(){
                var entryWeight = $scope.cloudParams.entryWeight,
                totalWeight = $scope.cloudParams.totalWeight;
                for (var i=0;i<$scope.words.length;i++) {
                    $scope.words[i].weight = entryWeight * $scope.words[i].entries + totalWeight * $scope.words[i].total;
                }
                // Trigger an update by deep copying the words array
                $scope.words = angular.copy($scope.words);

                // Adding non-blacklisted words to the cloud view
                $scope.cloudParams.words = [];
                $scope.words.forEach(function(word) {
                    if (!$scope.cloudParams.blacklist.includes(word.text)) {
                        $scope.cloudParams.words.push(word);
                    }
                });
            };
            // Ensure all promises are resolved
            entryPromise.then(function(){
                totalPromise.then(function() {
                    blacklistPromise.then(_updateWeights);
                });
            });
        };

        /**
         * Updates the cloud with new date and weight parameters
         */
        self.updateCloud = function() {
            database.Frequency.overview({
                gran: database.Frequency.granularity.DAY,
                limit: 150,
                year: $scope.cloudParams.date.getFullYear(),
                month: $scope.cloudParams.date.getMonth() + 1,
                day: $scope.cloudParams.date.getDate()
            }, function success(data){
                $scope.words = data.map(function(item){
                    return {
                        text: item.word,
                        entries: item.entries,
                        total: item.total,
                        html: {
                            class: 'clickable'
                        },
                        handlers: {
                            "click": function() {
                                $rootScope.$apply(function(){
                                    self.search(item.word);
                                });
                            }
                        }
                    };
                });
                self.updateWeights();
            }, function failure(){
                $scope.$emit('ranalyze.error', {
                    textContent: "Couldn't get word frequency from server."
                });
            });
        };

        self.updateCloud();

    };

    app.controller('cloudController', cloudController);

})(app);