(function(app){
"use strict";

    var searchController = function($scope, $mdDialog, database) {

        var self = this,
            baseForm = {
                advanced: false,
                subreddit: [],
                subredditMode: 'inclusive'
            };

        self.highlight = [];

        self.entries = [];

        self.clearForm = function(){

            $scope.form = angular.copy(baseForm);

        };

        self.clearForm();

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

        self.range = function(min, max, step) {
            step = step || 1;
            max = Math.ceil(max);
            var input = [];
            for (var i = min; i <= max; i += step) {
                input.push(i);
            }
            return input;
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
                    if (typeof data === 'object' && data["total"] == 0) {
                        $mdDialog.show(
                            $mdDialog.alert()
                                .clickOutsideToClose(true)
                                .title('No Results')
                                .textContent('This search yielded no results. Try broadening your criteria.')
                                .ariaLabel('No Results')
                                .ok('Ok')
                        );
                        return;
                    }
                    if (download) {
                        angular.element('<a/>')
                            .attr({
                                href: 'data:attachment/csv;charset=utf-8,' + encodeURI(data),
                                target: '_blank',
                                download: 'results.csv'
                            })[0].click();
                    }
                    else {
                        var results = data["results"],
                        count = data["total"];
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

        database.entry.getSubreddits()
            .then(function(subreddits){
                self.subreddits = subreddits;
            });

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

        $scope.$on('search', function(event, args) {
            $scope.form = angular.copy(baseForm);
            angular.extend($scope.form, args)
            self.search();
        });

        $scope.$watchGroup(['form.before', 'form.after'], function(){

            var date1 = $scope.form.after,
                date2 = $scope.form.before;

            var valid = !(date1 && date2 && date1.getTime() > date2.getTime());

            $scope.searchForm.before.$setValidity('order', valid);

        });

    };

    app.controller('searchController', searchController);

})(app);