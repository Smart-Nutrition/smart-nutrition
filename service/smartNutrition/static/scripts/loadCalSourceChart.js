function loadCalSourceFrame() {
    var nutSourcesData = {}

    function getData() {
        var xhr = new XMLHttpRequest();

        xhr.open('GET', "/api/macronutrients");
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function() {
            if (xhr.status !== 200 && xhr.status !== 201) {
                alert('Request failed.  Returned status of ' + xhr.status);
            }

            var data = JSON.parse(xhr.responseText);

            console.log("macro: ");
            console.log(data);

            nutSourcesData = data;
            loadCalSourceChart();
        };

        xhr.send();
    }

    function getCalSourceData() {
        var data = [];

        fat = nutSourcesData["totals"]["fat_p"];
        protein = nutSourcesData["totals"]["protein_p"];
        carbs = nutSourcesData["totals"]["carb_p"];

        data.push(fat);
        data.push(protein);
        data.push(carbs);

        return data;
    }


    // Main

    getData();

    function loadCalSourceChart() {
        var ctx = document.getElementById("calSourceChart").getContext('2d');
        var calSourceData = {
            datasets: [{
                data: getCalSourceData(),
                backgroundColor: ['rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)'],
                borderColor: ['rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)']
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: [
                'Fat',
                'Protein',
                'Carbs'
            ]
        }

        var calSourceChart = new Chart(ctx,{
            type: 'doughnut',
            data: calSourceData,
            options: {
              tooltips: {
                enabled:false
                callbacks: {
                  label: function(tooltipItem, data) {
                  	var dataset = data.datasets[tooltipItem.datasetIndex];
                    var total = dataset.data.reduce(function(previousValue, currentValue, currentIndex, array) {
                      return previousValue + currentValue;
                    });
                    var currentValue = dataset.data[tooltipItem.index];
                    var precentage = Math.floor(((currentValue/total) * 100)+0.5);
                    return precentage + "%";
                  }
                }
              }
            }
        });
    }
}
loadCalSourceFrame();
