var Experiment;
$(function () {

  Experiment = function (el, name, callback) {
    var that = {}, my = {};

    _.templateSettings.variable = 'experiment';

    my.el = el;
    my.name = name;
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
      // Add commas to the participant count
      _.each(data.alternatives, function (alt, k) {
        data.alternatives[k].participant_count = my.addCommas(data.alternatives[k].participant_count);
      });
      my.el.append(my.template(data));

      var chart = new Chart(my.name, data);
      chart.draw();
    });

    return that;
  };
});
