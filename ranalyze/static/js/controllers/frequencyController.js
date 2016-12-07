(function(app){
"use strict";

    var frequencyController = function($scope, $rootScope, config, models, tabs) {

        var self = this;

        self.cloud = {
            words: [],
            update: function(){
                var _update = function () {
                    self.cloud.words = self.frequency.words.filter(function(word) {
                        return !blacklist.includes(word.text);
                    });
                    // Deep copy to trigger cloud update
                    self.cloud.words = angular.copy(self.cloud.words);
                };
                blacklistPromise.then(_update);
            }
        };

        self.frequency = {
            params: {
                date_before: new Date(),
                date_after: new Date()
            },
            selectedWords: [],
            words: [],
            updateWeights: function(){
                var _updateWeights = function(){
                    var entryWeight = self.frequency.params.entryWeight,
                    totalWeight = self.frequency.params.totalWeight;
                    for (var i=0,j=self.frequency.words.length,word;i<j;i++) {
                        word = self.frequency.words[i];
                        word.weight = entryWeight * word.entries + totalWeight * word.total;
                    }
                    self.cloud.update();
                };
                // Ensure all promises are resolved
                entryPromise.then(function(){
                    totalPromise.then(_updateWeights);
                });
            },
            updateWords: function() {
                models.Frequency.getOverview({
                    gran: models.Frequency.granularity.DAY,
                    limit: 150,
                    year_before: self.frequency.params.date_before.getFullYear(),
                    month_before: self.frequency.params.date_before.getMonth()+1,
                    day_before: self.frequency.params.date_before.getDate(),

                    year_after: self.frequency.params.date_after.getFullYear(),
                    month_after: self.frequency.params.date_after.getMonth()+1,
                    day_after: self.frequency.params.date_after.getDate()
                }).then(function success(data){
                    self.frequency.words = data.map(function(item){
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
                    self.frequency.updateWeights();
                }, function failure(){
                    $scope.$emit('ranalyze.error', {
                        textContent: "Couldn't get word frequency from server."
                    });
                });
            },
            table: {
                limit: 10,
                limitOptions: [10, 25, 50, 100],
                order: "-weight",
                page: 1
            }
        };

        self.search = function(word) {
            tabs.setTab(0);
            $rootScope.$broadcast('ranalyze.search', {
                query: word,
                after: self.frequency.params.date_after,
                before: self.frequency.params.date_before,
                advanced: false,
                subreddit: []
            });
        };

        var entryPromise = config.getEntryWeight().then(function success(item) {
            self.frequency.params.entryWeight = item.value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `entryWeight` from server."
            });
        });

        var totalPromise = config.getTotalWeight().then(function success(item) {
            self.frequency.params.totalWeight = item.value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `totalWeight` from server."
            });
        });

        var blacklistPromise, blacklist = [];

        var updateBlacklist = function() {
            blacklistPromise = config.getBlacklist().then(function success(items) {
                blacklist = items.map(function (item) {
                    return item.value;
                });
            }, function failure() {
                $scope.$emit('ranalyze.error', {
                    textContent: "Couldn't get cloud parameter `blacklist` from server."
                });
            });
        };

        $scope.$on('ranalyze.cloudConfig.change', function(event, newConfig){
            angular.extend(self.frequency.params, newConfig.params);
            blacklist = newConfig.blacklist;
            self.frequency.updateWeights();
        });

        updateBlacklist();

        self.frequency.updateWords();

    };

    app.controller('frequencyController', frequencyController);

})(app);