(function(app){
"use strict";

    var searchController = function($scope, $mdDialog, constants, models) {

        var ctrl = this,
            baseForm = {
                advanced: false,
                subreddit: [],
                subredditMode: 'inclusive'
            },
            searchPromise, falseTableTrigger = false;
        angular.extend(ctrl, {
            search: {
                checkDates: function(){
                    var date1 = ctrl.search.form.after,
                        date2 = ctrl.search.form.before;

                    var valid = !(date1 && date2 && date1.getTime() >= date2.getTime());

                    $scope.searchForm.before.$setValidity('order', valid);

                },
                clear: function(){
                    ctrl.search.form = angular.copy(baseForm);
                },
                download: function(){
                    models.Entry.downloadSearch(ctrl.search.form);
                },
                execute: function(preservePage){
                    if (preservePage !== true) {
                        falseTableTrigger = ctrl.results.table.page !== 1;
                        ctrl.results.table.page = 1;
                    }
                    var params = angular.extend({
                        limit: ctrl.results.table.limit,
                        order: ctrl.results.table.order,
                        offset: (ctrl.results.table.page - 1) * ctrl.results.table.limit
                    }, ctrl.search.form);
                    var _execute = function() {
                        searchPromise = models.Entry.search(params)
                            .then(function success(data) {
                                ctrl.results.count = data.total;
                                ctrl.results.entries = data.results;
                                if (ctrl.results.count === 0) {
                                    $scope.$emit('ranalyze.error', {
                                        title: "No Results",
                                        textContent: "This search yielded no results. Try broadening your criteria."
                                    });
                                    return;
                                }
                                var query = ctrl.search.form.query;
                                if (ctrl.search.form.advanced) {
                                    var regex = /(["'])(.*?)\1/g;
                                    ctrl.results.highlight = [];
                                    var match;
                                    while ((match = regex.exec(query)) !== null) {
                                        ctrl.results.highlight.push(match[2]);
                                    }
                                }
                                else {
                                    ctrl.results.highlight = query.split(" ");
                                }
                            }, function failure() {
                                $scope.$emit('ranalyze.error', {
                                    textContent: "Something went wrong while trying to search."
                                });
                            });
                    };
                    if (!searchPromise) {
                        _execute();
                    }
                    else {
                        searchPromise.then(_execute);
                    }
                },
                querySubreddits: models.Entry.searchSubreddits,
                form: angular.copy(baseForm)
            },
            results: {
                count: 0,
                entries: [],
                highlight: [],
                table: {
                    limit: 10,
                    limitOptions: [10,25,50,100,250,500],
                    page: 1,
                    order: 'time_submitted'
                }
            }
        });

        $scope.$on('ranalyze.search', function onSearch(event, args) {
            ctrl.search.clear();
            angular.extend(ctrl.search.form, args);
            ctrl.search.execute();
        });

        $scope.$watchCollection(function getter(){
            return ctrl.results.table;
        }, function onChange(newValue, oldValue){
            if (falseTableTrigger) {
                falseTableTrigger = false;
                return;
            }
            if (!angular.equals(newValue, oldValue)) {
                ctrl.search.execute(true);
            }
        });

    };

    app.controller('searchController', searchController);

})(app);