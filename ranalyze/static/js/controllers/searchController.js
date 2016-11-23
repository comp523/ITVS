(function(app){
"use strict";

    var searchController = function($scope, $mdDialog, database) {

        var self = this,
            baseForm = {
                advanced: false,
                subreddit: [],
                subredditMode: 'inclusive'
            };

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
                "/comments/" + entry.root_id.substring(3) + "/slug/" + entry.id.substring(3);

        };

        self.search = function(){
            var params = {
                limit: $scope.table.limit,
                order: $scope.table.order,
                offset: ($scope.table.page - 1) * $scope.table.limit
            };
            angular.extend(params, $scope.form);
            database.entry.query(params, function(results){
                if (results.total==0) {
                    $mdDialog.show(
                        $mdDialog.alert()
                            .clickOutsideToClose(true)
                            .title('No Results')
                            .textContent('This search yielded no results. Try broadening your criteria.')
                            .ariaLabel('No Results')
                            .ok('Ok')
                    );
                }
                if ($scope.form.advanced) {
                    var regex = /(["'])(.*?)\1/g;
                    $scope.highlight = [];
                    var match;
                    while ( (match = regex.exec($scope.form.query) ) !== null ) {
                        $scope.highlight.push(match[2]);
                    }
                }
                else {
                    $scope.highlight = $scope.form.query.split(" ");
                }
                self.entries = results.results;
                self.entryCount = results.total;
            });
        };

        database.entry.getSubreddits(function(subreddits){
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