(function(app){
"use strict";

    var mainController = function($scope, database, tabs) {

        $scope.selectedIndex = 0;

        tabs.setObserver(function(index) {
            $scope.selectedIndex = index;
        });

        $scope.isScraping = function(){
            return database.Subreddit.scraping;
        };

    };

    app.controller('mainController', mainController);

})(app);