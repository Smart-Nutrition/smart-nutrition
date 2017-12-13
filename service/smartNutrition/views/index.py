import flask
import smartNutrition


@smartNutrition.app.route('/')
def show_index():
    """Display / route."""
    context = {}
    if "username" not in flask.session:
        context["logname"] = ""
        return flask.redirect(flask.url_for('show_login'))
    else:
        context["logname"] = flask.session["username"]

    return flask.render_template("index.html", **context)
