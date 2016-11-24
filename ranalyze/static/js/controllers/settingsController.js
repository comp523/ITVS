(function(app){
"use strict";

    var settingsController = function($scope, $mdDialog, config){

        var self = this;

        self.subreddits = {
            all: [],
            selected: [],
            deleteSelected: function(){
                var numSubs = self.subreddits.selected.length;
                $mdDialog.show(
                    $mdDialog.confirm()
                        .title('Delete Subreddits')
                        .textContent('You are about to delete ' + numSubs + ' subreddit' + (numSubs>1?'s':''))
                        .ariaLabel('Delete Subreddits')
                        .ok('Delete')
                        .cancel('Never mind')
                )
                    .then(function(){
                        angular.forEach(self.subreddits.selected, function(sub){
                            sub.delete();
                        });
                    })
            },
            add: function(){

            }
        };

        self.cloud = {};

        config.getSubreddits().then(function(subs){
            self.subreddits.all = subs;
        });

        config.getEntryWeight().then(function(value) {
            self.cloud.entryWeight = value;
        });

        config.getTotalWeight().then(function(value) {
            self.cloud.totalWeight = value;
        });

        $scope.table = {
            limit: 10,
            page: 1,
            order: 'name'
        };

    };

    app.controller('settingsController', settingsController);

})(app);