function createGoalNamespace() {
  function genFieldOptions() {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', "/api/summary");
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status !== 200 && xhr.status !== 201) {
            alert('Request failed.  Returned status of ' + xhr.status);
        }

        var data = JSON.parse(xhr.responseText);
        var fieldDiv = document.getElementById("goal-fields");

        var nutrients = Object.keys(data.totals);

        for (var i = 0; i < nutrients.length; i++) {
          var nutrient = nutrients[i];
          fieldDiv.innerHTML += "\n<h2>" + nutrient + "</h2>";
          fieldDiv.innerHTML += '<div class="ui input">' +
                                  '<input type="text" placeholder="Proportion" class="goal-value" id="goal-value-' + nutrient + '">' +
                                '</div>'
          fieldDiv.innerHTML += '<div class="ui basic buttons">' +
                                  '<div class="ui button">Below</div>' +
                                  '<div class="ui button active">Near</div>' +
                                  '<div class="ui button">Above</div>' +
                                '</div>'
        }
    };

    xhr.send();
  }

  function onload() {
    genFieldOptions();
  }

  onload();
}

createGoalNamespace();

function saveGoal() {
  var fields = document.getElementsByClassName("goal-value");

  var data = {'name': document.getElementById("goal-set-name").value,
              'description': document.getElementById("goal-set-description").value}

  for (var i = 0; i < fields.length; i++) {
    fieldID = fields[i].getAttribute("id");
    value = fields[i].value;
    nutrient = fieldID.split("goal-value-")[1]

    if (value === "") {
      value = 0;
    }

    data[nutrient] = value;
  }

  var xhr = new XMLHttpRequest();
  xhr.open('POST', "/api/goals");
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
      if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
          alert('Request failed.  Returned status of ' + xhr.status);
      } else {
        window.location.replace("/users"); // Will redirect to current user
      }
  };

  xhr.send(param(data));
}
