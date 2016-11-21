(function(app){
"use strict";

    var importController = function($scope, database) {

        var self = this;

        self.submit = function(){

            database.entry.import($scope.file.element)
                .then(function(data){
                    $scope.response = data;
                    $scope.file.element.val(null);
                });

        };

    };

    app.controller("importController", importController);

})(app);