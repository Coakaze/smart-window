import functools
from os import name

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from . import db
from . import auth

bp = Blueprint('notification', __name__)

@bp.route('/')
def index():
    my_db = db.get_db()
    notifications = my_db.execute(
        'SELECT *'
        ' FROM swNotification n JOIN ('
        ' 	SELECT sw.id AS windowID, sw.userID'
        '	FROM swindow sw JOIN user u ON sw.userID = u.id'
        ' ) w ON n.windowID = w.windowID'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('swNotification/index.html', notifications=notifications)


@bp.route('/create', methods=('GET', 'POST'))
@auth.login_required
def create():
    if request.method == 'POST':
        error = None
        content = request.form['content']

        if not content:
            error = 'Content is required.'

        if error is not None:
            flash(error)
        else:
            my_db = db.get_db()
            my_db.execute(
                'INSERT INTO swNotification (content, windowID)'
                ' VALUES (?, ?)',
                (content, g.swindow['id'])
            )
            my_db.commit()
            return redirect(url_for('swNotification.index'))

    return render_template('swNotification/create.html')


def get_notification(id, check_user=True):
    notification = db.get_db().execute(
        'SELECT *'
        ' FROM swNotification n JOIN ('
        ' 	SELECT sw.id AS windowID, sw.userID'
        '	FROM swindow sw JOIN user u ON sw.userID = u.id'
        ' ) w ON n.windowID = w.windowID'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if notification is None:
        abort(404, f"Notification id {id} doesn't exist.")

    if check_user and notification['userID'] != g.user['id']:
        abort(403)

    return notification


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@auth.login_required
def update(id):
    notification = get_notification(id)

    if request.method == 'POST':
        name = request.form['name']
        error = None

        iStart = request.form['iStart']        
        iEnd = request.form['iEnd']
        if not iStart or not iEnd:
            error = 'notification field missing'

        luminosity = request.form['luminosity']
        
        if error is not None:
            flash(error)
        else:
            my_db = db.get_db()
            my_db.execute(
                'UPDATE swNotification SET content = ?'
                ' WHERE id = ?',
                (name, iStart, iEnd, luminosity, id)
            )
            my_db.commit()
            return redirect(url_for('swNotification.index'))

    return render_template('swNotification/update.html', notification=notification)


@bp.route('/<int:id>/delete', methods=('POST',))
@auth.login_required
def delete(id):
    my_db = db.get_db()
    my_db.execute('DELETE FROM swNotification WHERE id = ?', (id,))
    my_db.commit()
    return redirect(url_for('swNotification.index'))