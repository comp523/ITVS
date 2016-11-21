(function(app){

    var settingsController = function($scope, database){

        var self = this;

        database.config.getSubreddits()
            .then(function(subs){
                self.subreddits = subs;
            });

        database.config.getCloudParams()
            .then(function(data){
                angular.extend($scope.config, data);
            });

        $scope.config = {};

        $scope.table = {
            limit: 10,
            page: 1,
            order: 'name'
        };

        $scope.selectedSubreddits = [];

    };

    app.controller('settingsController', settingsController);

})(app);