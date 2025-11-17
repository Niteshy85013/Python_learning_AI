"""
Small script to seed the database with sample exercises and (optionally) admin user.
Run: python data_seed.py
"""

from models import Session, init_db, User, Exercise
from werkzeug.security import generate_password_hash

init_db()
db = Session()

# Create admin user if not exists
admin = db.query(User).filter_by(username='admin').first()
if not admin:
    admin = User(username='admin', password_hash=generate_password_hash('admin123'), is_admin=True)
    db.add(admin)

# Sample Exercises
samples = [
    {
        'title': 'Hello World',
        'description': 'Write a program that prints "Hello, world!" exactly.',
        'starter_code': 'print("Hello, world!")',
        'expected_output': 'Hello, world!',
        'difficulty': 'Beginner'
    },
    {
        'title': 'Sum Two Numbers',
        'description': 'Read two integers from input (each on separate line) and print their sum.',
        'starter_code': 'a = int(input())\nb = int(input())\nprint(a + b)',
        'expected_output': '7',  # sample expected; when running tests provide inputs
        'difficulty': 'Beginner'
    },
    {
        'title': 'List Length',
        'description': 'Given a list, print its length. Example: for [1,2,3] print 3.',
        'starter_code': 'lst = [1,2,3]\nprint(len(lst))',
        'expected_output': '3',
        'difficulty': 'Beginner'
    },
]

for s in samples:
    if not db.query(Exercise).filter_by(title=s['title']).first():
        ex = Exercise(title=s['title'], description=s['description'],
                      starter_code=s['starter_code'], expected_output=s['expected_output'],
                      difficulty=s['difficulty'])
        db.add(ex)

db.commit()
db.close()
print("Seeded DB with sample exercises and admin user (username=admin, password=admin123)")
