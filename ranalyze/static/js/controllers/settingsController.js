(function(app){

    var settingsController = function($scope, $mdDialog, database){

        var self = this;

        self.subreddits = {
            all: [],
            selected: [],
            deleteSelected: function(){
                var numSubs = self.subreddits.selected.length;
                $mdDialog.show(
                    $mdDialog.confirm()
                        .title('Delete Subreddits')
                        .textContent('You are about to delete ' + numSubs + ' subreddit' + (numSubs>1?'s':''))
                        .ariaLabel('Delete Subreddits')
                        .ok('Delete')
                        .cancel('Never mind')
                )
                    .then(function(){
                        angular.forEach(self.subreddits.selected, function(sub){
                            sub.delete();
                        });
                    })
            },
            add: function(){

            }
        };

        database.config.getSubreddits(function(subs){
            self.subreddits.all = subs;
        });

        database.config.getCloudParams(function(data){
            angular.extend($scope.config, data);
        });

        $scope.config = {};

        $scope.table = {
            limit: 10,
            page: 1,
            order: 'name'
        };

    };

    app.controller('settingsController', settingsController);

})(app);