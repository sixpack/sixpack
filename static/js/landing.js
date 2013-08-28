$(function() {
	$('#client').bind('click', show_clients);
  $('#see-more-web').bind('click', show_web_ui);
	$('#upper-content').animate({ opacity: 1 }, {queue: false, duration: 800});
	$('#upper-content').animate({ top: 0 }, 700, 'easeOutQuad', function() {
		$('#github-links').animate({ opacity: 1 }, function() {
			$('#byline').animate({ opacity: 1 });
			$('#blog-post').animate({ opacity: 1 });
		});
	});
	var s = skrollr.init();
  $('.tooltip-marker').tooltip();
});

function show_clients() {
	$('#upper').animate({
		paddingBottom: '+=65px'
	}, function() {
		$('#clients').fadeIn();
	});
	$('#client').unbind('click', show_clients);
}

function show_web_ui(e) {
  e.preventDefault();
  $('#feature-depth').show();
  $('#feature-depth').animate({
    minHeight: '+=1143px'
  }, function() {
    $('#sixpack-web-large, #feature-depth h4').animate({ opacity: 1 }, 600, function() {
        $('#see-more-web').fadeOut();
      }
    );
  });
  $('#see-more-web').unbind('click', show_web_ui);
}