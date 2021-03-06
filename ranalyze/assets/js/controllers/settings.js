(function(app){
"use strict";

    var settingsController = function($scope, $mdDialog, $q, $rootScope, $timeout, models){

        var ctrl = this,

        broadcastChange = function(){
            $scope.$emit('ranalyze.cloudConfig.change', {
                blacklist: ctrl.blacklist.all,
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
                deleteSelected: models.confirm(function() {
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
                            obj.delete().then(function success(){
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
                }),
                add: models.confirm(function() {
                    $mdDialog.show(
                        $mdDialog.prompt()
                            .title('Add words to cloud blacklist')
                            .placeholder('Word to blacklist')
                            .ok('Add')
                            .cancel('Cancel')
                    ).then(function(word){
                        var inBlacklist = false;
                        word = word.trim().toLowerCase();
                        angular.forEach(ctrl.blacklist.all, function(item){
                            inBlacklist |= word === item.value;
                        });
                        return inBlacklist ? $q.reject("'" + word + "' is already in the blacklist") :
                            models.Config.addToBlacklist(word).then(function success(item){
                                ctrl.blacklist.all.push(item);
                                broadcastChange();
                            }, function failure(){
                                return $q.reject('An error occurred while trying to add ' + word + ' to the blacklist');
                            });
                    }).catch(function failure(reason){
                        $scope.$emit('ranalyze.error', {
                            textContent: reason
                        });
                    });
                }),
                table: {
                    columnCount: 4,
                    limit: 20,
                    limitOptions: [20, 40, 80, 160],
                    page: 1
                }
            },
            cloud: {
                save: models.confirm(function(){
                    ctrl.cloud.saving.inProgress = true;
                    ctrl.cloud.saving.failed = false;
                    var promises = [];
                    promises.push(ctrl.cloud.entryWeight.commit().then(function success(){
                        ctrl.cloud.entryWeight.value = parseFloat(ctrl.cloud.entryWeight.value);
                    }));
                    promises.push(ctrl.cloud.totalWeight.commit().then(function(){
                        ctrl.cloud.totalWeight.value = parseFloat(ctrl.cloud.totalWeight.value);
                    }));
                    $q.all(promises).then(function success(){
                        broadcastChange();
                        ctrl.cloud.saving.succeeded = true;
                        // wait 3 second before hiding success indicator
                        $timeout(function(){
                            ctrl.cloud.saving.succeeded = false;
                        }, 3000);
                    }, function failure(){
                        ctrl.cloud.saving.failed = true;
                    }).finally(function(){
                        ctrl.cloud.saving.inProgress = false;
                    });
                }),
                saving: {
                    failed: false,
                    inProgress: false,
                    succeeded: false
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

            /**
             * Create an array containing a range of values. Equivalent to
             * Python's range function. Three parameters are used to calculate
             * the range, start, stop, and step. The range will be every step-th
             * number on the interval [start, stop). The function itself accepts
             * 1-3 parameters as follows:
             * range(x) -> start=0, stop=x, step=1
             * range(x,y) -> start=x, stop=y, step=1
             * range(x,y,z) -> start=x, stop=y, step=z
             *
             * @param x {number}
             * @param y {number=}
             * @param z {number=}
             * @return {number[]}
             */
            range: function(x, y, z) {
                var start = 0, stop, step = 1, range = [];
                switch (arguments.length) {
                    case 3:
                        step = z;
                        //fallthrough
                    case 2:
                        start = x;
                        stop = y;
                        break;
                    case 1:
                        stop = x;
                }
                for (;start < stop;start += step) range.push(start);
                return range;
            },
            subreddits: {
                add: models.confirm(function(){
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
                }),
                deleteSelected: models.confirm(function(){
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
                }),
                getAll: function(){
                    return models.Subreddit.collection
                },
                isRefreshing: models.Subreddit.isRefreshing,
                refresh: function(){
                   models.Subreddit.refresh().catch(function(){
                        $scope.$emit('ranalyze.error', {
                            textContent: 'An error occurred while trying to refresh subreddit stats'
                        });
                   });
                },
                selected: [],
                table: {
                    limit: 10,
                    limitOptions: [10, 25, 50, 100],
                    page: 1,
                    order: '-posts'
                }
            }
        });

        $rootScope.$on('ranalyze.blacklist.change', function(event, blacklist) {
            ctrl.blacklist.all = blacklist;
        });

        models.Config.getBlacklist().then(function success(value) {
            ctrl.blacklist.all = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `blacklist` from server."
            })
        });

        models.Config.getEntryWeight().then(function success(value) {
            ctrl.cloud.entryWeight = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `entryWeight` from server."
            });
        });

        models.Config.getTotalWeight().then(function success(value) {
            ctrl.cloud.totalWeight = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `totalWeight` from server."
            });
        });

        models.Config.getServerBlacklist().then(function success(value){
            ctrl.blacklist.serverList = value;
        }, function failure(){
            $scope.$emit('ranalyze.error', {
                textContent: "Couldn't get cloud parameter `serverBlacklist` from server."
            })
        });

    };

    app.controller('settingsController', settingsController);

})(app);