(function(app){
"use strict";

    var cloudController = function($scope, $rootScope, database, tabs) {

        var d = new Date();

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

    };

    app.controller('cloudController', cloudController);

})(app);