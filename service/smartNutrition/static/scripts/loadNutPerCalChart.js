function nutPerCalChartDropdownTrigger() {
  loadNutPerCalFrame(document.getElementById("nutPerCalChartDropdown").value);
}

var attr_map = {'carb':'Carbs', 'fat':'Fat', 'protein':'Protein', 'cholesterol':'Cholesterol', 'iron':'Iron', 'copper':'Copper', 'calcium':'Calcium', 'fiber':'Fiber', 'manganese':'Manganese', 'niacin':'Niacin', 'riboflavin':'Riboflavin', 'sat_fat':'Saturated Fat', 'sodium':'Sodium', 'vit_a':'Vitamin A', 'vit_b12':'Vitamin B-12', 'vit_b6':'Vitamin B-6', 'vit_c':'Vitamin C', 'vit_d':'Vitamin D', 'vit_e':'Vitamin E', 'vit_k':'Vitamin K', 'zinc':'Zinc'}

function loadNutPerCalChartDropdown() {
  function getData() {
      var xhr = new XMLHttpRequest();

      xhr.open('GET', "/api/summary");
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.onload = function() {
          if (xhr.status !== 200 && xhr.status !== 201) {
              alert('Request failed.  Returned status of ' + xhr.status);
          }

          var data = JSON.parse(xhr.responseText);

          var dropdownEle = document.getElementById("nutPerCalChartDropdown");
          var htmlToAdd = "<option value=''>Nutrient</option>";

          var nutrients = Object.keys(data.totals);
          for (var i = 0; i < nutrients.length; i++) {
            if (nutrients[i] in attr_map) {
              textopt = attr_map[nutrients[i]]
              htmlToAdd += "<option value='" + nutrients[i] + "'>" + textopt + "</option>";
            }
          }

          dropdownEle.innerHTML = htmlToAdd;
      };

      xhr.send();
  }
  getData();
}

nut_per_cal_chart_holder = (() => {
    var last = null;
    return chart => {
        if(last != null) last.destroy();
        last = chart;
    };
})();

function loadNutPerCalFrame(nutParam) {
    var nutPerCalData = {};

    function getData() {
        var xhr = new XMLHttpRequest();

        xhr.open('GET', "/api/summary");
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function() {
            if (xhr.status !== 200 && xhr.status !== 201) {
                alert('Request failed.  Returned status of ' + xhr.status);
            }

            var data = JSON.parse(xhr.responseText);

            console.log(data);

            nutPerCalData = data;
            loadNutPerCalChart();
        };

        xhr.send();
    }

    function getNutPerCalData(nut) {
        var data = [];
        for (var i = 0; i < nutPerCalData["trips"].length; i++) {
            item = {};
            item["x"] = new Date(nutPerCalData["trips"][i].time);
            item["y"] = (nutPerCalData["trips"][i]["totals"][nut]) / (nutPerCalData["trips"][i]["totals"].calories);

            data.push(item);
        }

        return data;
    }

    function getGoalLine(nut) {
      var data = [];
      for (var i = 0; i < nutPerCalData["trips"].length; i++) {
          item = {};
          item["x"] = new Date(nutPerCalData["trips"][i].time);
          if (nutPerCalData["goals"][nut]) {
            item["y"] = (nutPerCalData["goals"][nut].value / 2000); // FIXME
            data.push(item);
          }
      }

      return data;
    }

    // Main

    getData();

    function loadNutPerCalChart() {
        var data = getNutPerCalData(nutParam);

        var ctx = document.getElementById("nutPerCalChart").getContext('2d');
        var nutPerCalChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: attr_map[nutParam] + ' / cal / date',
                    data: data,
                    backgroundColor: 'rgba(75, 192, 192, 0.5)',
                    borderColor: 'rgba(75, 192, 192, 0.7)'
                },
                {
                  label: "Goal",
                  data: getGoalLine(nutParam),
                  backgroundColor: 'rgba(0, 0, 0, 0.0)',
                  borderColor: 'black'
                }]
            },
            options: {
                scales: {
                    xAxes: [{
                        type: 'time',
                        time: {
                            unit: 'day',
                            displayFormats: {
                                quarter: 'II'
                            }
                        },
                        position: 'bottom'
                    }],
                    yAxes: [{
                      id: "y-axis-0",
                      ticks: {
                           min: 0,
                           callback: function(value) {
                               return "";//(100 * value).toFixed(2) + "%"
                           }
                       }
                    }]
                },
                tooltips: {
                    enabled:false
                }
            },
            annotation: {
              annotations: [
               {
                 type: "line",
                 mode: "horizontal",
                 scaleID: "y-axis-0",
                 value: .2,
                 borderColor: "red",
                 label: {
                   content: "TODAY",
                   enabled: true,
                   position: "top"
                 }
               }
             ]
           }
        });
        nut_per_cal_chart_holder(nutPerCalChart);
    }
}

loadNutPerCalChartDropdown();
loadNutPerCalFrame();
