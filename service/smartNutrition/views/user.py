import flask
import smartNutrition


@smartNutrition.app.route('/users/<user_id>/')
def show_user(user_id):
    """Display / route."""
    context = {}
    if "username" not in flask.session:
        context["logname"] = ""
        return flask.redirect(flask.url_for('show_login'))
    else:
        context["logname"] = flask.session["username"]

    return flask.render_template("user.html", **context)
