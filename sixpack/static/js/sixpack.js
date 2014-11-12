$(function () {
  var viewport_height = window.innerHeight;

  var spinner_config = {
    lines: 13, // The number of lines to draw
    length: 8, // The length of each line
    width: 15, // The line thickness
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
  $('.base-domain').html(document.location.origin);

  // Draw charts on Details page.
  if ($('#details-page').length) {
    var el = $('ul.experiments li');
    new Spinner(spinner_config).spin(el.get(0));
    var experiment = new Experiment($('ul.experiments li'), experiment_name, function () {
      el.find('.spinner').fadeOut('fast').remove();
      el.animate({
        opacity: 1
      });

      // Copy to Clipboard buttons
      // ZeroClipboard works by placing a transparent Flash
      // embed over the element, which means that default hover
      // and active states don't work, so we need to manually
      // activate them. It uses its own .on() methods for events,
      // so no clean jQuery syntax, unfortunately.
      var copyBtn = new ZeroClipboard($('.copy-querystring'), { moviePath: '/static/flash/ZeroClipboard.swf' });

      copyBtn.on('mousedown', function () {
        $(this).addClass('active');
      });
      copyBtn.on('mouseup', function () {
        $(this).removeClass('active');
      });
      copyBtn.on('mouseover', function () {
        $(this).closest('tr').addClass('highlight');
        $(this).tooltip('show');
      });
      copyBtn.on('mouseout', function () {
        $(this).removeClass('active');
        $(this).tooltip('hide');
      });
      copyBtn.on('complete', function (client, args) {
        $('.copy-success').fadeIn().find('code').html(args.text);

        // Take focus away from the flash doc
        document.body.tabIndex = 0;
        document.body.focus();
      });

      $('.copy-querystring').tooltip({ trigger: 'manual', placement: 'left' });

      $('#choose-kpi').on('change', function(e) {
        var this_kpi = $(this).val();
        if (this_kpi <= 0) {
          e.preventDefault();
          return;
        }
        url = '/experiments/' + experiment_name;
        if (this_kpi != 'default') {
          url += '?kpi=' + this_kpi;
        }
        window.location.href = url;
      });

    });

    // Focus the edit description textarea when opening the modal
    $('#desc-modal').on('shown', function() {
      $('#edit-description-textarea').focus();
    });
  }

  // Draw charts on Dashboard page.
  if ($('#dashboard-page').length) {

    if (experiments.length) {
      var el = null;
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

      var experiment = new Experiment(el, experiment_name, function () {
        el.find('.spinner').fadeOut('fast').remove();
        el.animate({
          opacity: 1
        });
      });

      // Listen to failed experiment response and handle it
      el.on('fail', function(e, resp) {
        if(experiment_name === 'undefined') {
          $(this).html('<p> Experiment name is invalid. </p>');
        } else {
          $(this).remove();
          $('.failing-experiments table').append('<tr><td><span>' + experiment_name + '</span></td>' + '<td><span>' + resp.statusText + '</span></td>' + '<td><span>' + "Erroring" + '</span></td></tr>');
        }
      });

      el.css('visibility', 'visible');
    }, {
      offset: viewport_height + (viewport_height * 0.5)
    });
  }
});

function getParameterByName (name) {
  // return name;
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
  var regexS = "[\\?&]" + name + "=([^&#]*)";
  var regex = new RegExp(regexS);
  var results = regex.exec(window.location.search);

  if (results === null) {
    return '';
  } else {
    return decodeURIComponent(results[1].replace(/\+/g, ' '));
  }
}
