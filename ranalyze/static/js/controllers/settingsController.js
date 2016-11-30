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
                            sub.$delete();
                        });
                    })
            },
            add: function(){

            }
        };

        self.blacklist = {
            all: [],
            selected: [],
            deleteSelected: function() {
                var numSelected = self.blacklist.selected.length;
                $mdDialog.show(
                    $mdDialog.confirm()
                        .title('Remove words from cloud blacklist')
                        .textContent('You are about to remove ' + numSelected + ' word' + (numSelected>1?'s':'')
                            + " from the blacklist"
                        )
                        .ariaLabel('Delete Subreddits')
                        .ok('Delete')
                        .cancel('Never mind')
                )
                    .then(function() {
                        self.blacklist.selected.forEach(function(obj){
                            // TODO: rest call to config here
                            var word = obj.value;
                            self.blacklist.all.splice(self.blacklist.all.indexOf(obj), 1);
                            $.ajax({
                                method: 'DELETE',
                                url: '/config?blacklist='+word,
                            });
                        });
                        self.blacklist.selected = [];
                    })
            },
            add: function() {
                $mdDialog.show(
                    $mdDialog.prompt()
                        .title('Add words to cloud blacklist')
                        .placeholder('Word to blacklist')
                        .ok('Add')
                        .cancel('Cancel')
                )
                    .then(function(res) {
                        // TODO: fix the below hacks
                        res = res.trim();
                        var contains = false;
                        for(var i in self.blacklist.all){
                            if (self.blacklist.all[i].value
                            && self.blacklist.all[i].value == res) {
                               contains = true;
                            }
                        }
                        if (!contains) {
                            var obj = {
                                'name': 'blacklist',
                                'value': res,
                            };
                            self.blacklist.all.push(obj);
                            $.ajax({
                                method: 'POST',
                                url: '/config?blacklist='+res,
                            });
                        }


                    })
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

        config.getBlacklist().then(function(value) {
            self.blacklist.all = value;
        });

        $scope.table = {
            limit: 10,
            page: 1,
            order: 'name'
        };

    };

    app.controller('settingsController', settingsController);

})(app);