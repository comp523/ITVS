(function(app){
"use strict";

    var databaseService = function($resource, $q, $http, $httpParamSerializer) {

        var self = this;

        self.Entry = $resource('/entry/:action', {}, {
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
                        data.results[i] = new self.Entry(data.results[i]);
                    }
                    return data;
                }
            }
        });

        Object.defineProperty(self.Entry.prototype, "type", {
            get: function(){
                return this.permalink ? "Post" : "Comment";
            }
        });

        self.Frequency = $resource('/frequency/:action', {}, {
            overview: {
                method: 'GET',
                isArray: true,
                params: {action: "overview"}
            }
        });

        self.Frequency.granularity = {
            YEAR: "year",
            MONTH: "month",
            DAY: "day"
        };

        self.ConfigItem = $resource('/config/:id', {
            id: '@id'
        });

    };

    app.service('database', databaseService);

})(app);