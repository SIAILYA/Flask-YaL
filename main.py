from datetime import datetime

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.forms.add_work_form import AddWorkForm
from data.forms.login_form import LoginForm
from data.forms.register_form import RegisterForm
from data.jobs import Jobs
from data.users import User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/jobs.sqlite")
    app.run()


@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route("/jobs_list")
def jobs_list():
    session = db_session.create_session()
    jobs = session.query(Jobs).all()
    users = session.query(User).all()
    us = {}
    for u in users:
        us.update({u.id: u.surname + ' ' + u.name})
    return render_template("jobs_list.html", jobs=jobs, us=us)


@app.route("/add_job", methods=['GET', 'POST'])
@login_required
def add_job():
    form = AddWorkForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        users_ids = [u.id for u in session.query(User).all()]
        if form.team_leader.data not in users_ids:
            form.team_leader.errors = 'Нет пользователя с таким ID!'
            return render_template('add_job.html', form=form, title='Добавление работы', error='1')
        else:

            new_job = Jobs(job=form.job.data,
                           work_size=form.work_size.data,
                           collaborators=form.collaborators.data,
                           is_finished=form.is_finished.data,
                           team_leader=form.team_leader.data)
            session.add(new_job)
            session.commit()
            return redirect('/jobs_list')
    return render_template('add_job.html', form=form, title='Добавление работы')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.login.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(name=form.name.data,
                    surname=form.surname.data,
                    age=int(form.age.data),
                    position=form.position.data,
                    speciality=form.speciality.data,
                    address=form.address.data,
                    email=form.login.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()

        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.login.data).first()
        login_user(user)
        return redirect('/')
    return render_template('register.html', form=form, title='Регистрация')


@app.route('/okay')
def okay():
    return 'Вы успешно зарегистрированы в системе!'


if __name__ == '__main__':
    main()
