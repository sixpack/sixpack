$(function () {
  // Display correct URL on "no-experiments" page.  
  $('#base-domain').html(document.location.origin);

  // Draw charts on Details page.
  if ($('#details-page').length) { 
    var id, alternative_name, color;
    var colors = $('#details-page').find('span.circle').get();
    var chart = new Chart($('.chart').data('experiment'), function () {
      $('.chart').each(function (index, val) {
        id = $(this).attr('id');
        alternative_name = id.substring(6, id.length);
        color = $(colors[index]).css('stroke');

        chart.drawAlternative(alternative_name, color);
      });
    });
  }

  // Draw charts on Dashboard page.
  if ($('#dashboard-page').length) { 
    $('li').waypoint(function (direction) {
      var el = $(this).find('.chart');

      // Prevent loading more than once:
      if (el.data('loaded')) return;
      el.data('loaded', true);
      
      var colors = []; 
      var circles = el.parent().find('span.circle').get();
      _.each(circles, function (val, index) {
        colors.push($(circles[index]).css('stroke'));
      });
      var experiment_name = el.data('experiment');
      var chart = new Chart(experiment_name, function () {
        chart.drawExperiment(experiment_name, colors);
      });
    }, {
      offset: 'bottom-in-view'
    });
  }
});