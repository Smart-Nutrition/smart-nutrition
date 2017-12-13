import flask
import smartNutrition


@smartNutrition.app.route('/signup/')
def show_signup():
    """Display / route."""
    context = {}
    if "username" not in flask.session:
        context["logname"] = ""
    else:
        context["logname"] = flask.session["username"]
    return flask.render_template("signup.html", **context)
