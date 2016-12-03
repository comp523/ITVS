(function(app){
"use strict";

    var mainController = function($scope, $interval, database, tabs) {

        $scope.selectedIndex = 0;

        tabs.setObserver(function(index) {
            $scope.selectedIndex = index;
        });

        $interval(function(){
            database.Subreddit.query({scraping: 1}, function(res) {
                $scope.scraping = res.length > 0;
            });
        }, 5000);

    };

    app.controller('mainController', mainController);

})(app);