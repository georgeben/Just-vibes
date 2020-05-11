"""
Authentication Blueprint
"""
from flask import (
  Blueprint, flash, request, redirect, url_for, render_template, session, g, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db
import functools

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')
  if user_id is None:
    g.user = None
  else:
    user = get_user_by_id(user_id)
    g.user = user

def login_required(view):
  @functools.wraps(view)
  def validate_login(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))
    return view(**kwargs)
  return validate_login

@auth_bp.route('/signup', methods=('GET', 'POST'))
def signup():
  if(g.user is not None):
    return redirect(url_for('posts.view_posts'))
  if request.method == 'POST':
    username = request.form.get('username', None)
    password = request.form.get('password', None)
      
    error = None
    if not username:
      error = 'Username is required'
    elif not password:
      error = 'Password is required'
    elif get_existing_user(username) is not None:
      error = 'A user with that email already exists'
  
    if error is None:
      create_new_user(username, password)
      return redirect(url_for('auth.login'))

    flash(error)
  return render_template('auth/signup.html')

@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
  if(g.user is not None):
    return redirect(url_for('posts.view_posts'))
  if request.method == 'POST':
    username = request.form.get('username', None)
    password = request.form.get('password', None)

    error = None
    if not username:
      error = 'Username is required'
    elif not password:
      error = 'Password is required'
     
    if error is None:
      user = validate_user_login(username, password)
      if (user): 
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('posts.view_posts'))
      error ="Incorrect username/password combination"
    flash(error)
    
  return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('posts.view_posts'))


def get_existing_user(username):
  db = get_db()
  c = db.cursor()
  r = c.execute(
      "SELECT * FROM users WHERE username = ?", (username,)
  )
  user = r.fetchone()
  return user

def get_user_by_id(id):
  db = get_db()
  user = db.execute(
    'SELECT * FROM users WHERE id=?',
    (id,)
  ).fetchone()
  return user

def create_new_user(username, password):
  db = get_db()
  password_hash = generate_password_hash(password)
  db.execute(
    'INSERT INTO users (username, password) VALUES (?, ?)',
    (username, password_hash)
  )
  db.commit()


def validate_user_login(username, password):
  user = get_existing_user(username)
  if user is None:
    return False
  elif not check_password_hash(user['password'], password):
    return False
  return user
  
