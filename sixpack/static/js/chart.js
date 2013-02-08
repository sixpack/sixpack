$(function() {
  var arrData = [
      ["2012-10-02",0.05],
      ["2012-10-03",0.056],
      ["2012-10-04",0.057],
      ["2012-10-06",0.06],
      ["2012-10-07",0.0582],
      ["2012-10-08",0.0584],
      ["2012-10-09",0.0586]];

  var margin = {top: 20, right: 20, bottom: 30, left: 50},
      width = 300
      height = 140

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

  var xAxis = d3.svg.axis()
      .scale(x)
      .ticks(4)
      .tickSize(0)
      .orient("bottom");

  var yAxis = d3.svg.axis()
      .scale(y)
      .ticks(2)
      .tickValues([0.055, 0.06])
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

  var svg = d3.select(".graph").append("svg")
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

  console.log(data);

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
});