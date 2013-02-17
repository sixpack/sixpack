$(function () { 
    $('#base-domain').html(document.location.origin);

    var id, alternative_name, experiment_name, conversions, participants;
    if ($('#graphs').length) {
    	$('#graphs .graph').each(function (key, val) {
    		id = $(this).attr('id');
    		alternative_name = id.substring(6, id.length);
    		var graph = GraphMaker('#' + id);
			graph.draw([{
				participants: graph_data[alternative_name]['participants_by_day'],
				conversions: graph_data[alternative_name]['conversions_by_day'],
				color: '#FFF'
			}]);
    	});
    }

	$('#dashboard-page ul.experiments .graph').each(function (key, val) {
		var alte, graph, lines;
		id = $(this).attr('id');
		experiment_name = id.substring(6, id.length);
		graph = GraphMaker('#' + id);
		lines = []
		_.each(graph_data[experiment_name], function (alt) {
			lines.push({
				participants: alt['participants_by_day'],
				conversions: alt['conversions_by_day'],
				color: '#FFF'
			});
		});

		graph.draw(lines);
	});
});