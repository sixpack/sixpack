var Experiment;
$(function () {

  Experiment = function (name, callback) {
    var that = {}, my = {};

    _.templateSettings.variable = 'rc';

    my.el = null;
    my.container = $('ul.experiments');
    my.name = name;
    my.callback = callback;

    my.template = _.template($('#experiment-template').html());

    my.colors = [
      '#714A33',
      '#32587E',
      '#327E51',
      '#3A85AC',
      '#8EBDBC',
      '#56BDBB',
      '#BDAB4D',
      '#33716F',
      '#7E466F',
      '#A4433A',
      '#B8C6D7',
      '#5D300B',
      '#D09104',
      '#E99E62'
    ];

    my.getData = function (callback) {
      var url = '/experiment/' + my.name + '.json?period=day';
      $.getJSON(url, function (data) {
        callback(data);
      });
    };

    my.getData(function (data) {
      console.log(data)
      console.log(my.template(data));
      my.container.append(my.template(data));

      //var chart = new Chart(data);
      //chart.draw();
    });

    return that;
  };
});