(function(app){
"use strict";

    var mainController = function($scope, models, tabs) {

        var ctrl = this;

        angular.extend(ctrl, {
            isScraping: models.Subreddit.isScraping,
            activeTab: 0
        });

        tabs.setObserver(function(index) {
            ctrl.activeTab = index;
        });

    };

    app.controller('mainController', mainController);

})(app);