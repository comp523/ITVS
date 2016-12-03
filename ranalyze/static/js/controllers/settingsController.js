(function(app){
"use strict";

    var settingsController = function($scope, $mdDialog, $timeout, config, constants, database){

        var self = this;

        self.subreddits = {
            all: [],
            selected: [],
            deleteSelected: function(){
                var numSubs = self.subreddits.selected.length;
                $mdDialog.show(
                    $mdDialog.confirm()
                        .title('Delete Subreddits')
                        .textContent(constants.STRINGS.DELETE_SUBREDDIT_WARNING)
                        .ariaLabel('Delete Subreddits')
                        .ok('Delete')
                        .cancel('Never mind')
                )
                    .then(function(){
                        angular.forEach(self.subreddits.selected, function(sub){
                            sub.$delete()
                                .then(function success(){
                                    self.subreddits.all.splice(self.subreddits.all.indexOf(sub), 1);
                                    self.subreddits.selected.splice(self.subreddits.selected.indexOf(sub), 1);
                                }, function failure(){
                                    $scope.$emit('ranalyze.error', {
                                        textContent: 'An error occurred while trying to delete the subreddit `' + sub.value + '`'
                                    });
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
                        sub = sub.trim();
                        var item = new database.Subreddit({
                            name: sub
                        });
                        item.$save()
                            .then(function success(){
                                self.subreddits.all.push(item);
                            }, function failure(){
                                $scope.$emit('ranalyze.error', {
                                    textContent: 'An error occurred while trying to save the subreddit `' + sub + '`'
                                });
                            });
                    });
            },
            get: function(){
                self.subreddits.getting = true;
                database.Subreddit.query({}, function success(subs){
                    self.subreddits.all = subs;
                    self.subreddits.getting = false;
                }, function failure(){
                    $scope.$emit('ranalyze.error', {
                        textContent: "Couldn't get list of subreddits from server."
                    });
                });
            }
        };

        self.subreddits.get();

        self.blacklist = {
            all: [],
            selected: [],
            serverList: [],
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
                    .then(function success(){
                        self.blacklist.selected.forEach(function(obj){
                            obj.$delete()
                                .then(function success(){
                                    self.blacklist.all.splice(self.blacklist.all.indexOf(obj), 1);
                                    self.blacklist.selected.splice(self.blacklist.selected.indexOf(obj), 1);
                                }, function failure(){
                                    $scope.$emit('ranalyze.error', {
                                        textContent: 'An error occurred while trying to delete the blacklist word `' + obj.value + '`'
                                    });
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
                        res = res.trim();
                        var contains = false;
                        for(var i=0,j=self.blacklist.all.length;i<j;i++){
                            if (self.blacklist.all[i].value == res) {
                                contains = true;
                                break;
                            }
                        }
                        if (!contains) {
                            var obj = {
                                'name': 'blacklist',
                                'value': res,
                            };
                            var item = new config.Item(obj);
                            item.$save()
                                .then(function success(){
                                    self.blacklist.all.push(obj);
                                }, function failure(response){
                                    $scope.$emit('ranalyze.error', {
                                        textContent: response
                                    });
                                });
                        }


                    })
            }
        };

        self.cloud = {
            save: function(){
                self.cloud.saving = true;
                self.cloud.savingDelayed = true;
                var entryPromise = self.cloud.entryWeight.$save()
                        .then(function success(){
                            self.cloud.entryWeight.value = parseFloat(self.cloud.entryWeight.value);
                        }, function failure(){
                            $scope.$emit('ranalyze.error', {
                                textContent: 'An error occurred while trying to save cloud parameter `entryWeight`'
                            });
                        }),
                    totalPromise = self.cloud.totalWeight.$save()
                        .then(function(){
                            self.cloud.totalWeight.value = parseFloat(self.cloud.totalWeight.value);
                        }, function failure(){
                            $scope.$emit('ranalyze.error', {
                                textContent: 'An error occurred while trying to save cloud parameter `totalWeight`'
                            });
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

        config.getEntryWeight().then(function success(value) {
            self.cloud.entryWeight = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `entryWeight` from server."
            });
        });

        config.getTotalWeight().then(function success(value) {
            self.cloud.totalWeight = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `totalWeight` from server."
            });
        });

        config.getBlacklist().then(function success(value) {
            self.blacklist.all = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `blacklist` from server."
            })
        });

        config.getServerBlacklist().then(function success(value){
            self.blacklist.serverList = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `serverBlacklist` from server."
            })
        });

        $scope.table = {
            limit: 10,
            page: 1,
            order: 'name'
        };

    };

    app.controller('settingsController', settingsController);

})(app);