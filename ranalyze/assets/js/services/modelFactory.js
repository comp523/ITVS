(function(app){
"use strict";

    var modelFactoryFactory = function($log, $q){
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
         * @param options {object=}
         * @param options.collection {boolean=false}
         * @param options.instanceMethods {object=}
         * @param options.instanceProperties {object=}
         * @param options.staticProperties {object=}
         * @returns {Function}
         */
        return function(resource, options) {
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
            var prototype = {
                commit: function () {
                    var self = this;
                    return self.$resourceInstance.$save().then(function () {
                        if (collectionMode && Model.$uncommitted.indexOf(self.proxy) !== -1) {
                            Model.$uncommitted.splice(Model.$uncommitted.indexOf(self.proxy), 1);
                            Model.collection.push(self.proxy);
                        }
                        return self.proxy;
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
            };
            angular.extend(Model.prototype, prototype, instanceMethods);
            return angular.extend(Model, staticProperties);
        };
    };

    app.factory("modelFactory", modelFactoryFactory);

})(app);