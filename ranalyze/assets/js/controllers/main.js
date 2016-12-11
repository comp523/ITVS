(function(app){
"use strict";

    var mainController = function($scope, models, tabs) {

        var ctrl = this,
        status = {
            importing: false,
            scraping: false
        };

        angular.extend(ctrl, {
            activeTab: 0,
            getStatus: function(){
                status.scraping = models.Subreddit.isScraping();
                status.importing = models.Entry.importing;
                return status;
            }
        });

        tabs.setObserver(function(index) {
            ctrl.activeTab = index;
        });

    };

    app.controller('mainController', mainController);

})(app);