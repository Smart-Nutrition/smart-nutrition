function nutChartDropdownTrigger() {
  loadNutFrame(document.getElementById("nutChartDropdown").value);
}

var attr_map = {'carb':'Carbs', 'fat':'Fat', 'protein':'Protein', 'cholesterol':'Cholesterol', 'iron':'Iron', 'copper':'Copper', 'calcium':'Calcium', 'fiber':'Fiber', 'manganese':'Manganese', 'niacin':'Niacin', 'riboflavin':'Riboflavin', 'sat_fat':'Saturated Fat', 'sodium':'Sodium', 'vit_a':'Vitamin A', 'vit_b12':'Vitamin B-12', 'vit_b6':'Vitamin B-6', 'vit_c':'Vitamin C', 'vit_d':'Vitamin D', 'vit_e':'Vitamin E', 'vit_k':'Vitamin K', 'zinc':'Zinc'}

function loadNutFrameDropdown() {
  function getData() {
      var xhr = new XMLHttpRequest();

      xhr.open('GET', "/api/summary");
      xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      xhr.onload = function() {
          if (xhr.status !== 200 && xhr.status !== 201) {
              alert('Request failed.  Returned status of ' + xhr.status);
          }

          var data = JSON.parse(xhr.responseText);

          var dropdownEle = document.getElementById("nutChartDropdown");
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

nut_chart_holder = (() => {
    var last = null;
    return chart => {
        if(last != null) last.destroy();
        last = chart;
    };
})();

function loadNutFrame(nutParam) {
    var nutData = {};

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

            nutData = data;
            loadNutChart();
        };

        xhr.send();
    }

    function getCalData(nutParam) {
        var data = [];
        for (var i = 0; i < nutData["trips"].length; i++) {
            item = {};
            item["x"] = new Date(nutData["trips"][i].time);
            item["y"] = nutData["trips"][i]["totals"][nutParam];

            data.push(item);
        }

        return data;
    }

    // Main

    getData();

    function loadNutChart() {
        var data = getCalData(nutParam);
        var ctx = document.getElementById("nutChart").getContext('2d');
        var nutChart = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: attr_map[nutParam] + ' / date',
                    data: data,
                    backgroundColor: 'rgba(153, 102, 255, 0.5)',
                    borderColor: 'rgba(153, 102, 255, 0.7)'
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
                    }]
                },
                tooltips: {
                    enabled:false
                }
            }
        });
        nut_chart_holder(nutChart);
    }
}
loadNutFrameDropdown();
loadNutFrame();
