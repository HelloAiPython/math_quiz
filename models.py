from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联练习记录
    quiz_records = db.relationship('QuizRecord', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_total_score(self):
        return sum(record.score for record in self.quiz_records)
    
    def get_accuracy_rate(self):
        if not self.quiz_records:
            return 0
        total_questions = sum(record.total_questions for record in self.quiz_records)
        correct_answers = sum(record.correct_answers for record in self.quiz_records)
        return round((correct_answers / total_questions) * 100, 2) if total_questions > 0 else 0

class QuizRecord(db.Model):
    __tablename__ = 'quiz_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)  # easy, medium, hard
    operation = db.Column(db.String(20), nullable=False)  # add, subtract, multiply, divide, mixed
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_time = db.Column(db.Integer, nullable=False)  # 秒数
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_accuracy_rate(self):
        return round((self.correct_answers / self.total_questions) * 100, 2) if self.total_questions > 0 else 0

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_record_id = db.Column(db.Integer, db.ForeignKey('quiz_records.id'), nullable=False)
    question_text = db.Column(db.String(100), nullable=False)
    correct_answer = db.Column(db.Integer, nullable=False)
    user_answer = db.Column(db.Integer)
    is_correct = db.Column(db.Boolean, nullable=False)
    time_spent = db.Column(db.Integer, nullable=False)  # 秒数
    
    quiz_record = db.relationship('QuizRecord', backref='questions')