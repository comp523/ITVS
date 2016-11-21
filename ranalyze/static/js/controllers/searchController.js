(function(app){
"use strict";

    var searchController = function($scope, database) {

        var self = this;

        $scope.form = {
            subreddit: []
        };

        $scope.table = {
            limit: 10,
            page: 1,
            order: 'time_submitted'
        };

        $scope.$watchCollection('table', function(newValue, oldValue){
            if (!angular.equals(newValue, oldValue)) {
                self.search();
            }
        });

        self.highlight = [];

        self.entries = [];

        database.entry.getSubreddits()
            .then(function(subreddits){
                self.subreddits = subreddits;
            });

        self.filterSubs = function(sub) {

            var results = self.subreddits.filter(function(item){
                return item.toLowerCase().indexOf(sub.toLowerCase()) === 0;
            });

            return results || [];

        };

        self.getLink = function(entry){


            if (entry.permalink) {
                return entry.permalink;
            }

            return "https://www.reddit.com/r/" + entry.subreddit +
                "/comments/" + entry.root_id.substring(3);

        };

        self.search = function(download){
            download = !!download;
            var localParams = {
                download: !!download
            };
            if (!download) {
                angular.extend(localParams, {
                    limit: $scope.table.limit,
                    order: $scope.table.order,
                    offset: ($scope.table.page - 1) * $scope.table.limit
                });
            }
            angular.extend(localParams, $scope.form);
            database.entry.search(localParams)
                .then(function(data){
                    var results = data["results"],
                        count = data["total"];
                    if (download) {
                        angular.element('<a/>')
                            .attr({
                                href: 'data:attachment/csv;charset=utf-8,' + encodeURI(results),
                                target: '_blank',
                                download: 'results.csv'
                            })[0].click();
                    }
                    else {
                        self.entries = results.map(function (item) {
                            item.type = item.permalink ? "Post" : "Comment";
                            return item;
                        });
                        self.entryCount = count;
                    }
                });
            if ($scope.form.advanced) {
                var regex = /(["'])(.*?)\1/g;
                self.highlight = [];
                var match;
                while ( (match = regex.exec($scope.form.query) ) !== null ) {
                    self.highlight.push(match[2]);
                }
            }
            else {
                self.highlight = $scope.form.query.split(" ");
            }
        };

        $scope.$on('search.simple', function(event, args) {
            angular.extend($scope.form, args);
            self.search();
        });

    };

    app.controller('searchController', searchController);

})(app);