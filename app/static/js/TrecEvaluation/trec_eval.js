/**
 * Created by Tirthraj on 7/20/2016.
 */

$(document).ready(function() {
    $("#draw_graph").click(function(){
        draw_chart();
    });
});

function draw_chart() {

    for(var key in precision) {

        var graphData = [];
        var results_length = precision[key].length;

        var global_minimum = 2;
        var prev_precision = 0;

        for (var i = 0; i < results_length; i++) {
            var recall_value = Math.round(recall[key][i] * 100) / 100;
            var precision_value = Math.round(precision[key][i] * 100) / 100;

            if(precision_value > global_minimum) {
                precision_value = prev_precision;
            }
            else {
                global_minimum = precision_value;
            }

            prev_precision = precision_value;

            var data = {
                "recall": recall_value,
                "precision": precision_value
            };
            graphData.push(data);
        }

        var chart = new AmCharts.AmXYChart();
        chart.titles = [{"text": "Precision - Recall Curve"}];
        chart.dataProvider = graphData;

        var xAxis = new AmCharts.ValueAxis();
        xAxis.title = "Recall";
        xAxis.position = "bottom";
        chart.addValueAxis(xAxis);

        var yAxis = new AmCharts.ValueAxis();
        yAxis.title = "Precision";
        yAxis.position = "left";
        chart.addValueAxis(yAxis);

        var graph = new AmCharts.AmGraph();
        graph.xField = "recall";
        graph.yField = "precision";
        graph.lineAlpha = 1;
        graph.type = "solid";
        //graph.bullet = "round";
        graph.lineColor = "#428bca";

        chart.addGraph(graph);

        var chartCursor = new AmCharts.ChartCursor();
        chart.addChartCursor(chartCursor);

        chart.write('chart_div_'+key);

        // chart_div.text(graphData);
    }
}