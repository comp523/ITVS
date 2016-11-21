(function(app){
"use strict";

    var mainController = function($scope, tabs) {

        $scope.selectedIndex = 0;

        tabs.setObserver(function(index) {
            $scope.$apply(function(){
                $scope.selectedIndex = index;
            });
        });

    };

    app.controller('mainController', mainController);

})(app);