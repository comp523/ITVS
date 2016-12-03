(function(app){
"use strict";

    var databaseService = function($resource, $httpParamSerializer, $window) {

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
                    data.results = data.results.map(function(item) {
                        return new self.Entry(item);
                    });
                    return data;
                }
            }
        });

        self.Entry.downloadQuery = function(params) {
            params.download = true;
            var url = '/entry?' + $httpParamSerializer(params);
            $window.open(url);
        };

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

        self.Subreddit = $resource('/subreddit/:name', {
            name: '@name'
        });

        self.ConfigItem = $resource('/config/:id', {
            id: '@id'
        });

    };

    app.service('database', databaseService);

})(app);