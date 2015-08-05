$(function() {
  $('#see-more-web').bind('click', show_web_ui);
	$('#upper-content').animate({ opacity: 1 }, {queue: false, duration: 800});
	$('#upper-content').animate({ top: 0 }, 700, 'easeOutQuad', function() {
		$('#github-links').animate({ opacity: 1 }, function() {
			$('#byline').animate({ opacity: 1 });
			$('#blog-post').animate({ opacity: 1 });
		});
	});
  $('.tooltip-marker').tooltip();

  // Only initialize skrollr (parallax) on non-phone browsers.
  // I'm using a media query to hide a gist for phones only, so
  // this takes advantage of thiat.
  if($('.section .gist').css('display') !== 'none') {
    var s = skrollr.init();
  }
});

function show_web_ui(e) {
  e.preventDefault();
  $('#feature-depth').show();
  $('#feature-depth').animate({
    minHeight: '+=1143px'
  }, function() {
    $('#sixpack-web-large, #feature-depth h4').animate({ opacity: 1 }, 860, function() {
        $('#see-more-web').fadeOut();
      }
    );
  });
  $('#see-more-web').unbind('click', show_web_ui);
}
