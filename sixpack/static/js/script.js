$(function () {
  var id, graph, alternative_name, experiment_name, 
      conversions, participants, lines, line_colors, counter;
    
  // Display correct URL on "no-experiments" page.  
  $('#base-domain').html(document.location.origin);

  // Draw charts on Details page.
  if ($('#details-page').length) { 
    var colors = $('#details-page').find('span.circle').get();
    var chart = new Chart($('.chart').data('experiment'), function () {
      console.log(chart)
      $('.chart').each(function (index, val) {
        id = $(this).attr('id');
        alternative_name = id.substring(6, id.length);
        color = $(colors[index]).css('stroke');

        chart.drawAlternative(alternative_name, color);
      });
    });
  }

  // Draw charts on Dashboard page.
  $('#dashboard-page ul.experiments .chart').each(function (index, val) {
    var colors = []; 
    var circles = $(this).parent().find('span.circle').get();
    _.each(circles, function (val, index) {
      colors.push($(circles[index]).css('stroke'));
    });
    var experiment_name = $(this).data('experiment');
    var chart = new Chart(experiment_name, function () {
      chart.drawExperiment(experiment_name, colors);
    });
  });
});