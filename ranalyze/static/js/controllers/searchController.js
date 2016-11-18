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

        self.search = function(download){
            var localParams = {download: !!download};
            angular.extend(localParams, $scope.form);
            database.entry.search(localParams)
                .then(function(data){
                    if (!!download) {
                        angular.element('<a/>')
                            .attr({
                                href: 'data:attachment/csv;charset=utf-8,' + encodeURI(data),
                                target: '_blank',
                                download: 'results.csv'
                            })[0].click();
                    }
                    else {
                        self.entries = data.map(function (item) {
                            item.type = item.permalink ? "Post" : "Comment";
                            return item;
                        });
                    }
                });
            if ($scope.form.advanced) {
                var regex = /(["'])(.*?)\1/g;
                $scope.highlight = [];
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