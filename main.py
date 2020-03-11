import datetime

from flask import Flask, render_template

from data import db_session
from data.jobs import Jobs
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/jobs.sqlite")
    app.run()


@app.route("/")
def index():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = session.query(User).all()
    us = {}
    for u in users:
        us.update({u.id: u.surname + ' ' + u.name})
    return render_template("index.html", jobs=jobs, us=us)


if __name__ == '__main__':
    main()
