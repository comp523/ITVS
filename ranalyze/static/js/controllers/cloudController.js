(function(app){
"use strict";

    var cloudController = function($scope, $rootScope, database, config, tabs) {

        var self = this;

        $scope.cloudParams = {};

        $scope.tableOrder = "-weight";

        $scope.selectedWords = [];

        var entryPromise = config.getEntryWeight().then(function(item) {
            $scope.cloudParams.entryWeight = item.value;
        });

        var totalPromise = config.getTotalWeight().then(function(item) {
            $scope.cloudParams.totalWeight = item.value;
        });

        self.updateWeights = function(){
            var _updateWeights = function(){
                var entryWeight = $scope.cloudParams.entryWeight,
                totalWeight = $scope.cloudParams.totalWeight;
                for (var i=0;i<$scope.words.length;i++) {
                    $scope.words[i].weight = entryWeight * $scope.words[i].entries + totalWeight * $scope.words[i].total;
                }
                // Trigger an update by deep copying the words array
                $scope.words = angular.copy($scope.words);
            };
            // Ensure both promises are resolved
            entryPromise.then(function(){
                totalPromise.then(_updateWeights);
            });
        };

        var d = new Date();

        database.Frequency.overview({
            gran: database.Frequency.granularity.DAY,
            limit: 150,
            year: d.getFullYear(),
            month: d.getMonth() + 1,
            day: d.getDate()
        }, function(data){
            $scope.masterWords = data.map(function(item){
                return {
                    text: item.word,
                    entries: item.entries,
                    total: item.total,
                    html: {
                        class: 'clickable'
                    },
                    handlers: {
                        "click": function() {
                            tabs.setTab(0);
                            $rootScope.$broadcast('search', {
                                query: item.word,
                                advanced: false,
                                subreddit: []
                            });
                        }
                    }
                };
            });
            $scope.words = angular.copy($scope.masterWords);
            self.updateWeights();
        });

    };

    app.controller('cloudController', cloudController);

})(app);