(function(app){
"use strict";

    /**
     *  Filter to retrieve only the file name from a full path.
     *  E.g. on a unix-like system:
     *  Input: /home/user/Documents/file.txt
     *  Output: file.txt
     */
    var fileNameFilter = function(){
        var slashRegExp = /[\/\\]/;
        return function(input) {
            if (input===undefined || !input.match(slashRegExp)) {
                return input;
            }
            var segments = input.split(slashRegExp);
            return segments[segments.length-1];
        };
    };

    app.filter("fileName", fileNameFilter);

})(app);