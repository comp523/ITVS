(function(app){
"use strict";

    var settingsController = function($scope, $mdDialog, $rootScope, $timeout, config, constants, models){

        var self = this,

            broadcastChange = function(){
                $rootScope.$broadcast('ranalyze.cloudConfig.change', {
                    blacklist: self.blacklist.all.map(function(item){
                        return item.value;
                    }),
                    params: {
                        entryWeight: self.cloud.entryWeight.value,
                        totalWeight: self.cloud.totalWeight.value
                    }
                });
            },
            findSubredditByName = function(name) {
                for (var i=0,subs=self.subreddits.getAll(),j=subs.length;i<j;i++){
                    if (subs[i].name === name) {
                        return subs[i];
                    }
                }
            };

        self.subreddits = {
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
                        new models.Subreddit({
                            name: sub
                        }).commit()
                            .catch(function failure(){
                                $scope.$emit('ranalyze.error', {
                                    textContent: 'An error occurred while trying to save the subreddit `' + sub + '`'
                                });
                            });
                    });
            },
            deleteSelected: function(){
                $mdDialog.show(
                    $mdDialog.confirm()
                        .title('Delete Subreddits')
                        .textContent(constants.STRINGS.DELETE_SUBREDDIT_WARNING)
                        .ariaLabel('Delete Subreddits')
                        .ok('Delete')
                        .cancel('Never mind')
                )
                    .then(function(){
                        angular.forEach(self.subreddits.selected, function(name){
                            var sub = findSubredditByName(name);
                            if (!sub) {
                                $scope.$emit('ranalyze.error', {
                                    textContent: 'Subreddit `' + sub.name + '` has already been deleted'
                                });
                            }
                            sub.delete()
                                .then(function success(){
                                    self.subreddits.selected.splice(self.subreddits.selected.indexOf(name), 1);
                                }, function failure(){
                                    $scope.$emit('ranalyze.error', {
                                        textContent: 'An error occurred while trying to delete the subreddit `' + sub.name + '`'
                                    });
                                });
                        });
                    })
            },
            getAll: function(){
                return models.Subreddit.$collection
            },
            isRefreshing: function(){
                return models.Subreddit.refreshing
            },
            refresh: models.Subreddit.refresh,
            selected: [],
            table: {
                limit: 10,
                limitOptions: [10, 25, 50, 100],
                page: 1,
                order: '-posts'
            }
        };

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
                        var promiseCount = 0;
                        self.blacklist.selected.forEach(function(obj){
                            promiseCount ++;
                            obj.$delete()
                                .then(function success(){
                                    self.blacklist.all.splice(self.blacklist.all.indexOf(obj), 1);
                                    self.blacklist.selected.splice(self.blacklist.selected.indexOf(obj), 1);
                                    if (--promiseCount==0) {
                                        broadcastChange();
                                    }
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
                                    self.blacklist.all.push(item);
                                    broadcastChange();
                                }, function failure(response){
                                    $scope.$emit('ranalyze.error', {
                                        textContent: response
                                    });
                                });
                        }


                    })
            },
            table: {
                limit: 10,
                limitOptions: [10, 25, 50, 100],
                page: 1
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
                        broadcastChange();
                        self.cloud.saving = false;
                        // wait 3 second before hiding success indicator
                        $timeout(function(){
                            self.cloud.savingDelayed = false;
                        }, 3000);
                    });
                });
            }
        };

        self.import = {
            submit: function() {
                models.Entry.import({
                    file: self.import.file.files[0]
                }).then(function success(data) {
                    self.import.response = data;
                    self.import.file.value = null;
                }, function failure() {
                    $scope.$emit('ranalyze.error', {
                        textContent: "Couldn't import csv."
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

    };

    app.controller('settingsController', settingsController);

})(app);