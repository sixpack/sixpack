var drawChart;
$(function() {

  drawChart = function (element, participants, conversions) {

    var $element = $(element);
    var arrData = _.map(participants, function (participant, key) {
        conversion = _.find(conversions, function (conversion) {return conversion[0] === participant[0]});
        return [participant[0], Number(conversion[1]/participant[1]).toFixed(2)];
    });

    if (arrData.length <= 2) {
        $element.append("<p>Not enough data to graph</p>");
        return;
    }


    var margin = {top: 20, right: 20, bottom: 30, left: 50},
        width = $element.width()
        height = $element.height()

    function make_x_axis() {
        return d3.svg.axis()
            .scale(x)
            .orient("bottom")
            .ticks(5)
    }

    var parseDate = d3.time.format("%Y-%m-%d").parse;

    var x = d3.time.scale()
        .range([0, width])

    var y = d3.scale.linear()
        .range([height, 0]);

    var xValues =_.map(arrData, function(arr) {
        return _.first(arr);
    });
    var yValues =_.map(arrData, function(arr) {
        return _.last(arr);
    });

    var xAxis = d3.svg.axis()
        .scale(x)
        .ticks(4)
        .tickSize(0)
        .tickValues(xValues)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .ticks(yValues.length)
        .tickValues(yValues)
        .tickSize(0)
        .tickFormat(d3.format(".1%"))
        .orient("left");

    var area = d3.svg.area()
      .x(function(d) { return x(d.date); })
      .y0(height)
      .y1(function(d) { return y(d.close); });

    var line = d3.svg.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.close); });

    var svg = d3.select(element).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var data = arrData.map(function(d) {
        return {
           date: parseDate(d[0]),
           close: d[1]
        };
    });

    x.domain(d3.extent(data, function(d) { return d.date; }));
    y.domain(d3.extent(data, function(d) { return d.close; }));

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")

    svg.append("g")
            .attr("class", "grid")
            .attr("transform", "translate(0," + height + ")")
            .call(make_x_axis()
                .tickSize(-height, 0, 0)
                .tickFormat("")
            );

    svg.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line);

    svg.append("path")
          .datum(data)
          .attr("class", "area")
          .attr("d", area);
  }
});