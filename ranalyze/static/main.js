// Keeps track of which subreddits to add
var subreddits = new Set();

function addScrapeJobListner() {
    $(".scrape-job").on('click', function(event) {
        if (subreddits.has($(this).text())) {
            subreddits.delete($(this).text());
            $(this).css('text-decoration', 'line-through');
        } else {
            subreddits.add($(this).text());
            $(this).css('text-decoration', '');
        }
    });
}

function updateScrapeConfig(subreddits) {
    console.log(subreddits);
    $.ajax({
        method: 'POST',
        url: '/scrape',
        data: JSON.stringify(subreddits),
    }).done(function(res){
        $('#scrape-job-list').empty();
        console.log(res);
        subreddits = new Set();
        res.forEach(function(r) {
            console.log(r);
            subreddits.add(r);
            $('#scrape-job-list').append(
                '<li class="list-group-item scrape-job">'+
                r+
                '</li>');
        });
        addScrapeJobListner();
    });
}

function getScrapeSettings() {
    $.ajax('/scrape')
    .done(function(res){
        $('#scrape-job-list').empty();
        subreddits = new Set();
        res.forEach(function(r) {
            console.log(r);
            subreddits.add(r);
            $('#scrape-job-list').append(
                '<li class="list-group-item scrape-job">'+
                r+
                '</li>');
        });
        addScrapeJobListner();
    });
}

function addSubredditToDom(subreddit) {
    if (subreddits.has(subreddit)) return;
    else {
        subreddits.add(subreddit);
        var newSubElement = $('<li class="list-group-item scrape-job">'
                +subreddit
                +'</li>');
        $('#scrape-job-list').append(newSubElement);
        newSubElement.on('click', function(event) {
            if (subreddits.has(subreddit)) {
                subreddits.delete(subreddit);
                $(this).css('text-decoration', 'line-through');
            } else {
                subreddits.add(subreddit);
                $(this).css('text-decoration', '');
            }
        });
    }
}

function advancedSearch(searchConditions) {
    // empty object, don't send request
    if(Object.keys(searchConditions).length === 0
        && searchConditions.constructor === Object) return;
    $("#advanced-search-results>tbody").empty()
    $.ajax({
        method: 'POST',
        url: '/advanced_search/',
        data: JSON.stringify(searchConditions),
        success: function(res) {
            res.forEach(function(row) {
                var type = "";
                if(row.parent_id) {
                    type = "comment";
                } else {
                    type = "post";
                }
                var permalink = row.permalink ?
                    "<a target='_blank' href='"+row.permalink+"''><b>external link</b></a>"
                    : "N/A";
                $("#advanced-search-results").DataTable().row.add(
                    [type, permalink, row.subreddit, row.title, row.text_content]
                ).draw(false);
            });
            $('#download-advanced-search').removeAttr('hidden');
        }
    });
}

function search(searchConditions, download) {
    // empty object, don't send request
    if (download) {
        var url = "/search?",
            components = ["download=true"]
        for (var key in searchConditions) {
            if (searchConditions.hasOwnProperty(key)) {
                components.push(key + "=" + encodeURIComponent(searchConditions[key]));
            }
        }
        window.open(url + components.join("&"));
    }
    else {
        $("#search-results").DataTable().clear().draw();
        $.get('/search/', searchConditions,
            function(res) {
                res.forEach(function(row) {
                    var type = "";
                    if(row.parent_id) {
                        type = "comment";
                    } else {
                        type = "post";
                    }
                    var permalink = row.permalink ?
                        "<a target='_blank' href='"+row.permalink+"''><b>external link</b></a>"
                        : "N/A";
                    $("#search-results").DataTable().row.add(
                        [type, permalink, row.subreddit, row.title, row.text_content]
                    ).draw(false);
                });
            });
    }

}

function getTrendingWords(){
    var d = new Date(),
        month = d.getMonth() + 1,
        day = d.getDate();
    $.get("/frequency", {
        gran: "day",
        limit: "150",
        month: month,
        day: day
    }, function(data){
        var words = data.map(function(item){
            return {
                text: item.word,
                weight: item.total + (1.5 * item.entries)
            };
        });
        $("#tabcontainer").on("shown.bs.tab", function(){
            $("#word-frequency").jQCloud(words, {
                autoResize: true
            });
        });
    })
}

function addListeners() {
    $("#enable-advanced").change(function(){
        $("#query-label").html(this.checked ? "Expression" : "Keywords");
    });
    $('#search-button, #search-download').click(function() {
        var searchConditions = {};
        var advanced = $("#enable-advanced")[0].checked;
        if ($('#search-query').val()) {
            var queryKey = advanced ? "expression" : "keywords";
            searchConditions[queryKey] = $('#search-query').val();
        }
        if ($('#search-subreddits').val()) {
            searchConditions.subreddits = $('#search-subreddits').val().split(' ');
        }
        if ($('#search-after').val()) {
            searchConditions.after = $('#search-after').val().split(' ');
        }
        if ($('#search-before').val()) {
            searchConditions.before = $('#search-before').val().split(' ');
        }
        var download = $("#search-download").is(event.target);
        search(searchConditions, download);
    });
}



$(document).ready(function() {
    getScrapeSettings();
    getTrendingWords();
    addListeners();
    $('#search-after, #search-before').datepicker();

    $("#search-results").DataTable();

    $('#add-job').click(function() {
        addSubredditToDom($("#new-job").val().trim());
        $("#new-job").val('');
    });
    $('#save-jobs').click(function() {
        console.log(subreddits);
        var newState = [];
        subreddits.forEach(function(s){
            newState.push(s);
        });
        console.log('saving');
        //updateScrapeConfig(['abcd', 'efg']);
        updateScrapeConfig(newState);
    });
});