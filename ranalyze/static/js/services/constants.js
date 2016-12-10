(function(app){
"use strict";

    var CONSTANTS = {

        /** Format for sanitizing dates to be passed to the API */
        DATE_FORMAT: 'yyyy-MM-dd',

        /** Number of attempts to refresh each stat before aborting */
        MAX_REFRESH_TRIES: 10,

        /** Time between automatic stat refreshes */
        REFRESH_INTERVAL: 10000,

        /** Number of likely SSO timeout error to ignore before alerting */
        SSO_ERROR_THRESHOLD: 0

    };

    app.value('constants', CONSTANTS);

})(app);