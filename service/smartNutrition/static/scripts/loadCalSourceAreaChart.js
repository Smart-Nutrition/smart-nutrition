function loadCalSourceFrame() {
    var nutSourcesData = {}

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

            nutSourcesData = data;
            loadCalSourceChart();
        };

        xhr.send();
    }

    function getCalSourceData() {
      fatDataset = {data: [], backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 0.7)', label: 'Fat'};
      proteinDataset = {data: [], backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 0.7)', label: 'Protein'};
      carbDataset = {data: [], backgroundColor: 'rgba(255, 206, 86, 0.5)',
                     borderColor: 'rgba(255, 206, 86, 0.7)', label: 'Carbs'};

      for (var i = 0; i < nutSourcesData["trips"].length; i++) {
        console.log(i);
          var fat = nutSourcesData["trips"][i]["totals"]["fat"];
          var protein = nutSourcesData["trips"][i]["totals"]["protein"];
          var carbs = nutSourcesData["trips"][i]["totals"]["carb"];

          var totalSum = fat + protein + carbs;

          itemFat = {};
          itemProtein = {};
          itemCarbs = {};

          itemFat["x"] = new Date(nutSourcesData["trips"][i].time);
          itemProtein["x"] = new Date(nutSourcesData["trips"][i].time);
          itemCarbs["x"] = new Date(nutSourcesData["trips"][i].time);

          itemFat["y"] = fat / totalSum;

          fatDataset.data.push(itemFat);

          itemProtein["y"] = protein / totalSum;
          proteinDataset.data.push(itemProtein);

          itemCarbs["y"] = carbs / totalSum;
          carbDataset.data.push(itemCarbs);
      }

      return [fatDataset, proteinDataset, carbDataset];
    }


    // Main

    getData();

    function loadCalSourceChart() {
        var ctx = document.getElementById("calSourceChart").getContext('2d');
        var calSourceData = {
            datasets: getCalSourceData(),
        }

        var calSourceChart = new Chart(ctx,{
            type: 'line',
            data: calSourceData,
            options: {
              scales: {
                yAxes: [{
                  stacked: true,
                }],
                xAxes: [{
                  type: "time",
                  time: {
                    unit: 'day',
                    displayFormats: {
                      quarter: 'II'
                    }
                  },
                  bounds: 'data',
                  ticks: {
                    source: "data"
                  }
                }]
              }
            }
        });
    }
}
loadCalSourceFrame();
