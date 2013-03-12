$(function () {
  var viewport_height = window.innerHeight;

  var include_archived = getParameterByName('include_archived') === 'True' ? true : false;

  var spinner_config = {
    lines: 13, // The number of lines to draw
    length: 8, // The length of each line
    width: 20, // The line thickness
    radius: 40, // The radius of the inner circle
    corners: 1, // Corner roundness (0..1)
    rotate: 0, // The rotation offset
    color: '#fff', // #rgb or #rrggbb
    speed: 1.1, // Rounds per second
    trail: 34, // Afterglow percentage
    shadow: false, // Whether to render a shadow
    hwaccel: false, // Whether to use hardware acceleration
    className: 'spinner', // The CSS class to assign to the spinner
    zIndex: 2e9, // The z-index (defaults to 2000000000)
    top: 'auto', // Top position relative to parent in px
    left: 'auto' // Left position relative to parent in px
  };

  // Display correct URL on "no-experiments" page.  
  $('#base-domain').html(document.location.origin);

  // Draw charts on Details page.
  if ($('#details-page').length) {
    var el = $('ul.experiments li');
    new Spinner(spinner_config).spin(el.get(0));
    var experiment = new Experiment($('ul.experiments li'), experiment_name, true, function () {
      el.find('.spinner').fadeOut('fast').remove();
      el.animate({
        opacity: 1
      });
    });
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
      var el = null;
      $('#archive-notice').fadeIn('fast');
      _.each(experiments, function (experiment_name) {
        el = $('<li class="experiment" data-name="' + experiment_name + '" style="visibility: hidden;"></li>');
        $('ul.experiments').append(el);
        new Spinner(spinner_config).spin(el.get(0));
      });
    } else {
      $('#no-data').fadeIn('fast');
    }

    $('ul.experiments li').each(function () {
      var el = $(this);
      var experiment_name = el.data('name');

      // Prevent loading more than once:
      if (el.data('loaded')) return;
      el.data('loaded', true);

      var experiment = new Experiment(el, experiment_name, include_archived, function () {
        el.find('.spinner').fadeOut('fast').remove();
        el.animate({
          opacity: 1
        });
      });
      el.css('visibility', 'visible');
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