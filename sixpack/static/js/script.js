$(function () {
  var id, graph, alternative_name, experiment_name, 
      conversions, participants, lines, line_colors, counter;
    
  // Display correct URL on "no-experiments" page.  
  $('#base-domain').html(document.location.origin);

  // Draw graphs on Details page.
  if ($('#details-page').length) { 
    line_colors = $('#details-page').find('span.circle').get();
    $('#details-page .graph').each(function (index, val) {
      id = $(this).attr('id');
      alternative_name = id.substring(6, id.length);
      graph = GraphMaker('#' + id);
      graph.draw([{
        participants: graph_data[alternative_name]['participants_by_day'],
        conversions: graph_data[alternative_name]['conversions_by_day'],
        color: $(line_colors[index]).css('stroke')
      }]);
    });
  }

  // Draw graphs on Dashboard page.
  $('#dashboard-page ul.experiments .graph').each(function (index, val) {
    id = $(this).attr('id');
    experiment_name = id.substring(6, id.length);
    lines = []
    line_colors = $(this).parent().find('span.circle').get();
    counter = 0
    _.each(graph_data[experiment_name], function (alt) {
      lines.push({
        participants: alt['participants_by_day'],
        conversions: alt['conversions_by_day'],
        color: $(line_colors[counter]).css('stroke')
      });
      counter++;
    });
    GraphMaker('#' + id).draw(lines);
  });
});