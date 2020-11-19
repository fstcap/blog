from flask import (
    Blueprint, request, make_response, g
)
from flaskr.auth import login_required
from flaskr.db import get_redis, get_db

bp = Blueprint('like', __name__, url_prefix='/like')

@bp.route('/<int:id>/<string:ob>', methods=['POST', 'DELETE'])
@login_required
def add_delete(id, ob):
    redis = get_redis()
    db = get_db()
    if request.method == 'POST':
        try:
            redis.sadd(f"{ob}_{id}", g.user['id'])
        except:
            return make_response('fail add like', 500)
        else:
            return make_response('success add like', 200)
    try:
        redis.srem(f"{ob}_{id}", g.user['id'])
    except:
        return make_response('fail add like', 500)
    else:
        return make_response('success add like', 200)
