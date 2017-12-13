function addKrogerPostRequest(username, password) {
    var xhr = new XMLHttpRequest();

    var requestObj = {"username": "", "password": ""};

    // Recal these are Kroger credentials.
    requestObj.username = username;
    requestObj.password = password;

    xhr.open('POST', "/api/providers/Kroger");
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
            alert('Request failed.  Returned status of ' + xhr.status);
        }
    };

    xhr.send(param(requestObj));
}

function removeKrogerPostRequest(username, password) {
    var xhr = new XMLHttpRequest();

    xhr.open('DELETE', "/api/providers/Kroger");
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
            alert('Request failed.  Returned status of ' + xhr.status);
        }
    };

    xhr.send();
}

function finishAddKrogerTrigger() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    addKrogerPostRequest(username, password);
    krogerSetUpdateUI();
}

function finishRemoveKrogerTrigger() {
    removeKrogerPostRequest(username, password);
    krogerRemovedUpdateUI();
}

function krogerSetUpdateUI() {
    var kDiv = document.getElementById('addKrogerDiv');
    var kIcon = document.getElementById('addKrogerDivIcon');
    var kText = document.getElementById('addKrogerDivText');
    kDiv.className += " positive";
    kDiv.onclick = function() {krogerRemoveProviderTrigger();};
    kIcon.className = "checkmark icon";
    kText.textContent = "Added";
}

function krogerRemovedUpdateUI() {
    var kDiv = document.getElementById('addKrogerDiv');
    var kIcon = document.getElementById('addKrogerDivIcon');
    var kText = document.getElementById('addKrogerDivText');
    kDiv.className = "ui bottom attached button";
    kDiv.onclick = function() {krogerAddProviderTrigger();};
    kIcon.className = "add icon";
    kText.textContent = "Add Provider";
}

function krogerRemoveProviderTrigger() {
    $('#removeModal').modal('show');
}

function krogerAddProviderTrigger() {
    $('#addModal').modal('show');
}

function checkKroger() {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', "/api/providers");
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
            alert('Request failed.  Returned status of ' + xhr.status);
        } else {
            var data = JSON.parse(xhr.responseText);

            if (data.Kroger !== undefined) {
                krogerSetUpdateUI();
            }
        }
    };

    xhr.send();
}

function checkGoal() {
    var xhr = new XMLHttpRequest();

    xhr.open('GET', "/api/summary");
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
            alert('Request failed.  Returned status of ' + xhr.status);
        } else {
            var data = JSON.parse(xhr.responseText);

            if (data.goals.name !== undefined) {
                var ele = document.getElementById(data.goals.name);

                if (ele !== null) {
                  toggleGoal(data.goals.name);
                }
            }
        }
    };

    xhr.send();
}

function toggleGoal(goalName) {
  var goalDiv = document.getElementById(goalName);
  var goalDivIcon = document.getElementById((goalName + 'Icon'));
  var goalDivText = document.getElementById((goalName + 'Text'));
  goalDiv.className += " positive";
  goalDiv.onclick = function() {};
  goalDivIcon.className = "checkmark icon";
  goalDivText.textContent = "Added";
}

function patchGoal(goalName, goals) {
  // Send patch request to set user's goal. Make sure name matches.
  var xhr = new XMLHttpRequest();
  var data = {'name': goalName};
  for (var i = 0; i < goals.length; i++) {
    if (goalName === goals[i].name) {

      var attributes = Object.keys(goals[i].goals);

      for (var j = 0; j < attributes.length; j++) {
        if (attributes[j] !== "calories" && goals[i].goals[attributes[j]] !== null) {
          data[attributes[j]] = goals[i].goals[attributes[j]].value;
        }
      }
    }
  }

  xhr.open('PATCH', "/api/users/goals");
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
      if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
          alert('Request failed.  Returned status of ' + xhr.status);
      } else {
        toggleGoal(goalName);
      }
  };

  xhr.send(param(data));

}

function useGoal(goalName) {
  var xhr = new XMLHttpRequest();

  xhr.open('GET', "/api/goals");
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
      if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
          alert('Request failed.  Returned status of ' + xhr.status);
      } else {
          var response = JSON.parse(xhr.responseText);

          patchGoal(goalName, response.goals);
      }
  };

  xhr.send();
}

function addGoal() {
  window.location.href = "/create-goal/";
}

function genGoalHTML(goalID, goalName, goalDescription) {
    return '<div class="card">' +
                '<div class="content">' +
                  '<div class="header">' + goalName + '</div>' +
                  '<div class="description">' +
                     goalDescription +
                  '</div>' +
                '</div>' +
                '<div id="' + goalName + '" class="ui bottom attached button" onclick="useGoal(\'' + goalName + '\')">' +
                  '<i class="add icon" id="' + goalName + 'Icon"></i>' +
                  '<div class="inline-div" id="' + goalName + 'Text"> Use Goal </div>' +
                '</div>' +
              '</div>';
}

function genGoalCreateHTML() {
  return '<div class="card">' +
             '<button class="big ui primary basic button" style="height: 100%" onclick="addGoal()"> Create Custom Goal' +
             '</button>' +
         '</div>';
}

function fillGoals() {
    var container = document.getElementById('goalsDiv');

    var xhr = new XMLHttpRequest();

    xhr.open('GET', "/api/goals");
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        if (xhr.status !== 200 && xhr.status !== 201 && xhr.status !== 204) {
            alert('Request failed.  Returned status of ' + xhr.status);
        } else {
            var data = JSON.parse(xhr.responseText);

            if (data.goals !== undefined) {
                for (var i = 0; i < data.goals.length; i++) {
                    container.innerHTML += genGoalHTML(i, data.goals[i].name, data.goals[i].description);
                }
            }

            container.innerHTML += genGoalCreateHTML();
            checkGoal();

        }
    };

    xhr.send();
}

// On load
checkKroger();
fillGoals();
