(function(app){
"use strict";

    var importController = function($scope, database) {

        var self = this;

        self.submit = function(){

            database.Entry.import({
                file: $scope.file.files[0]
            },
            function(data){
                $scope.response = data;
                $scope.file.value=null;
            });

        };

    };

    app.controller("importController", importController);

})(app);