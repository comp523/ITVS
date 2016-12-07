(function(app){
"use strict";

    var settingsController = function($scope, $mdDialog, $rootScope, $timeout, config, models){

        var ctrl = this,

        broadcastChange = function(){
            $rootScope.$broadcast('ranalyze.cloudConfig.change', {
                blacklist: ctrl.blacklist.all.map(function(item){
                    return item.value;
                }),
                params: {
                    entryWeight: ctrl.cloud.entryWeight.value,
                    totalWeight: ctrl.cloud.totalWeight.value
                }
            });
        },
        findSubredditByName = function(name) {
            for (var i=0,subs=ctrl.subreddits.getAll(),j=subs.length;i<j;i++){
                if (subs[i].name === name) {
                    return subs[i];
                }
            }
        };

        angular.extend(ctrl, {
            blacklist: {
                all: [],
                selected: [],
                serverList: [],
                deleteSelected: function() {
                    var numSelected = ctrl.blacklist.selected.length;
                    $mdDialog.show(
                        $mdDialog.confirm()
                            .title('Remove words from cloud blacklist')
                            .textContent('You are about to remove ' + numSelected +
                                ' word' + (numSelected>1?'s':'') + " from the blacklist")
                            .ariaLabel('Delete Subreddits')
                            .ok('Delete')
                            .cancel('Never mind')
                    ).then(function success(){
                        var promiseCount = 0;
                        ctrl.blacklist.selected.forEach(function(obj){
                            promiseCount ++;
                            obj.$delete().then(function success(){
                                ctrl.blacklist.all.splice(ctrl.blacklist.all.indexOf(obj), 1);
                                ctrl.blacklist.selected.splice(ctrl.blacklist.selected.indexOf(obj), 1);
                                if (--promiseCount==0) {
                                    broadcastChange();
                                }
                            }, function failure(){
                                $scope.$emit('ranalyze.error', {
                                    textContent: 'An error occurred while trying to delete the blacklist word `' + obj.value + '`'
                                });
                            });
                        });
                        ctrl.blacklist.selected = [];
                    });
                },
                add: function() {
                    $mdDialog.show(
                        $mdDialog.prompt()
                            .title('Add words to cloud blacklist')
                            .placeholder('Word to blacklist')
                            .ok('Add')
                            .cancel('Cancel')
                    ).then(function(res) {
                        res = res.trim();
                        var contains = false;
                        for(var i=0,j=ctrl.blacklist.all.length;i<j;i++){
                            if (ctrl.blacklist.all[i].value == res) {
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
                            item.$save().then(function success(){
                                ctrl.blacklist.all.push(item);
                                broadcastChange();
                            }, function failure(response){
                                $scope.$emit('ranalyze.error', {
                                    textContent: response
                                });
                            });
                        }
                    });
                },
                table: {
                    limit: 10,
                    limitOptions: [10, 25, 50, 100],
                    page: 1
                }
            },
            cloud: {
                save: function(){
                    ctrl.cloud.saving = true;
                    ctrl.cloud.savingDelayed = true;
                    var entryPromise = ctrl.cloud.entryWeight.$save().then(function success(){
                        ctrl.cloud.entryWeight.value = parseFloat(ctrl.cloud.entryWeight.value);
                    }, function failure(){
                        $scope.$emit('ranalyze.error', {
                            textContent: 'An error occurred while trying to save cloud parameter `entryWeight`'
                        });
                    }),
                    totalPromise = ctrl.cloud.totalWeight.$save().then(function(){
                        ctrl.cloud.totalWeight.value = parseFloat(ctrl.cloud.totalWeight.value);
                    }, function failure(){
                        $scope.$emit('ranalyze.error', {
                            textContent: 'An error occurred while trying to save cloud parameter `totalWeight`'
                        });
                    });
                    entryPromise.then(function(){
                        totalPromise.then(function(){
                            broadcastChange();
                            ctrl.cloud.saving = false;
                            // wait 3 second before hiding success indicator
                            $timeout(function(){
                                ctrl.cloud.savingDelayed = false;
                            }, 3000);
                        });
                    });
                }
            },
            import: {
                submit: function() {
                    models.Entry.import({
                        file: ctrl.import.file.files[0]
                    }).then(function success(data) {
                        ctrl.import.response = data;
                        ctrl.import.file.value = null;
                    }, function failure() {
                        $scope.$emit('ranalyze.error', {
                            textContent: "Couldn't import csv."
                        });
                    });
                }
            },
            subreddits: {
                add: function(){
                    $mdDialog.show(
                        $mdDialog.prompt()
                            .title('Add subreddit to scrape')
                            .placeholder('subreddit')
                            .ok('Add')
                            .cancel('Cancel')
                    ).then(function(sub){
                        sub = sub.trim();
                        new models.Subreddit({
                            name: sub
                        }).commit().catch(function failure(){
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
                            .textContent('Deleting a subreddit means that it will no longer be scraped,' +
                                         ' it does not remove existing posts and comments from the database.')
                            .ariaLabel('Delete Subreddits')
                            .ok('Delete')
                            .cancel('Never mind')
                    ).then(function(){
                        angular.forEach(ctrl.subreddits.selected, function(name){
                            var sub = findSubredditByName(name);
                            if (!sub) {
                                $scope.$emit('ranalyze.error', {
                                    textContent: 'Subreddit `' + sub.name + '` has already been deleted'
                                });
                            }
                            sub.delete().then(function success(){
                                ctrl.subreddits.selected.splice(ctrl.subreddits.selected.indexOf(name), 1);
                            }, function failure(){
                                $scope.$emit('ranalyze.error', {
                                    textContent: 'An error occurred while trying to delete the subreddit `' + sub.name + '`'
                                });
                            });
                        });
                    })
                },
                getAll: function(){
                    return models.Subreddit.collection
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
            }
        });

        config.getEntryWeight().then(function success(value) {
            ctrl.cloud.entryWeight = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `entryWeight` from server."
            });
        });

        config.getTotalWeight().then(function success(value) {
            ctrl.cloud.totalWeight = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `totalWeight` from server."
            });
        });

        config.getBlacklist().then(function success(value) {
            ctrl.blacklist.all = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `blacklist` from server."
            })
        });

        config.getServerBlacklist().then(function success(value){
            ctrl.blacklist.serverList = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `serverBlacklist` from server."
            })
        });

    };

    app.controller('settingsController', settingsController);

})(app);