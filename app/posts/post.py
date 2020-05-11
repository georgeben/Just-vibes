from flask import (
  Blueprint, render_template, request as req, flash, g, redirect, url_for,abort
)
from flask.cli import with_appcontext
from app.auth.auth import login_required
from app.db import get_db

bp = Blueprint('posts', __name__)

@bp.route('/')
def view_posts():
  posts = fetch_all_posts()
  return render_template('posts/index.html.j2', posts=posts)

@bp.route('/new', methods = ('GET', 'POST'))
@login_required
def create():
  if req.method == 'POST':
    error = None
    content = req.form.get('content', None)
    if content is None:
      error = 'Cannot create an empty post'

    if error is None:
      save_post(content)
      return redirect(url_for('posts.view_posts'))
    flash(error)
  return render_template('posts/create.html.j2')

@bp.route('/delete/<int:id>', methods = ('POST',))
@login_required
def delete_post(id):
  fetch_post(id)
  delete_post_from_db(id)
  return redirect(url_for('posts.view_posts'))


def fetch_all_posts():
  db = get_db()
  posts = db.execute(
    """
    SELECT posts.id AS post_id, content, posts.created_at as created_at, username, users.id, user_id
    FROM posts
    INNER JOIN users ON posts.user_id = users.id
    ORDER BY posts.created_at DESC
    """
  ).fetchall()
  return posts

def save_post(content):
  db = get_db()
  db.execute(" INSERT INTO posts ( content, user_id ) VALUES (?, ?)", (content, g.user['id']))
  db.commit()

def fetch_post(id, checkUser = True):
  db = get_db()
  post = db.execute(
    """
    SELECT posts.id, content, user_id, posts.created_at
    FROM posts
    INNER JOIN users ON posts.user_id = users.id
    WHERE posts.id = ?
    """,
    (id,)
  ).fetchone()

  if post is None:
    abort(404, f"Post with ID {id} was not found")
  if checkUser and post['user_id'] != g.user['id']:
    abort(403)

def delete_post_from_db(id):
  db = get_db()
  db.execute(
    """
    DELETE FROM posts
    WHERE id = ?
    """,
    (id, )
  )
  db.commit()

