(function(app){
"use strict";

    var cloudController = function($scope, $rootScope, database, tabs) {

        var d = new Date();

        $scope.cloudParams = {};

        var defaultsPromise = database.getCloudParamDefaults()
            .then(function(defaults){
                angular.extend($scope.cloudParams, defaults)
            });

        self.updateWeights = function(){
            defaultsPromise.then(function(){
                var entryWeight = $scope.cloudParams.entryWeight,
                    totalWeight = $scope.cloudParams.totalWeight;
                for (var i=0;i<$scope.words.length;i++) {
                    $scope.words[i].weight = entryWeight * $scope.words[i].entries + totalWeight * $scope.words[i].total;
                }
            });
        };

        database.frequency({
            gran: database.granularity.DAY,
            limit: 150,
            year: 2016, //d.getFullYear()
            month: 11, //d.getMonth() + 1
            day: 14 //d.getDate()
        })
            .then(function(data){
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
                self.updateWeights();
            });

    };

    app.controller('cloudController', cloudController);

})(app);