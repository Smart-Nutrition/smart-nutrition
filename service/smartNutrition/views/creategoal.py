import flask
import smartNutrition


@smartNutrition.app.route('/create-goal/')
def show_creategoal():
    """Display / route."""
    context = {}
    if "username" not in flask.session:
        context["logname"] = ""
        return flask.redirect(flask.url_for('show_login'))
    else:
        context["logname"] = flask.session["username"]

    return flask.render_template("create-goal.html", **context)
