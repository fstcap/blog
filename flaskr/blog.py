from flask import (
        Blueprint, render_template, request, flash, redirect, url_for, g, make_response
)
from flaskr.auth import login_required
from flaskr.db import get_db
from werkzeug.exceptions import abort

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, p.created, author_id, total_like_count, username, ulp.user_id'
        ' FROM post p LEFT JOIN user u ON p.author_id = u.id LEFT'
        ' JOIN user_like_post ulp ON ulp.user_id = p.author_id AND ulp.post_id = p.id'
        ' ORDER BY p.created DESC'
    ).fetchall()
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
    db = get_db()
    if request.method == "POST":
        try:
            db.execute(
                'INSERT INTO user_like_post (user_id, post_id)'
                ' VALUES (?, ?)',
                (g.user['id'], id)
            )
            db.execute(
                'UPDATE post SET total_like_count = total_like_count + 1'
                ' WHERE id = ?',
                (id,)
            )
            db.commit()
            return make_response('success add like', 200)
        except:
            return make_response('fail add like', 500)
    try:
        db.execute(
            'DELETE FROM user_like_post WHERE user_id=? AND post_id=?',
            (g.user['id'], id)
        )
        db.execute(
            'UPDATE post SET total_like_count = total_like_count - 1'
            ' WHERE id = ?',
            (id,)
        )
        db.commit()
        return make_response('success delete like', 200)
    except:
        return make_response('fail delete like', 500)
