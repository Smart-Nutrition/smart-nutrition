function loadFoodGroupFrame() {
    var nutSourcesData = {}

    function getData() {
        var xhr = new XMLHttpRequest();

        xhr.open('GET', "/api/foodgroups");
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function() {
            if (xhr.status !== 200 && xhr.status !== 201) {
                alert('Request failed.  Returned status of ' + xhr.status);
            }
            
            var data = JSON.parse(xhr.responseText);
            
            console.log(data);
            
            nutSourcesData = data;
            loadFoodGroupChart();
        };
        
        xhr.send();
    }

    function getCalSourceData() {
        var data = [];
        
        grains = nutSourcesData["totals"]["grain_s"];
        dairy = nutSourcesData["totals"]["dairy_s"];
        protein = nutSourcesData["totals"]["protein_s"];
        fruits = nutSourcesData["totals"]["fruit_s"];
        vegetables = nutSourcesData["totals"]["vegetable_s"];
        
        data.push(grains);
        data.push(dairy);
        data.push(protein);
        data.push(fruits);
        data.push(vegetables);
        
        return data;
    }

    // Main
    getData();
    
    function loadFoodGroupChart() {
        var ctx = document.getElementById("foodGroupChart").getContext('2d');

        var data = {
            datasets: [{
                data: getCalSourceData(),
                backgroundColor: ['rgba(255, 99, 132, 0.5)',
                'rgba(54, 162, 235, 0.5)',
                'rgba(255, 206, 86, 0.5)',
                'rgba(75, 192, 192, 0.5)',
                'rgba(153, 102, 255, 0.5)'],
                borderColor: ['rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)']
            }],

            // These labels appear in the legend and in the tooltips when hovering different arcs
            labels: [
                'Grains',
                'Dairy',
                'Protein',
                'Fruits',
                'Vegetables'
            ]
        }

        var foodGroupChart = new Chart(ctx,{
            type: 'doughnut',
            data: data,
            options:{
                tooltips:{
                    enabled:false
                }
            }
        });
    }
}
loadFoodGroupFrame();
