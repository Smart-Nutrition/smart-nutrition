import flask
import smartNutrition


@smartNutrition.app.route('/users/')
def show_users():
    """Display /users route. Redirects to /users/loggedin"""
    context = {}
    if "username" not in flask.session:
        context["logname"] = ""
        return flask.redirect(flask.url_for('show_login'))
    else:
        context["logname"] = flask.session["username"]

    return flask.redirect("/users/" + context["logname"])
