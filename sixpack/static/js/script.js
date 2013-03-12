$(function () {
  var viewport_height = window.innerHeight;

  var include_archived = getParameterByName('include_archived') === 'True' ? true : false;

  // Display correct URL on "no-experiments" page.  
  $('#base-domain').html(document.location.origin);

  // Draw charts on Details page.
  if ($('#details-page').length) {
    var experiment = new Experiment($('ul.experiments'), experiment_name, true);
  }

  // Draw charts on Dashboard page.
  if ($('#dashboard-page').length) { 

    // Toggle archive toolbar
    if (include_archived) {
      $('.archive-is-not-active').fadeIn('fast');
    } else {
      $('.archive-is-active').fadeIn('fast');
    }

    if (experiments.length) {
      $('#archive-notice').fadeIn('fast');
      _.each(experiments, function (experiment_name) {
        $('ul.experiments').append('<li data-name="' + experiment_name + '" style="visibility: hidden;"></li>')
      });
    } else {
      $('#no-data').fadeIn('fast');
    }

    $('li').waypoint(function (direction) {
      var el = $(this);
      var experiment_name = el.data('name');

      // Prevent loading more than once:
      if (el.data('loaded')) return;
      el.data('loaded', true);

      var experiment = new Experiment(el, experiment_name, include_archived);

      el.css('visibility', 'visible');
    }, {
      offset: viewport_height + (viewport_height * 0.5)
    });
  }
});

function getParameterByName (name) {
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
  var regexS = "[\\?&]" + name + "=([^&#]*)";
  var regex = new RegExp(regexS);
  var results = regex.exec(window.location.search);

  if (results == null) {
    return '';
  } else { 
    return decodeURIComponent(results[1].replace(/\+/g, ' '));
  }
}