import flask
import smartNutrition


@smartNutrition.app.route('/signout/')
def show_signout():
    """Display / route."""
    context = {}

    return flask.render_template("signout.html", **context)
