import re
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, g, make_response
)
from flaskr.auth import login_required
from flaskr.db import get_db, get_redis
from werkzeug.exceptions import abort

bp = Blueprint('blog', __name__)

def like(post, redis):
    post = dict(post)

    post_id = f"post_{post['id']}"
    post['total_post_like'] = redis.scard(post_id)
    post['the_user_like'] = redis.sismember(post_id, g.user['id']) if g.user is not None else False
    return post

def pre_body(post):
    post['body'] = re.sub(r"[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*<>]+", " ", post["body"])
    return post

@bp.route('/')
@bp.route('/<int:cur_page>')
def index(cur_page=1, page_size=5):

    db = get_db()
    redis = get_redis()

    start_position = (cur_page-1)*page_size

    posts = db.execute(
        'SELECT p.id, title, body, p.created, author_id, total_post_like, total_post_comment, username'
        ' FROM post p LEFT JOIN user u ON p.author_id = u.id'
        ' ORDER BY p.created DESC'
        ' LIMIT ?, ?',
        (start_position, page_size)
    ).fetchall()
    
    total_count = db.execute(
        'SELECT COUNT(id) FROM post'
    ).fetchone()

    total_page = (total_count[0] // page_size) + 1

    posts = map(lambda x: like(x, redis), posts)
    posts = map(pre_body, posts)

    return render_template(
        'blog/index.html', 
        posts=posts, 
        cur_page=cur_page, 
        total_page=total_page)

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
        'SELECT p.id, title, body, created, author_id, total_post_like, total_post_comment, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn`t exist.")
    if check_author and post['author_id'] != g.user['id']:
        abort(403, f"Author doesn`t right")
    
    redis = get_redis()
    post = like(post, redis)
    
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
