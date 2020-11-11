from flask import (
        Blueprint, render_template, request, flash, redirect, url_for, g, make_response
)
from flaskr.auth import login_required
from flaskr.db import get_db, get_redis
from werkzeug.exceptions import abort

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    redis = get_redis()
    posts = db.execute(
        'SELECT p.id, title, body, p.created, author_id, username'
        ' FROM post p LEFT JOIN user u ON p.author_id = u.id'
        ' ORDER BY p.created DESC'
    ).fetchall()
   
    for index, value in enumerate(posts):
        posts[index] = dict(value)
        posts[index]['total_post_like'] = redis.scard(value['id'])
        posts[index]['the_user_like'] = redis.sismember(value['id'], g.user['id']) if g.user is not None else False
    
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn`t exist.")
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?,body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@bp.route('/<int:id>/like', methods=['POST', 'DELETE'])
@login_required
def like(id):
    redis = get_redis()
    if request.method == "POST":
        try: 
            redis.sadd(id, g.user['id'])
        except:
            return make_response('fail add like', 500)
        else:
            return make_response('success add like', 200)
    try:
        redis.srem(id, g.user['id'])
    except:
        return make_response('fail delete like', 500)
    else:
        return make_response('success delete like', 200)
