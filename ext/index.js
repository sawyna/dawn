$(document).ready(function() {

	function doPoll(url, callback) {
		$.ajax({
			url: url,
			type: 'GET',
			dataType: 'json'
		})
		.done(function(data) {
			callback(data);
			// if(data.status) {
			// 	$("#info").html(data.status.percent + " percent completed." + data.status.eta + " remaining");
			// }
		})
		.fail(function(e) {
			console.log(e);
		})
	}

	$("#downloadButton").click(function(event) {
		chrome.tabs.query( {
			"active": true,
			"currentWindow": true
		}, 
		function(tabs) {
			console.log(tabs[0].url);
			$.ajax({
				url: 'http://localhost:8000/download?url=' + encodeURIComponent(tabs[0].url),
				type: 'GET',
				dataType: 'json',
				contentType: 'application/json'
			})
			.done(function() {
				console.log("success");
			})
			.fail(function() {
				console.log("error");
			});
			
		});
	});

	chrome.tabs.query ({
			"active": true,
			"currentWindow": true
		},
		function(tabs) {
			var url = tabs[0].url;
			var regexp = /^https:\/\/www.youtube.com\/watch\?(.*)$/g;
			var match = regexp.exec(url);
			url = 'http://localhost:8000/status?id=' + encodeURIComponent(match[1]);
			console.log(url);
			setInterval(function(){
				doPoll(url, function(data) {
					if(data.payload) {
						$("#info").html(data.payload.percent + " percent completed." + data.payload.eta + " remaining");
					}
				});
			}, 2000);
		}
	);

});