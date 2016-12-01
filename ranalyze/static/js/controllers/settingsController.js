(function(app){
"use strict";

    var settingsController = function($scope, $mdDialog, $timeout, config){

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
                            sub.$delete()
                                .then(function(){
                                    self.subreddits.all.splice(self.subreddits.all.indexOf(sub), 1);
                                    self.subreddits.selected.splice(self.subreddits.selected.indexOf(sub), 1);
                                });
                        });
                    })
            },
            add: function(){
                $mdDialog.show(
                    $mdDialog.prompt()
                        .title('Add subreddit to scrape')
                        .placeholder('subreddit')
                        .ok('Add')
                        .cancel('Cancel')
                )
                    .then(function(sub){
                        var item = new config.Item({
                            name: "subreddit",
                            value: sub
                        });
                        item.$save()
                            .then(function(){
                                self.subreddits.all.push(item);
                            });
                    });
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
                            obj.$delete()
                                .then(function(){
                                    self.blacklist.all.splice(self.blacklist.all.indexOf(obj), 1);
                                    self.blacklist.selected.splice(self.blacklist.selected.indexOf(obj), 1);
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
                            /*$.ajax({
                                method: 'POST',
                                url: '/config?blacklist='+res,
                            });*/
                            var item = new config.Item(obj);
                            item.$save();
                        }


                    })
            }
        };

        self.cloud = {
            save: function(){
                self.cloud.saving = true;
                self.cloud.savingDelayed = true;
                var entryPromise = self.cloud.entryWeight.$save()
                    .then(function(){
                        self.cloud.entryWeight.value = parseFloat(self.cloud.entryWeight.value);
                    }),
                    totalPromise = self.cloud.totalWeight.$save()
                    .then(function(){
                        self.cloud.totalWeight.value = parseFloat(self.cloud.totalWeight.value);
                    });
                entryPromise.then(function(){
                    totalPromise.then(function(){
                        self.cloud.saving = false;
                        // wait 3 second before hiding success indicator
                        $timeout(function(){
                            self.cloud.savingDelayed = false;
                        }, 3000);
                    });
                });
            }
        };

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