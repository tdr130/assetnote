from flask import Flask, render_template, request, jsonify, url_for, redirect
from flask.ext.seasurf import SeaSurf
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
import sqlite3
import config
import sqlalchemy

DATABASE = 'assetnote.db'
conn = sqlite3.connect(DATABASE, check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS domains (d_id integer primary key, domain text, first_scan text, push_notification_key text, type text)''')
c.execute('''CREATE TABLE IF NOT EXISTS sent_notifications (n_id integer primary key, new_domain text, push_notification_key text, time_sent timestamp)''')
conn.commit()
# Initialization of variables and modules
app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
csrf = SeaSurf(app)
engine = sqlalchemy.create_engine('mysql://root:testing@localhost:3389/assetnote')
connection = engine.connect()

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

db.create_all()

@app.before_first_request
def create_user():
    to_delete=User.query.filter_by(email='shubs').first()
    if to_delete is not None:
        user_datastore.delete_user(to_delete)
        db.session.commit()
    user_datastore.create_user(email='shubs', password='testing')
    db.session.commit()

def make_external(url):
    return urljoin(request.url_root, url)

@app.route("/")
@login_required
def index():
    c.execute("select * from sent_notifications")
    sent_notifications = c.fetchall()
    return render_template("index.html", sent=sent_notifications)

@app.route("/manage")
@login_required
def manage():
    c.execute("select * from domains")
    all_domains = c.fetchall()
    return render_template("manage.html", domains_monitored=all_domains)

@app.route("/api/get_domains")
@login_required
def get_domain_data():
    c.execute("select * from domains")
    all_domains = c.fetchall()
    return jsonify(data=all_domains)

@app.route("/api/add_domain", methods = ["POST"])
@login_required
def add_domain_api():
    domain = request.form["domain"]
    pushover_key = request.form["pushover_key"]
    try:
        c.execute("insert into domains(domain, first_scan, push_notification_key) values(?, ?, ?)", (domain, "Y", pushover_key))
        conn.commit()
        return jsonify(result="success")
    except Exception as e:
        print e
        return jsonify(result=str(e))

@app.route("/api/delete_domain", methods = ["POST"])
@login_required
def delete_domain_api():
    d_id = request.form["d_id"]
    try:
        delete_rec = c.execute("DELETE FROM domains WHERE d_id=?", (d_id,))
        conn.commit()
        return jsonify(result="success")
    except Exception as e:
        print e
        return jsonify(result=str(e))

if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=80, debug=True)