(function(app){
"use strict";

    var modelsService = function($filter, $httpParamSerializer, $log, $mdDialog, $q,
                                 $resource, $timeout, $window, constants, modelFactory) {

        var sanitizeDate = function(value) {
            return value ? $filter('date')(value, constants.DATE_FORMAT) : value;
        },

        /**
         * Dictionary of functions to refresh various stats. Each function should
         * return a Promise indicating the success or failure of the refresh.
         * @type {Object<string, function(): Promise>}
         */
        refreshFunctions = {
            import: function(){
                return Entry.$resource.get({action: "import"}, function success(results){
                    Entry.importing = results.queueLength > 0;
                }).$promise;
            },
            subreddits: function(){

                return Subreddit.$resource.query({}, function success(results){
                    Subreddit.collection = results.map(function(item){
                        item = new Subreddit(item, true);
                        Subreddit.$setRefreshing(false);
                        return item;
                    }, Subreddit.$setRefreshing);
                }).$promise;
            }
        },


        refreshPromise,

        /**
         * Runs on an interruptable timer, periodically running each function in refreshFunctions,
         * on an interval equal to constants.REFRESH_INTERVAL. If a promise returned by a function is rejected,
         * a fail counter is incremented, and once it exceeds constants.MAX_REFRESH_TRIES,
         * that function will be removed from refreshFunctions. Returns a combined promise which will be
         * rejected if any of the promised from refreshFunctions are rejected.
         * @returns {Promise}
         */
        refreshStats = function(){
            var promises = {};
            if (refreshPromise) {
                $timeout.cancel(refreshPromise);
            }
            angular.forEach(refreshFunctions, function(fn, key) {
                promises[key] = fn().then(function success(){
                    fn.failCount = 0;
                }, function failure(){
                    fn.failCount = (fn.failCount || 0) + 1;
                    var warning = "Refreshing stats for " + key + " failed "
                        + "(attempt " + fn.failCount + "/"
                        + constants.MAX_REFRESH_TRIES + ")...";
                    if (fn.failCount >= constants.MAX_REFRESH_TRIES) {
                        warning += " exceeded maximum attempts... aborting.";
                        delete refreshFunctions[key];
                    }
                    else {
                        warning += " retrying in " + constants.REFRESH_INTERVAL/1000 + " seconds.";
                    }
                    $log.warn(warning);
                    return $q.reject(warning);
                });
            });
            return $q.all(promises)
                .finally(function(){
                    if (Object.keys(refreshFunctions).length > 0) {
                        refreshPromise = $timeout(refreshStats, constants.REFRESH_INTERVAL);
                    }
                });
        },


        /**
         * Dictionary of $resource objects for use by the models.
         *
         * @type {object<string, $resource>}
         */
        resources = {
            Config: $resource('/config/:id', {
                id: '@id'
            }),
            Entry: $resource('/entry/:action', {}, {
                import: {
                    method: 'POST',
                    params: {
                        action: "import"
                    },
                    headers: {
                        'content-type': undefined
                    }
                },
                search: {
                    method: 'GET',
                    params: {
                        after: sanitizeDate,
                        before: sanitizeDate
                    },
                    transformResponse: function(json) {
                        var data = angular.fromJson(json);
                        data.results = data.results.map(function(item) {
                            return new resources.Entry(item);
                        });
                        return data;
                    }
                }
            }),
            Frequency: $resource('/frequency/:action'),
            Subreddit: $resource('/subreddit/:name', {
                name: '@name'
            })
        },

        noConfirm = false,

        confirm = this.confirm = function(fn) {

            return function(){
                var args = arguments;
                (noConfirm ? $q.resolve() : $mdDialog.show({
                    controller: confirmDialogController,
                    controllerAs: 'ctrl',
                    templateUrl: 'dialogs/config-warning.html'
                })).then(function(stopAsking){
                    if (stopAsking) {
                        noConfirm = true;
                    }
                    fn.apply(undefined, args);
                });
            };

        },

        /**
         *
         * @param name
         * @param options {object=}
         * @param options.isArray {boolean=true}
         * @param options.transformValues {function=}
         * @param options.transpose {boolean=true}
         * @returns {function(): Promise}
         */
        configGetterFactory = function(name, options) {
            options = options || {};
            var isArray = options.isArray !== false,
                transformValue = options.transformValues,
                transpose = options.transpose !== false;
            return function getter(){
                return Config.$resource.query({
                    name: name
                }).$promise.then(function(results){
                    results = results.map(function(item){
                        if (transformValue) {
                            item.value = transformValue(item.value);
                        }
                        return transpose ? new Config(item) : item;
                    });
                    return isArray ? results : results[0];
                });
            }
        },

        Config = this.Config = modelFactory(resources.Config, {
            staticProperties: {
                addToBlacklist: function(word) {
                    word = word.trim().toLowerCase();
                    var obj = {
                        'name': 'blacklist',
                        'value': word,
                    };
                    var item = new Config(obj);
                    return item.commit();
                },
                getBlacklist: configGetterFactory("blacklist"),
                getEntryWeight: configGetterFactory("entryWeight", {
                    isArray:false,
                    transformValues: parseFloat
                }),
                getTotalWeight: configGetterFactory("totalWeight", {
                    isArray:false,
                    transformValues: parseFloat
                }),
                getServerBlacklist: configGetterFactory("serverBlacklist", {
                    transpose: false
                })
            }
        }),

        Entry = this.Entry = modelFactory(resources.Entry, {
            instanceProperties: {
                permalink: function getter($resourceInstance){
                    if (this.type === Entry.types.POST) {
                        return $resourceInstance.permalink;
                    }
                    return "https://www.reddit.com/r/" + this.subreddit +
                        "/comments/" + this.root_id.substring(3) + "/slug/" +
                        this.id.substring(3);
                },
                type: function getter($resourceInstance){
                    return $resourceInstance.permalink ? Entry.types.POST : Entry.types.COMMENT;
                }
            },
            staticProperties: {
                downloadSearch: function(params) {
                    params.download = true;
                    var url = '/entry?' + $httpParamSerializer(params);
                    $window.open(url);
                },
                import: function(params){
                    var formData = new FormData();
                    angular.forEach(params, function(value, key) {
                        formData.append(key, value);
                    });
                    return Entry.$resource.import(formData).$promise;
                },
                importing: false,
                searchSubreddits: function(name){
                    return Entry.$resource.query({
                        action: "subreddits",
                        name: name
                    }).$promise;
                },
                search: function(params) {
                    angular.forEach(["after", "before"], function(key) {
                        params[key] = sanitizeDate(params[key]);
                    });
                    return Entry.$resource.search(params).$promise
                        .then(function success(data){
                            data.results = data.results.map(function(item) {
                                return new Entry(item);
                            });
                            return data;
                        });
                },
                types: {
                    COMMENT: "Comment",
                    POST: "Post"
                }
            }
        }),

        Frequency = this.Frequency = modelFactory(resources.Frequency, {
            staticProperties: {
                granularity: {
                    YEAR: "year",
                    MONTH: "month",
                    DAY: "day"
                },
                getOverview: function(params) {
                    params = angular.extend({
                        "action": "overview"
                    }, params);
                    return Frequency.$resource.query(params).$promise
                        .then(function(results) {
                            return results.map(function(item) {
                                return new Frequency(item);
                            })
                        });
                }
            }
        }),

        Subreddit = this.Subreddit =  modelFactory(resources.Subreddit, {
            collection: true,
            staticProperties: {
                isRefreshing: function(){
                    return subredditIsRefreshing;
                },
                refresh: refreshStats,
                $setRefreshing: function(value) {
                    subredditIsRefreshing = !!value;
                },
                isScraping: function(){
                    var isScraping = false;
                    angular.forEach(Subreddit.collection, function(item) {
                        isScraping |= item.scraping;
                    });
                    return !!isScraping;
                }
            }
        }),

        subredditIsRefreshing = false;

        refreshStats();

    };

    var confirmDialogController = function($scope, $mdDialog) {

        var ctrl = this;

        angular.extend(ctrl, {
            cancel: function(){
                $mdDialog.cancel('warning');
            },
            confirm: function(){
                $mdDialog.hide(ctrl.stopAsking);
            }
        });

    };

    app.service("models", modelsService);

})(app);