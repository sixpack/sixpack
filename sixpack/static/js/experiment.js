var Experiment;
$(function () {

  Experiment = function (name, callback) {
    var that = {}, my = {};

    _.templateSettings.variable = 'experiment';

    my.el = null;
    my.container = $('ul.experiments');
    my.name = name;
    my.callback = callback;

    my.template = _.template($('#experiment-template').html());

    my.getData = function (callback) {
      var url = '/experiment/' + my.name + '.json?period=day';
      $.getJSON(url, function (data) {
        callback(data);
      });
    };

    my.getData(function (data) {
      my.container.append(my.template(data));
      var chart = new Chart(my.name, data);
      chart.draw();
    });

    return that;
  };
});