$(function () {
  // Display correct URL on "no-experiments" page.  
  $('#base-domain').html(document.location.origin);

  // Draw charts on Details page.
  if ($('#details-page').length) { 
    var path = document.location.pathname;
    var experiment_name = path.slice(12, path.length - 1);

    var experiment = new Experiment(experiment_name);
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
        el.fadeIn();
      });
    }, {
      offset: 'bottom-in-view'
    });
  }
});