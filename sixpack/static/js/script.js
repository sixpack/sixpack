$(function () { 
    $('#base-domain').html(document.location.origin);

    var id, alternative_name, experiment_name, conversions, participants;
    if ($('#graphs').length) {
    	$('#graphs .graph').each(function (key, val) {
    		id = $(this).attr('id');
    		alternative_name = id.substring(6, id.length);
    		drawChart(
    			'#' + id,
    			graph_data[alternative_name]['participants_by_day'],
    			graph_data[alternative_name]['conversions_by_day']
    		);
    	});
    }

	$('#dashboard-page ul.experiments .graph').each(function (key, val) {
		var alte;
		id = $(this).attr('id');
		experiment_name = id.substring(6, id.length);
		_.each(graph_data[experiment_name], function (alt) {
			alte = alt;
		});
		drawChart(
			'#' + id,
			alte['participants_by_day'],
			alte['conversions_by_day']
		);
	});
});