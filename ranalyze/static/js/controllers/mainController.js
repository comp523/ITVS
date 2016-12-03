(function(app){
"use strict";

    var mainController = function($scope, database, tabs) {

        $scope.selectedIndex = 0;

        tabs.setObserver(function(index) {
            $scope.selectedIndex = index;
        });

        database.Subreddit.query({scraping: 1}, function(res) {
            $scope.scraping = res.length > 0;
        });

    };

    app.controller('mainController', mainController);

})(app);