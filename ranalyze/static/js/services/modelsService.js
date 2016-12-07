(function(app){
"use strict";

    var modelsService = function($httpParamSerializer, $log, $resource, $timeout, $window, constants) {

        var sanitizeDate = function(value) {
            return value ? $filter('date')(value, constants.DATE.FORMAT) : value;
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
         * getters. Additional static properties and methods may be defined in
         * options.staticProperties. If options.collection is set to true, all
         * created instances will be stored in an array available via the getAll
         * method of the constructor.
         *
         * The constructor creates objects with the following instance methods:
         * commit(): save changes to the server, if collection mode is on,
         *     this adds an object to the set of instances.
         * delete(): delete the element from the server.
         * get(property, skipCustom): retrieve a property from the underlying
         *     resource object, if skipCustom===true, instance properties
         *     defined in options.instanceProperties will be ignored.
         * set(property, value): set a property on the underlying resource
         *     object.
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
                        $collection: collectionMode ? [] : undefined,
                        $uncommitted: collectionMode ? [] : undefined
                    });
                }
            var ProxyFactory = function(model) {
                return new Proxy(model, proxyHandler);
            },
            proxyHandler = {
                get: function(target, name, proxy) {
                    if (name in target && target[name] !== target.$resourceInstance) {
                        if (!target.hasOwnProperty(name) && typeof target[name] === 'function'){
                            return target[name].bind(target);
                        }
                        return target[name];
                    }
                    if (name in instanceProperties) {
                        return instanceProperties[name].call(proxy);
                    }
                    if (name in target.$resourceInstance &&
                        typeof target.$resourceInstance[name] !== 'function') {
                        return target.$resourceInstance[name];
                    }
                    return undefined;
                },
                set: function(target, name, value) {
                    if (name.startsWith("$")) {
                        return target[name] = value;
                    }
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
                            Model.$collection.push(self.proxy);
                        }
                        return this;
                    });
                },
                delete: function () {
                    var self = this;
                    return self.$resourceInstance.$delete()
                        .then(function(){
                            if (collectionMode) {
                                if (Model.$uncommitted.indexOf(self.proxy) !== -1) {
                                    Model.$uncommitted.splice(Model.$uncommitted.indexOf(self.proxy), 1);
                                }
                                else if (Model.$collection.indexOf(self.proxy) !== -1) {
                                    Model.$collection.splice(Model.$collection.indexOf(self.proxy), 1);
                                }
                            }
                        });
                }
            }, instanceMethods);
            return angular.extend(Model, staticProperties);
        };

        var Entry = this.Entry = modelConstructorFactory(resources.Entry, {
            instanceProperties: {
                permalink: function getter(){
                    if (this.type === Entry.types.POST) {
                        return this.$resourceInstance.permalink;
                    }
                    return "https://www.reddit.com/r/" + this.subreddit +
                        "/comments/" + this.root_id.substring(3) + "/slug/" +
                        this.id.substring(3);
                },
                type: function getter(){
                    return this.$resourceInstance.permalink ? Entry.types.POST : Entry.types.COMMENT;
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
                searchSubreddits: function(name){
                    return Entry.$resource.query({
                        action: "subreddits",
                        name: name
                    }).$promise;
                },
                search: function(params) {
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
                $failCount: 0,
                refreshing: false,
                refresh: function(){
                    if (Subreddit.$refreshPromise) {
                        $timeout.cancel(Subreddit.$refreshPromise);
                    }
                    Subreddit.refreshing = true;
                    Subreddit.$resource.query({}, function success(results){
                        Subreddit.$collection = results.map(function(item){
                            item = new Subreddit(item, true);
                            return item;
                        });
                        Subreddit.refreshing = false;
                        Subreddit.$failCount = 0;
                        Subreddit.$refreshPromise = $timeout(Subreddit.refresh, constants.REFRESH_INTERVAL);
                    }, function failure(){
                        $log.warn("Couldn't refresh subreddits");
                        if (Subreddit.$failCount++ <= constants.MAX_REFRESH_TRIES) {
                            Subreddit.$refreshPromise = $timeout(Subreddit.refresh, constants.REFRESH_INTERVAL);
                        }
                        else {
                            $log.warn("Exceeded max refresh retries. Aborting.")
                        }
                    });
                },
                isScraping: function(){
                    var isScraping = false;
                    angular.forEach(Subreddit.$collection, function(item) {
                        isScraping |= item.scraping;
                    });
                    return isScraping;
                }
            }
        });

        Subreddit.refresh();

    };

    app.service("models", modelsService);

})(app);