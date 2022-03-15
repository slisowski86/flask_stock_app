from flask import Blueprint
from flask import redirect
server_bp=Blueprint('main', __name__)


@server_bp.route("/")
def hello_world():
        return redirect('/dashboard/')