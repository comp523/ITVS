(function(app){
"use strict";

    var mainController = function($scope, models, tabs) {

        var self = this;

        self.selectedIndex = 0;

        tabs.setObserver(function(index) {
            self.selectedIndex = index;
        });

        self.isScraping = models.Subreddit.isScraping;

    };

    app.controller('mainController', mainController);

})(app);