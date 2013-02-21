var GraphMaker;
$(function () {

  GraphMaker = function (element) {
    var that = {}, my = {};

    my.$element = $(element);
    my.margin = {
      top: 20,
      right: 20,
      bottom: 30,
      left: 50
    };
    my.width = my.$element.width();
    my.height = my.$element.height();
    my.xScale = d3.time.scale().range([0, my.width]);
    my.yScale = d3.scale.linear().range([my.height, 0]);

    my.drawLabels = function (data) {
      var xValues, yValues, yMin, yMax;

      xValues = _.map(data, function (d) {
        return d[0];
      });
      yValues = _.map(data, function (d) {
        return parseFloat(d[1]);
      });
      yMin = _.min(yValues);
      yMax = _.max(yValues);
      yValues = [yMin, ((yMax - yMin) * 0.5) + yMin, yMax]

      my.xAxis = d3.svg.axis()
        .scale(my.xScale)
        .ticks(4)
        .tickSize(0)
        .tickValues(xValues)
        .orient("bottom");

      my.yAxis = d3.svg.axis()
        .scale(my.yScale)
        .ticks(yValues.length)
        .tickValues(yValues)
        .tickSize(0)
        .tickFormat(d3.format(".1%"))
        .orient("left");
    };

    my.drawLine = function (data, color) {
      color = color || "#9d5012";
      var line = d3.svg.line()
        .x(function (d) {
          return my.xScale(d.date);
        })
        .y(function (d) {
          return my.yScale(d.close);
        });

      my.svg.append("path")
        .datum(data)
        .attr("class", "line")
        .attr("d", line)
        .attr("style", "stroke:" + color)
    };

    my.drawArea = function (data) {
      var area = d3.svg.area()
        .x(function (d) {
          return my.xScale(d.date);
        })
        .y0(my.height)
          .y1(function (d) {
          return my.yScale(d.close);
        });

      my.svg.append("path")
        .datum(data)
        .attr("class", "area")
        .attr("d", area);
    };

    // Calculate conversion rates each time interval
    my.formatRateData = function (participants, conversions) {
      var rate = 0;
      return _.map(participants, function (participant, key) {
        conversion = _.find(conversions, function (conversion) {
          return conversion[0] === participant[0]
        });

        rate = Number(conversion[1] / participant[1]).toFixed(2);
        if (isNaN(rate)) rate = 0.00;
        return [participant[0], rate];
      });
    };

    // Compose a D3-friendly data structure
    my.formatGraphData = function (rates) {
      return rates.map(function (d) {
        return {
          date: d3.time.format("%Y-%m-%d").parse(d[0]),
          close: d[1]
        };
      });
    };

    my.drawBase = function () {
      my.svg = d3.select(element).append("svg")
        .attr("width", my.width + my.margin.left + my.margin.right)
        .attr("height", my.height + my.margin.top + my.margin.bottom)
        .append("g")
        .attr("transform", "translate(" + my.margin.left + "," + my.margin.top + ")");
    };

    my.drawBackground = function (data) {
      my.xScale.domain(d3.extent(data, function (d) {
        return d.date;
      }));

      my.yScale.domain(d3.extent(data, function (d) {
        return d.close;
      }));

      my.svg.append("g")
        .attr("class", "y axis")
        .call(my.yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end");
        
      my.svg.append("g")
        .attr("class", "grid")
        .attr("transform", "translate(0," + my.height + ")")
        .call(d3.svg.axis()
          .scale(my.xScale)
          .orient("bottom")
          .ticks(data.length)
        .tickSize(-my.height, 0, 0)
        .tickFormat(""));
    };

    my.dataExists = function (data) {
      if (data.participants.length <= 2) {
        my.$element.append("<p>Not enough data to graph</p>");
        return false;
      }
      return true;
    };

    /**
     * Takes an array of alt(s) and draws them to graph.
     * @param {Array} alt An array of objects
     *      @param {Array<Array<String>>} conversions
     *      @param {Array<Array<String>>} participants
     *      @param {String} color
     * @return 
     */
    that.draw = function (alts) {
      var data, rate_data, d3_data, aggregate_rates, data_intervals, min_rate, max_rate;

      if (alts.length === 1) {
        if (!my.dataExists(alts[0])) return;

        rate_data = my.formatRateData(alts[0].participants, alts[0].conversions);
        d3_data = my.formatGraphData(rate_data);

        my.drawBase();
        my.drawLabels(rate_data);
        my.drawBackground(d3_data);
        my.drawLine(d3_data, alts[0].color);
        my.drawArea(d3_data);
      } else {
        // TODO: better data check
        if (!my.dataExists(alts[0])) return;

        // Get the aggregate data intervals for drawing labels + background
        aggregate_rates = [];
        _.each(alts, function (alt, k) {
          _.each(my.formatRateData(alt.participants, alt.conversions), function (rate, k) {
            aggregate_rates.push(rate);
          });
        });

        data_intervals = _.uniq(_.map(aggregate_rates, function (d, k) {
          return d[0];
        }));

        min_rate = _.min(_.map(aggregate_rates, function(n) {
          return parseFloat(n[1]);
        }));
        max_rate = _.max(_.map(aggregate_rates, function(n) {
          return parseFloat(n[1]);
        }));
        
        rate_data = _.map(data_intervals, function (date, index) {
          return [date, min_rate];
        });
        rate_data[0][1] = max_rate;

        d3_data = my.formatGraphData(rate_data);

        my.drawBase();
        my.drawLabels(rate_data);
        my.drawBackground(d3_data);

        _.each(alts, function (alt, k) {
          rate_data = my.formatRateData(alt.participants, alt.conversions);
          d3_data = my.formatGraphData(rate_data);
          my.drawLine(d3_data, alt.color);
        });
      }
    };

    return that;
  };
});