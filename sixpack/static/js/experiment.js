var Experiment;
$(function () {

  Experiment = function (el, name, include_archived, callback) {
    var that = {}, my = {};

    _.templateSettings.variable = 'experiment';

    my.el = el;
    my.name = name;
    my.include_archived = include_archived;
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
      // Remove archived experiments
      if (!my.include_archived && data.is_archived) {
          my.el.remove();
          return;
      }
      // Format some of the data before printing
      _.each(data.alternatives, function (alt, k) {
        data.alternatives[k].participant_count = my.addCommas(data.alternatives[k].participant_count);
        data.alternatives[k].conversion_rate = data.alternatives[k].conversion_rate.toFixed(2) + '%';
      });
      my.el.append(my.template(data));

      $('table tr').hover(
        function () {
          var alt_name = $(this).attr('class');
          if (!alt_name) return;

          $(this).addClass('highlight');

          var line = d3.select("#" + alt_name);
          line.attr('class', line.attr('class') + " line-hover")
        },
        function () {
          $(this).removeClass('highlight');
          d3.select('#' + $(this).attr('class')).attr('class', 'line');
        }
      );

      var chart = new Chart(my.name, data);
      chart.draw();
      my.callback();
    });

    return that;
  };
});
