$(function() {
	$('#client').bind('click', show_clients);
	$('#upper-content').animate({ opacity: 1 }, {queue: false, duration: 800});
	$('#upper-content').animate({ top: 0 }, 600, function() {
		$('#github-links').animate({ opacity: 1 }, function() {
			$('#byline').animate({ opacity: 1 });
		});
	});
});

function show_clients() {
	$('#upper').animate({
		height: '+=65px'
	}, function() {
		$('#clients').fadeIn();
	});
	$('#client').unbind('click', show_clients);
}