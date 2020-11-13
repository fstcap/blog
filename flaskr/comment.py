from flask import (
    Blueprint
)
from flaskr.auth import login_required
from flaskr.db import get_redis

bp = Blueprint('comment', __name__, url_prefix='/comment')

@bp.route('/<int:id>')
def index(id):
    redis = get_redis()


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():

