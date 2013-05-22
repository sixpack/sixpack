var Experiment;
$(function () {

  Experiment = function (el, name, archived_only, callback) {
    var that = {}, my = {};

    _.templateSettings.variable = 'experiment';

    my.el = el;
    my.name = name;
    my.archived_only = archived_only;
    my.callback = callback;

    my.template = _.template($('#experiment-template').html());

    my.getData = function (callback) {
      var url = '/experiment/' + my.name + '.json?period=day';
      $.getJSON(url, function (data) {
        callback(data);
      });
    };

    // Add commas to a number
    my.addCommas = function (n) {
      while (/(\d+)(\d{3})/.test(n.toString())) {
        n = n.toString().replace(/(\d+)(\d{3})/, '$1'+','+'$2');
      }
      return n;
    };

    my.getData(function (data) {

      if ($('#dashboard-page').length) {
        if (my.archived_only && !data.is_archived) {
          my.el.remove();
          return;
        } else if (!my.archived_only && data.is_archived) {
          my.el.remove();
          return;
        }
      }

      // Format some of the data before printing
      _.each(data.alternatives, function (alt, k) {
        data.alternatives[k].participant_count = my.addCommas(data.alternatives[k].participant_count);
        data.alternatives[k].conversion_rate = data.alternatives[k].conversion_rate.toFixed(2) + '%';
      });
      my.el.append(my.template(data));

      $("li[data-name='" + my.name + "'] tr").hover(
        function () {
          var alt_name = $(this).attr('class');
          if (!alt_name) return;

          $(this).addClass('highlight');

          var line = d3.select("#" + alt_name);
          var id = line.attr('id');
          var el = d3.select('#' + id)[0][0];

          if (line.attr('class') === 'circle') {
            line.attr('r', 7);
          } else {
            line.attr('class', line.attr('class') + " line-hover");
          }

          // Sort the lines so the current line is "above" the non-hovered lines
          el.parentNode.appendChild(el);
        },
        function () {
          $(this).removeClass('highlight');

          var alt_name = $(this).attr('class');
          if (!alt_name) return;

          var line = d3.select('#' + alt_name);

          if (line.attr('class') === 'circle') {
            line.attr('r', 5);
          } else {
            line.attr('class', 'line');
          }
        }
      );

      var chart = new Chart(my.name, data);
      chart.draw();
      my.callback();
    });

    return that;
  };
});
