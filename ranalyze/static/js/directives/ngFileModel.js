(function(app){
"use strict";

    /**
     *  Directive for binding the value of a file input object
     *  to a special object with two properties:
     *  files: the array of File objects selected
     *  value: the text value of the file input element
     */
    var ngFileModelDirective = function(){
        return {
            scope: {
                ngFileModel: "="
            },
            link: function(scope, element) {
                scope.ngFileModel = scope.ngFileModel || {};
                element.on("change", function(){
                    scope.$apply(function(){
                        scope.ngFileModel['files'] = element[0].files;
                        scope.ngFileModel['value'] = element.val();
                    });
                });
            },
            restrict: 'A'
        }
    };

    app.directive('ngFileModel', ngFileModelDirective);

})(app);