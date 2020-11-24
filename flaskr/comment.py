from flask import (
    Blueprint, render_template, request, flash, redirect, url_for, abort, g
)
from flaskr.auth import login_required
from flaskr.db import get_db, get_redis
from flaskr.blog import get_post

bp = Blueprint('comment', __name__, url_prefix='/comment')

def like(comment, redis):
    comment = dict(comment)
    comment_id = f"comment_{comment['id']}"
    comment['total_comment_like'] = redis.scard(comment_id)
    comment['the_user_like'] = redis.sismember(comment_id, g.user['id']) if g.user is not None else False
    return comment

@bp.route('/<int:post_id>')
@bp.route('/<int:post_id>/<int:cur_page>')
def index(post_id, cur_page=1, page_size=5):
    db = get_db()
    redis = get_redis()
    post = get_post(post_id, check_author=False)
    
    start_position = (cur_page-1)*page_size
    
    comments = db.execute(
        'SELECT c1.id, c1.body, c1.created, c1.comment_id, c1.post_id,'
        ' c1.author_id by_author_id, c2.author_id to_author_id,'
        ' u1.username by_username, u2.username to_username'
        ' FROM comment c1 LEFT'
        ' JOIN comment c2 ON c1.comment_id=c2.id LEFT'
        ' JOIN user u1 ON by_author_id=u1.id LEFT'
        ' JOIN user u2 ON to_author_id=u2.id'
        ' WHERE c1.post_id=?'
        ' ORDER BY c1.created DESC'
        ' LIMIT ?, ?',
        (post_id, start_position, page_size)
    ).fetchall()

    total_count = db.execute(
        'SELECT COUNT(id) FROM comment WHERE post_id=?',
        (post_id,)
    ).fetchone()

    total_page = (total_count[0] // page_size) + 1

    comments = map(lambda x: like(x, redis), comments)

    return render_template(
        'comment/index.html', 
        post=post, 
        comments=comments, 
        cur_page=cur_page, 
        total_page=total_page)

def get_comment(id, check_author=True):
    comment = get_db().execute(
        'SELECT c1.id, c1.body, c1.created, c1.comment_id, c1.post_id,'
        ' c1.author_id by_author_id, c2.author_id to_author_id,'
        ' u1.username by_username, u2.username to_username'
        ' FROM comment c1 LEFT'
        ' JOIN comment c2 ON c1.comment_id=c2.id LEFT'
        ' JOIN user u1 ON by_author_id=u1.id LEFT'
        ' JOIN user u2 ON to_author_id=u2.id'
        ' WHERE c1.id=?',
        (id,)
    ).fetchone()
    
    if comment is None:
        return None
    if check_author and comment['by_author_id'] != g.user['id']:
        abort('403', f"Author doesn`t right")
    
    redis = get_redis()
    comment = like(comment, redis)
    return comment

@bp.route('/<int:post_id>/create', methods=['GET', 'POST'])
@bp.route('/<int:post_id>/<int:comment_id>/create', methods=['GET', 'POST'])
@login_required
def create(post_id, comment_id=None):
    if request.method == 'POST':
        body = request.form['body']
        error = None
        
        if not body:
            error = 'Body is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            
            db.execute(
                'INSERT INTO comment (post_id, comment_id, author_id, body)'
                ' VALUES (?, ?, ?, ?)',
                (post_id, comment_id, g.user['id'], body)
            )

            db.execute(
                'UPDATE post SET total_post_comment=total_post_comment+1'
                ' WHERE id=?',
                (post_id,)
            )

            db.commit()
            return redirect(url_for('comment.index', post_id=post_id))
    
    post = get_post(post_id, check_author=False)
    comment = get_comment(comment_id, check_author=False)
    return render_template('comment/create.html', post=post, comment=comment)

@bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    comment = get_comment(id)
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            
            db.execute(
                'UPDATE comment SET body = ?'
                ' WHERE id = ?',
                (body, id)
            )
            db.commit()
            return redirect(url_for('comment.index', post_id=comment['post_id']))
    
    return render_template('comment/update.html', comment=comment)

@bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    comment = get_comment(id)
    db = get_db()
    db.execute('DELETE FROM comment WHERE id=?', (id,))
    
    db.execute(
        'UPDATE post SET total_post_comment=total_post_comment-1'
        ' WHERE id=?',
        (comment['post_id'],)
    )

    db.commit()
    return redirect(url_for('comment.index',post_id=comment['post_id']))
