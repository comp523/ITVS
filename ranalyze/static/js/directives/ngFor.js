(function(app){

    var ngForDirective = function(){
        return {
            link: function(scope, element, attrs) {
                var target = angular.element("html").find("#" + attrs.ngFor)[0];
                element.on("click", function(){
                    target.click();
                });
            },
            restrict: 'A'
        }
    };

    app.directive('ngFor', ngForDirective);

})(app);