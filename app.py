import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Exercise, Submission, Session, init_db
from forms import RegisterForm, LoginForm, CodeSubmissionForm
from evaluator import run_restricted_code
from config import Config
from sqlalchemy.orm import joinedload  # ADD THIS IMPORT

# Initialize DB (create tables if not exist)
init_db()

app = Flask(__name__)
app.config.from_object(Config)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class LoginUser(UserMixin):
    def __init__(self, user_obj):
        self.id = str(user_obj.id)
        self.username = user_obj.username

@login_manager.user_loader
def load_user(user_id):
    db = Session()
    user = db.query(User).filter_by(id=int(user_id)).first()
    db.close()
    if user:
        return LoginUser(user)
    return None

@app.teardown_appcontext
def remove_session(exception=None):
    Session.remove()

@app.route('/')
def index():
    db = Session()
    exercises = db.query(Exercise).order_by(Exercise.id).all()
    db.close()
    return render_template('index.html', exercises=exercises)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    db = Session()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        if db.query(User).filter_by(username=username).first():
            flash('Username already exists. Choose another.', 'danger')
            db.close()
            return render_template('register.html', form=form)
        u = User(username=username, password_hash=generate_password_hash(password))
        db.add(u)
        db.commit()
        flash('Registration successful. Please log in.', 'success')
        db.close()
        return redirect(url_for('login'))
    db.close()
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db = Session()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        user = db.query(User).filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(LoginUser(user))
            flash('Logged in successfully', 'success')
            db.close()
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'danger')
    db.close()
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    db = Session()
    exercises = db.query(Exercise).order_by(Exercise.id).all()
    # Eager load exercise relationship
    submissions = db.query(Submission)\
        .options(joinedload(Submission.exercise))\
        .filter_by(user_id=int(current_user.id))\
        .order_by(Submission.created_at.desc())\
        .limit(10).all()
    db.close()
    return render_template('dashboard.html', exercises=exercises, submissions=submissions)

@app.route('/exercise/<int:ex_id>', methods=['GET', 'POST'])
@login_required
def exercise_view(ex_id):
    db = Session()
    exercise = db.query(Exercise).filter_by(id=ex_id).first()
    if not exercise:
        db.close()
        flash('Exercise not found', 'danger')
        return redirect(url_for('dashboard'))
    
    form = CodeSubmissionForm()
    if request.method == 'GET':
        form.code.data = exercise.starter_code or ''
    
    if form.validate_on_submit():
        code = form.code.data
        eval_result = run_restricted_code(code, stdin_text='')
        output = eval_result.get('output', '')
        error = eval_result.get('error', '')
        passed = False
        
        expected = (exercise.expected_output or '').strip()
        if expected:
            if output.strip() == expected:
                passed = True
        else:
            passed = eval_result['success']

        sub = Submission(user_id=int(current_user.id), exercise_id=exercise.id,
                         code=code, result=(error or output)[:4000], passed=passed)
        db.add(sub)
        db.commit()
        flash('Code submitted. Passed: {}'.format(passed), 'info')
        db.close()
        return redirect(url_for('exercise_view', ex_id=ex_id))
    
    # Eager load exercise relationship
    subs = db.query(Submission)\
        .options(joinedload(Submission.exercise))\
        .filter_by(user_id=int(current_user.id), exercise_id=exercise.id)\
        .order_by(Submission.created_at.desc()).limit(5).all()
    
    db.close()
    return render_template('excercise.html', exercise=exercise, form=form, submissions=subs)  # Fixed typo

@app.route('/profile')
@login_required
def profile():
    db = Session()
    user = db.query(User).filter_by(id=int(current_user.id)).first()
    # Eager load both relationships
    subs = db.query(Submission)\
        .options(joinedload(Submission.exercise), joinedload(Submission.user))\
        .filter_by(user_id=int(current_user.id))\
        .order_by(Submission.created_at.desc()).all()
    db.close()
    return render_template('profile.html', user=user, submissions=subs)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)