# coding=utf8

from datetime import datetime

from messageboard import app
from messageboard.models import Message

from flask import flash, render_template, request, redirect, url_for


@app.route('/', methods=['GET'])
def index():
    query = Message.orderby(
        Message.create_at, desc=True).select()  # sort by created time
    results = query.execute()
    messages = results.all()
    return render_template('template.html', messages=messages)


@app.route('/create', methods=['POST'])
def create():
    title = request.form['title']
    content = request.form['content']

    if title and content:
        message = Message.create(
            title=title, content=content, create_at=datetime.now())
        if message is not None:  # ok
            flash(dict(type='success', content='New message created'))
        else:  # create failed
            flash(dict(type='error', content='Failed to create new message'))
    else:  # invalid input
        flash(dict(type='warning', content='Empty input'))
    return redirect(url_for('index'))
