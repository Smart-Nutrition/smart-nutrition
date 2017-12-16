function loadRecommendedProductsFrame(nutrientList) {
    var xhr = new XMLHttpRequest();

    var nutrientStr = nutrientList.join(" ");

    xhr.open('GET', "/api/recommend?nutrient=" + nutrientStr);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status !== 200 && xhr.status !== 201) {
            alert('Request failed.  Returned status of ' + xhr.status);
        }

        var data = JSON.parse(xhr.responseText);

        var recView = document.getElementById("recommendedItemsView");

        for (var i = 0; i < data.food.length; i++) {
          console.log(data.food[i].name);
          recView.innerHTML += "<a class='item' href='https://www.kroger.com/search?query=" + data.food[i].name + "'>  \
                        <div class='ui tiny image'> \
                          <img src='https://semantic-ui.com/images/wireframe/image.png'> \
                        </div> \
                        <div class='content'> \
                          <div class='header'>" + data.food[i].name + "</div> \
                          <div class='description'> \
                            <p>This will help you meet your goal for " + data.food[i].recommended_for[0] + "</p> \
                          </div> \
                        </div> \
                      </a> "
        }
    };

    xhr.send();
}
