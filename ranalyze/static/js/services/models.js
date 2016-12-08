(function(app){
"use strict";

    var modelsService = function($filter, $httpParamSerializer, $log, $q, $resource, $timeout, $window, constants) {

        var sanitizeDate = function(value) {
            return value ? $filter('date')(value, constants.DATE.FORMAT) : value;
        },
        refreshFailCount = 0,
        refreshFunctions = {
            import: function(){
                return Entry.$resource.get({action: "import"}, function success(results){
                    Entry.importing = results.queueLength > 0;
                }).$promise;
            },
            subreddits: function(){
                Subreddit.refreshing = true;
                return Subreddit.$resource.query({}, function success(results){
                    Subreddit.collection = results.map(function(item){
                        item = new Subreddit(item, true);
                        return item;
                    });
                    Subreddit.refreshing = false;
                }).$promise;
            }
        },
        refreshPromise,
        refreshStats = function(){
            var promises = [];
            if (refreshPromise) {
                $timeout.cancel(refreshPromise);
            }
            angular.forEach(refreshFunctions, function(fn, key) {
                promises.push(fn().then(function success(){
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
                }));
            });
            $q.all(promises)
                .finally(function(){
                    if (Object.keys(refreshFunctions).length > 0) {
                        refreshPromise = $timeout(refreshStats, constants.REFRESH_INTERVAL/4);
                    }
                });
        },
        resources = {
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
        };

        /**
         * Factory for creating constructors for  Models are wrappers
         * for angular's $resource. Additional instance methods may be defined
         * in options.instanceMethods, and properties in
         * options.instanceProperties, instance properties are treated as
         * getters, and will be passed the underlying $resource instance as an
         * argument. Additional static properties and methods may be defined in
         * options.staticProperties. If options.collection is set to true, all
         * created instances will be stored in an array available via the getAll
         * method of the constructor.
         *
         * The constructor creates objects with the following instance methods:
         * commit(): save changes to the server, if collection mode is on,
         *     this adds an object to the set of instances.
         * delete(): delete the element from the server.
         *
         * The constructor ob
         * @param resource {$resource}
         * @param options {Object|null}
         * @returns {Function}
         */
        var modelConstructorFactory = function(resource, options) {
            options = options || {};
            var collectionMode = options.collection === true,
                instanceMethods = options.instanceMethods || {},
                instanceProperties = options.instanceProperties || {},
                staticProperties = options.staticProperties;
                staticProperties.$resource = resource;
                if (collectionMode){
                    angular.extend(staticProperties, {
                        collection: collectionMode ? [] : undefined,
                        $uncommitted: collectionMode ? [] : undefined
                    });
                }
            var ProxyFactory = function(model) {
                return new Proxy(model, proxyHandler);
            },
            proxyHandler = {
                get: function(target, name, proxy) {

                    /* $resource instance is a private property, don't pass it through the proxy */
                    if (name in target && target[name] !== target.$resourceInstance) {

                        /* if the requested property is a function and not defined on the underlying
                           model object itself (e.g. is inherited prototypically), bind the underlying
                           model object to the function and return it. */
                        if (!target.hasOwnProperty(name) && angular.isFunction(target[name])){
                            return target[name].bind(target);
                        }
                        return target[name];
                    }

                    /* if the requested property is a getter defined in instanceProperties
                       call it bound to the proxy object with the underlying $resource as an
                       argument. */
                    else if (name in instanceProperties) {
                        return instanceProperties[name].call(proxy, target.$resourceInstance);
                    }

                    /* if the requested property exists on the underlying $resource object,
                       and is not an instance method (i.e. $save, $delete, etc.) return that
                       property.
                     */
                    else if (name in target.$resourceInstance && !angular.isFunction(target.$resourceInstance[name])) {
                        return target.$resourceInstance[name];
                    }
                    return undefined;
                },
                set: function(target, name, value) {
                    /* Only allow angular prefixed values to be assigned to the model,
                       not the underlying $resource instance. */
                    if (name.startsWith("$")) {
                        return target[name] = value;
                    }

                    /* Don't allow getters to be overridden */
                    else if (name in instanceProperties || name in target) {
                        $log.error("Can't set value of getter");
                    }
                    else {
                        return target.$resourceInstance[name] = value;
                    }
                }
            },

            /**
             *
             * @param a {$resource|Object}
             * @param committed {Boolean|undefined}
             * @constructor
             */
            Model = function(a, committed) {
                this.proxy = ProxyFactory(this);
                this.$resourceInstance = (a instanceof resource) ? a : new resource(a);
                if (collectionMode && committed !== true) {
                    Model.$uncommitted.push(this.proxy);
                }
                return this.proxy;
            };
            angular.extend(Model.prototype, {
                commit: function () {
                    var self = this;
                    return self.$resourceInstance.$save().then(function () {
                        if (collectionMode) {
                            Model.$uncommitted.splice(Model.$uncommitted.indexOf(self.proxy));
                            Model.collection.push(self.proxy);
                        }
                        return this;
                    });
                },
                delete: function () {
                    var self = this;
                    return self.$resourceInstance.$delete().then(function(){
                        if (collectionMode) {
                            if (Model.$uncommitted.indexOf(self.proxy) !== -1) {
                                Model.$uncommitted.splice(Model.$uncommitted.indexOf(self.proxy), 1);
                            }
                            else if (Model.collection.indexOf(self.proxy) !== -1) {
                                Model.collection.splice(Model.collection.indexOf(self.proxy), 1);
                            }
                        }
                    });
                }
            }, instanceMethods);
            return angular.extend(Model, staticProperties);
        };

        var Entry = this.Entry = modelConstructorFactory(resources.Entry, {
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
                downloadQuery: function(params) {
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
        });

        var Frequency = this.Frequency = modelConstructorFactory(resources.Frequency, {
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
        });

        var Subreddit = this.Subreddit =  modelConstructorFactory(resources.Subreddit, {
            collection: true,
            staticProperties: {
                refreshing: false,
                refresh: refreshStats,
                isScraping: function(){
                    var isScraping = false;
                    angular.forEach(Subreddit.collection, function(item) {
                        isScraping |= item.scraping;
                    });
                    return !!isScraping;
                }
            }
        });

        refreshStats();

    };

    app.service("models", modelsService);

})(app);