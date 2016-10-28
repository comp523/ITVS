// Keeps track of which subreddits to add
var subreddits = new Set();
var removedSubreddits = new Set();
function addScrapeJobListner() {
	$(".scrape-job").on('click', function(event) {
		if(removedSubreddits.has($(this).text())) {
			removedSubreddits.delete($(this).text());
			$(this).css('text-decoration', '');
		} else {
			removedSubreddits.add($(this).text());
			$(this).css('text-decoration', 'line-through');
		}
	});
}

function addJob(subreddit) {

}

function updateScrapeConfig(subreddits) {
	$.ajax({
		method: 'POST',
		url: '/scrape', 
		data: JSON.stringify(subreddits),
		success: getScrapeSettings()
	});
}

function getScrapeSettings() {
	$.ajax('/scrape')
	.done(function(res){
		$('#scrape-jobs').empty();
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
		$('#scrape-job-list').append(
				'<li class="list-group-item scrape-job">'
				+subreddit
				+'</li>');
	}
}

function advancedSearch(searchConditions) {
	// empty object, don't send request
	if(Object.keys(searchConditions).length === 0 
		&& searchConditions.constructor === Object) return;
	$("#advanced-search-results").empty()
	$("#advanced-search-results")
	.append("<tr><th>Type</th>"
		+"<th>Permalink</th>"
		+"<th>Subreddit</th>"
		+"<th>Title</th>"
		+"<th>Text</th>"
		+"</tr>");
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
				$("#advanced-search-results").append(
					"<tr>"
					+"<td>"+type+"</td>"
					+"<td>"+row.permalink+"</td>"
					+"<td>"+row.subreddit+"</td>"
					+"<td>"+row.title+"</td>"
					+"<td>"+row.text_content+"</td>"
					+"</tr>"
				);
			});
		}
	});
}

function simpleSearch(searchConditions) {
	// empty object, don't send request
	if(Object.keys(searchConditions).length === 0 
		&& searchConditions.constructor === Object) return;
	$("#simple-search-results").empty()
	$("#simple-search-results")
	.append("<tr><th>Type</th>"
		+"<th>Permalink</th>"
		+"<th>Subreddit</th>"
		+"<th>Title</th>"
		+"<th>Text</th>"
		+"</tr>");
	$.ajax({
		method: 'POST',
		url: '/simple_search/', 
		data: JSON.stringify(searchConditions),
		success: function(res) {
			res.forEach(function(row) {
				var type = "";
				if(row.parent_id) {
					type = "comment";
				} else {
					type = "post";
				}
				$("#simple-search-results").append(
					"<tr>"
					+"<td>"+type+"</td>"
					+"<td>"+row.permalink+"</td>"
					+"<td>"+row.subreddit+"</td>"
					+"<td>"+row.title+"</td>"
					+"<td>"+row.text_content+"</td>"
					+"</tr>"
				)
			});
		}
	});
}

function addListeners() {
	// Simple Search Listener
	$('#simple-search-button').click(function() {
		var searchConditions = {};
		if ($('#simple-search-keywords').val().length) {
			searchConditions.keywords = $('#simple-search-keywords').val().split(' ');
		}
		if ($('#simple-search-subreddits').val().length) {
			searchConditions.subreddits = $('#simple-search-subreddits').val().split(' ');
		}
		if ($('#simple-search-after').val().length) {
			searchConditions.after = $('#simple-search-after').val().split(' ');
		}
		if ($('#simple-search-before').val().length) {
			searchConditions.before = $('#simple-search-before').val().split(' ');
		}
		simpleSearch(searchConditions);
	});
	// Advanced Search Listener
	$('#advanced-search-button').click(function() {
		var searchConditions = {};
		if ($('#advanced-search-expression').val().length) {
			// unlike simple, don't split
			searchConditions.expression = $('#advanced-search-expression').val();
		}
		if ($('#advanced-search-subreddits').val().length) {
			searchConditions.subreddits = $('#advanced-search-subreddits').val().split(' ');
		}
		if ($('#advanced-search-after').val().length) {
			searchConditions.after = $('#advanced-search-after').val().split(' ');
		}
		if ($('#advanced-search-before').val().length) {
			searchConditions.before = $('#advanced-search-before').val().split(' ');
		}
		advancedSearch(searchConditions);
	});
}



$(document).ready(function() {
	getScrapeSettings();
	addListeners();
	
	$('#save-jobs').click(function() {
		var subreddits = $('#scrape-jobs').children().text().split('\n');
		updateScrapeConfig(['abcd', 'efg']);
		//updateScrapeConfig(subreddits);
	});
});