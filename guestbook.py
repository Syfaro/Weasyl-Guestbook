import os
import datetime
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, g


app = Flask(__name__)
DATABASE = os.getcwd() + os.sep + 'guestbook.db'


def get_database():
    return sqlite3.connect(DATABASE)


def get_entries():
    db = g.db

    c = db.cursor()
    c.execute(
        'SELECT `id`, `name`, `message`, `posted_at` FROM `messages` \
            ORDER BY `id` DESC')
    entries = c.fetchall()

    return entries


def add_entry(name, message):
    db = g.db

    c = db.cursor()
    c.execute('INSERT INTO `messages` (`name`, `message`) VALUES (?, ?)',
              (name, message, ))

    db.commit()


def remove_entry(id):
    db = g.db

    c = db.cursor()
    c.execute('DELETE FROM `messages` WHERE `id` = ?', id)

    db.commit()


@app.before_request
def before_request():
    if getattr(g, 'db', None) is None:
        g.db = get_database()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)

    if db is not None:
        db.close()


@app.route('/')
def index():
    return render_template(
        'index.html', entries=get_entries())


@app.route('/submit', methods=['POST'])
def submit():
    if not request.form['name']:
        flash('You must provide a name!')
        return redirect('/')

    add_entry(request.form['name'], request.form['entry'])

    flash('Message added!')
    return redirect('/')


@app.route('/admin')
def admin_login():
    if 'logged_in' in session and session['logged_in']:
        return redirect('/')

    return render_template('login.html')


@app.route('/admin', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password':
        session['logged_in'] = True
        return redirect('/')

    else:
        flash('Wrong password!')

    return admin_login()


@app.route('/moderate', methods=['POST'])
def moderate_posts():
    if session['logged_in']:
        remove_entry(request.form['id'])

        flash('Removed entry')
        return redirect('/')

    flash('You need to be logged in to do this!')
    return redirect('/admin')


if __name__ == '__main__':
    db = get_database()

    c = db.cursor()
    c.execute(
        'CREATE TABLE IF NOT EXISTS `messages` ( \
            id INTEGER PRIMARY KEY, \
            name VARCHAR(255), \
            message TEXT, \
            posted_at DATETIME DEFAULT CURRENT_TIMESTAMP)')

    db.close()

    app.secret_key = os.urandom(12)
    app.run(debug=True)
