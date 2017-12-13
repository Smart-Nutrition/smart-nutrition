import flask
import smartNutrition


@smartNutrition.app.route('/login/')
def show_login():
    """Display / route."""
    context = {}
    if "username" not in flask.session:
        context["logname"] = ""
    else:
        context["logname"] = flask.session["username"]
    return flask.render_template("login.html", **context)
