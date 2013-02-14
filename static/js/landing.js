$(function() {
	$('#client').click(function() {
		$('#upper').animate({
			height: '+=85px'
		}, function() {
			$('#clients').fadeIn();
		});
	});
});