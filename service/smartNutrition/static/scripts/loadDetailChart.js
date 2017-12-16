function loadDetailFrame() {
    var CSS_COLOR_NAMES = ["AliceBlue","AntiqueWhite","Aqua","Aquamarine","Azure","Beige","Bisque","Black","BlanchedAlmond","Blue","BlueViolet","Brown","BurlyWood","CadetBlue","Chartreuse","Chocolate","Coral","CornflowerBlue","Cornsilk","Crimson","Cyan","DarkBlue","DarkCyan","DarkGoldenRod","DarkGray","DarkGrey","DarkGreen","DarkKhaki","DarkMagenta","DarkOliveGreen","Darkorange","DarkOrchid","DarkRed","DarkSalmon","DarkSeaGreen","DarkSlateBlue","DarkSlateGray","DarkSlateGrey","DarkTurquoise","DarkViolet","DeepPink","DeepSkyBlue","DimGray","DimGrey","DodgerBlue","FireBrick","FloralWhite","ForestGreen","Fuchsia","Gainsboro","GhostWhite","Gold","GoldenRod","Gray","Grey","Green","GreenYellow","HoneyDew","HotPink","IndianRed","Indigo","Ivory","Khaki","Lavender","LavenderBlush","LawnGreen","LemonChiffon","LightBlue","LightCoral","LightCyan","LightGoldenRodYellow","LightGray","LightGrey","LightGreen","LightPink","LightSalmon","LightSeaGreen","LightSkyBlue","LightSlateGray","LightSlateGrey","LightSteelBlue","LightYellow","Lime","LimeGreen","Linen","Magenta","Maroon","MediumAquaMarine","MediumBlue","MediumOrchid","MediumPurple","MediumSeaGreen","MediumSlateBlue","MediumSpringGreen","MediumTurquoise","MediumVioletRed","MidnightBlue","MintCream","MistyRose","Moccasin","NavajoWhite","Navy","OldLace","Olive","OliveDrab","Orange","OrangeRed","Orchid","PaleGoldenRod","PaleGreen","PaleTurquoise","PaleVioletRed","PapayaWhip","PeachPuff","Peru","Pink","Plum","PowderBlue","Purple","Red","RosyBrown","RoyalBlue","SaddleBrown","Salmon","SandyBrown","SeaGreen","SeaShell","Sienna","Silver","SkyBlue","SlateBlue","SlateGray","SlateGrey","Snow","SpringGreen","SteelBlue","Tan","Teal","Thistle","Tomato","Turquoise","Violet","Wheat","White","WhiteSmoke","Yellow","YellowGreen"];
    var summaryData = {}

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

            summaryData = data;
            loadDetailChart();
            loadRecommendedProductsFrame(globalBadNutrients);
        };

        xhr.send();
    }
    attr_map = {'carb':'Carbs', 'fat':'Fat', 'protein':'Protein', 'cholesterol':'Cholesterol', 'iron':'Iron', 'copper':'Copper', 'calcium':'Calcium', 'fiber':'Fiber', 'manganese':'Manganese', 'niacin':'Niacin', 'riboflavin':'Riboflavin', 'sat_fat':'Saturated Fat', 'sodium':'Sodium', 'vit_a':'Vitamin A', 'vit_b12':'Vitamin B-12', 'vit_b6':'Vitamin B-6', 'vit_c':'Vitamin C', 'vit_d':'Vitamin D', 'vit_e':'Vitamin E', 'vit_k':'Vitamin K', 'zinc':'Zinc'}

    function getNutrientData() {
        var result = [];

        var attributes = Object.keys(summaryData.totals);

        for (var i = 0; i < attributes.length; i++) {
            if (attributes[i] in attr_map) {
                result.push(summaryData.totals[attributes[i]] / summaryData.totals["calories"]);
            }
        }

        return result;
    }

    function getGoalData() {
      var result = [];

      var attributes = Object.keys(summaryData.totals);

      for (var i = 0; i < attributes.length; i++) {
          if (attributes[i] in attr_map) {
              if (summaryData.goals[attributes[i]] !== undefined) {
                result.push({'value':summaryData.goals[attributes[i]].value/ 2000, 'type':summaryData.goals[attributes[i]].type}); // FIXME
              } else {
                result.push(0);
              }
          }
      }

      return result;
    }

    function getLabels() {
        // Find everything that ends with "gs"
        var result = [];

        var attributes = Object.keys(summaryData.totals);

        for (var i = 0; i < attributes.length; i++) {
            if (attributes[i] in attr_map) {
                result.push(attr_map[attributes[i]]);
            }
        }
        return result;
    }

    function getLabelKeys() {
        // Find everything that ends with "gs"
        var result = [];

        var attributes = Object.keys(summaryData.totals);

        for (var i = 0; i < attributes.length; i++) {
            if (attributes[i] in attr_map) {
                result.push(attributes[i]);
            }
        }
        return result;
    }

    function makeBarColor(goal, actual, type) {
      var quality;
      var eps = 0.001
      if (type == 'below') {
        quality = Math.min(1,Math.pow((goal+eps)/(actual+eps),4))
      } else if (type == 'above') {
        quality = Math.min(1,Math.pow((actual+eps)/(goal+eps),4))
      } else {
        quality = Math.min(1,Math.pow((actual+eps)/(goal+eps),2)) + Math.min(1,Math.pow((goal+eps)/(actual+eps),2)) - 1
      }

      // HSL gradient looks WAAAY better, goes red yellow green instead of red brown green
      return ['hsl(' + Math.floor(118*quality) + ',' + Math.floor(100-50*quality) + '%, 50%)', quality]
      //return 'rgb(' + Math.floor(255-255*quality) + ',' + Math.floor(128*quality) + ', 10)'
    }

    // Combines user data with goals into one dataset for stacked bar charts.
    function mergeDataSet() {
      var userData = getNutrientData();
      var goalData = getGoalData();
      var labels = getLabels();
      var keys = getLabelKeys();

      var data = [];
      var colors = [];

      var userDataObj = {
        label: 'Actual',
        backgroundColor: 'red',
        borderColor: 'rgba(0, 128, 0, 1)'
      };



      if (goalData.length == userData.length) {
        for (var i = 0; i < userData.length; i++) {
          if (goalData[i].value > 0) {
            var goalAndQuality = makeBarColor(goalData[i].value, userData[i], goalData[i].type)
            colors.push(goalAndQuality[0])
            userData[i] = userData[i] / goalData[i].value;

            if (typeof globalBadNutrients === "undefined") {
              globalBadNutrients = []
            }

            if (goalAndQuality[1] < .3) {
                globalBadNutrients.push(keys[i])
            }
          }
        }
      }
      console.log(colors);

      userDataObj.data = userData;
      userDataObj.backgroundColor = colors;

      data.push(userDataObj);
      //data.push(goalDataObj);

      return data;
    }

    // Main
    getData();

    function loadDetailChart() {
        var ctx = document.getElementById("detailChart").getContext('2d');

        var data = {
            datasets: mergeDataSet(),

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: getLabels()
        }

        var foodGroupChart = new Chart(ctx,{
            type: 'horizontalBar',
            data: data,
            options: {
              onClick: function(e, active) {
                if(active.length == 0) return;
                var toselect = data.labels[active[0]._index];
                $('#nutChartDropdown').dropdown('set selected', toselect);
                $('#nutPerCalChartDropdown').dropdown('set selected', toselect);
              },
              tooltips: {
                enabled:false
              },
              legend: {
                display:false,
                labels: {
                  fillstyle: 'rgb(255, 0, 0)'
                }
              },
              scales: {
                xAxes: [{
                  id: "x-axis-0",
                  stacked: true,
                  gridLines: {
                       lineWidth: [1, 3, 3, 0],
                       color: ['transparent', 'light grey', 'light grey', 'transparent']
                  },
                  ticks: {
                       min: 0,
                       max: 2.2,
                       stepSize: 1,
                       callback: function(value) {
                           return Math.floor(value) == value?(100 * value) + "%":""
                       }
                   }
                }],
                yAxes: [{
                  stacked: true,
                  gridLines: {
                    display: false
                  }
                }]
              }
            }
        });
    }
}
loadDetailFrame();
