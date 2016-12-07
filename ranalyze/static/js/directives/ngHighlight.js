(function(app){
"use strict";

    var ngHighlightDirective = function(){
        return {
            scope: {
                keywords: '&ngHighlight'
            },
            link: function(scope, element, attrs) {

                scope.$watchGroup(['keywords', function(){
                    return element.text();
                }], function(){
                    var regex = new RegExp('(' + scope.keywords().join('|') + ')', 'gi'),
                        text = element.text(),
                        highlightClass = attrs.ngHighlightClass || "highlight",
                        highlighted = text.replace(regex, "<span class=\"" + highlightClass + "\">$1</span>");
                    element.html(highlighted);
                });

            }
        }
    };

    app.directive('ngHighlight', ngHighlightDirective);

})(app);