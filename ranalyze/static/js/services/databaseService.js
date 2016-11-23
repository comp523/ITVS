(function(app){
"use strict";

    var databaseService = function($resource, $q, $http, $httpParamSerializer) {

        var self = this;

        self.entry = $resource('/entry/:action', {}, {
            getSubreddits: {
                method: 'GET',
                params: {action: 'subreddits'},
                isArray: true
            },
            import: {
                method: 'POST',
                params: {action: 'import'},
                isArray: false,
                transformRequest: function(data){
                    var formdata = new FormData();
                    formdata.append('file', data.file);
                    return formdata;
                },
                headers: {
                    'content-type': undefined
                }
            },
            /** @override */
            query: {
                method: 'GET',
                isArray: false,
                transformResponse: function(json) {
                    var data = angular.fromJson(json);
                    for (var i=0, j=data.results.length;i<j;i++) {
                        data.results[i] = new self.entry(data.results[i]);
                    }
                    return data;
                }
            }
        });

        Object.defineProperty(self.entry.prototype, "type", {
            get: function(){
                return this.permalink ? "Post" : "Comment";
            }
        });

        self.frequency = $resource('/frequency/:action', {}, {
            overview: {
                method: 'GET',
                isArray: true,
                params: {action: "overview"}
            }
        });

        self.frequency.granularity = {
            YEAR: "year",
            MONTH: "month",
            DAY: "day"
        };

        self.config = $resource('/config/:field/:id', {},{
            getCloudParams: {
                method: 'GET',
                params: {
                    field: 'cloud'
                },
                transformResponse: function(json) {
                    var data = angular.fromJson(json);
                    angular.forEach(['entryWeight', 'totalWeight'], function(key) {
                        data[key] = parseFloat(data[key]);
                    });
                    return data;
                }
            },
            getSubreddits: {
                method: 'GET',
                isArray: true,
                params: {
                    field: 'subreddits'
                }
            }
        });
    };

    app.service('database', databaseService);

})(app);