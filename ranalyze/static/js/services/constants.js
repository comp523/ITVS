(function(app){
"use strict";

    var CONSTANTS = {
        DATE: {
            FORMAT: 'yyyy-MM-dd'
        },
        MAX_REFRESH_TRIES: 10,
        REFRESH_INTERVAL: 10000
    };

    app.value('constants', CONSTANTS);

})(app);