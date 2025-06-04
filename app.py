from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, QuizRecord, Question
from forms import LoginForm, RegisterForm, QuizSettingsForm, AnswerForm
from config import Config
import random
import time
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面。'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 生成数学题目的函数
def generate_question(difficulty, operation_type):
    """根据难度和运算类型生成题目"""
    if difficulty == 'easy':
        min_num, max_num = 1, 20
    elif difficulty == 'medium':
        min_num, max_num = 1, 100
    else:  # hard
        min_num, max_num = 1, 1000
    
    if operation_type == 'mixed':
        operation_type = random.choice(['add', 'subtract', 'multiply', 'divide'])
    
    if operation_type == 'add':
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, max_num)
        question = f"{a} + {b} = ?"
        answer = a + b
    elif operation_type == 'subtract':
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, a)  # 确保结果为正数
        question = f"{a} - {b} = ?"
        answer = a - b
    elif operation_type == 'multiply':
        # 乘法使用较小的数字
        if difficulty == 'easy':
            a = random.randint(1, 10)
            b = random.randint(1, 10)
        elif difficulty == 'medium':
            a = random.randint(1, 20)
            b = random.randint(1, 20)
        else:
            a = random.randint(1, 50)
            b = random.randint(1, 50)
        question = f"{a} × {b} = ?"
        answer = a * b
    else:  # divide
        # 除法确保整除
        if difficulty == 'easy':
            b = random.randint(1, 10)
            answer = random.randint(1, 10)
        elif difficulty == 'medium':
            b = random.randint(1, 20)
            answer = random.randint(1, 20)
        else:
            b = random.randint(1, 50)
            answer = random.randint(1, 50)
        a = b * answer
        question = f"{a} ÷ {b} = ?"
    
    return question, answer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 检查用户名是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在，请选择其他用户名。', 'error')
            return render_template('register.html', form=form)
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=form.email.data).first():
            flash('邮箱已被注册，请使用其他邮箱。', 'error')
            return render_template('register.html', form=form)
        
        # 创建新用户
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功！请登录。', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'欢迎回来，{user.username}！', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('用户名或密码错误。', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录。', 'info')
    return redirect(url_for('index'))

@app.route('/quiz_settings', methods=['GET', 'POST'])
@login_required
def quiz_settings():
    form = QuizSettingsForm()
    if form.validate_on_submit():
        # 将设置保存到session中
        session['quiz_settings'] = {
            'difficulty': form.difficulty.data,
            'operation_type': form.operation_type.data,
            'question_count': int(form.question_count.data)
        }
        session['current_question'] = 0
        session['correct_count'] = 0
        session['questions'] = []
        session['start_time'] = time.time()
        
        return redirect(url_for('quiz'))
    
    return render_template('quiz_settings.html', form=form)

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if 'quiz_settings' not in session:
        flash('请先设置练习参数。', 'warning')
        return redirect(url_for('quiz_settings'))
    
    settings = session['quiz_settings']
    current_question = session.get('current_question', 0)
    total_questions = settings['question_count']
    
    # 检查是否完成所有题目
    if current_question >= total_questions:
        return redirect(url_for('quiz_result'))
    
    form = AnswerForm()
    
    # 生成当前题目
    if current_question >= len(session.get('questions', [])):
        question_text, correct_answer = generate_question(
            settings['difficulty'], 
            settings['operation_type']
        )
        session['questions'].append({
            'text': question_text,
            'answer': correct_answer,
            'start_time': time.time()
        })
        session.modified = True
    
    current_q = session['questions'][current_question]
    
    if form.validate_on_submit():
        # 记录答题时间
        question_time = int(time.time() - current_q['start_time'])
        user_answer = form.answer.data
        is_correct = user_answer == current_q['answer']
        
        # 更新题目信息
        session['questions'][current_question].update({
            'user_answer': user_answer,
            'is_correct': is_correct,
            'time_spent': question_time
        })
        
        if is_correct:
            session['correct_count'] = session.get('correct_count', 0) + 1
        
        session['current_question'] = current_question + 1
        session.modified = True
        
        return redirect(url_for('quiz'))
    
    # 计算总用时
    total_time = int(time.time() - session['start_time'])
    
    return render_template('quiz.html', 
                         form=form,
                         question_text=current_q['text'],
                         current_question=current_question,
                         total_questions=total_questions,
                         correct_count=session.get('correct_count', 0),
                         total_time=total_time)

@app.route('/quiz_result')
@login_required
def quiz_result():
    if 'quiz_settings' not in session or 'questions' not in session:
        flash('没有找到练习记录。', 'warning')
        return redirect(url_for('quiz_settings'))
    
    settings = session['quiz_settings']
    questions = session['questions']
    total_time = int(time.time() - session['start_time'])
    correct_count = session.get('correct_count', 0)
    
    # 计算分数（每题10分）
    score = correct_count * 10
    
    # 保存练习记录到数据库
    quiz_record = QuizRecord(
        user_id=current_user.id,
        difficulty=settings['difficulty'],
        operation_type=settings['operation_type'],
        total_questions=len(questions),
        correct_answers=correct_count,
        score=score,
        time_spent=total_time
    )
    db.session.add(quiz_record)
    db.session.flush()  # 获取ID
    
    # 保存每道题的详细信息
    for q in questions:
        question = Question(
            quiz_record_id=quiz_record.id,
            question_text=q['text'],
            correct_answer=q['answer'],
            user_answer=q.get('user_answer'),
            is_correct=q.get('is_correct', False),
            time_spent=q.get('time_spent', 0)
        )
        db.session.add(question)
    
    db.session.commit()
    
    # 清除session中的练习数据
    for key in ['quiz_settings', 'current_question', 'correct_count', 'questions', 'start_time']:
        session.pop(key, None)
    
    return render_template('quiz_result.html', quiz_record=quiz_record)

@app.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    pagination = QuizRecord.query.filter_by(user_id=current_user.id)\
                                 .order_by(QuizRecord.created_at.desc())\
                                 .paginate(page=page, per_page=per_page, error_out=False)
    
    quiz_records = pagination.items
    
    return render_template('history.html', 
                         quiz_records=quiz_records, 
                         pagination=pagination)

@app.route('/quiz_detail/<int:record_id>')
@login_required
def quiz_detail(record_id):
    quiz_record = QuizRecord.query.filter_by(id=record_id, user_id=current_user.id).first_or_404()
    return render_template('quiz_result.html', quiz_record=quiz_record)

@app.route('/statistics')
@login_required
def statistics():
    # 获取用户的所有练习记录
    records = QuizRecord.query.filter_by(user_id=current_user.id).all()
    
    if not records:
        stats = {
            'total_score': 0,
            'total_quizzes': 0,
            'overall_accuracy': 0,
            'total_time': 0,
            'by_difficulty': {},
            'by_operation': {},
            'recent_records': {}
        }
        return render_template('statistics.html', stats=stats)
    
    # 基本统计
    total_score = sum(r.score for r in records)
    total_quizzes = len(records)
    total_questions = sum(r.total_questions for r in records)
    total_correct = sum(r.correct_answers for r in records)
    overall_accuracy = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0
    total_time = sum(r.time_spent for r in records)
    
    # 按难度统计
    by_difficulty = defaultdict(lambda: {'count': 0, 'correct': 0, 'total': 0, 'score': 0})
    for record in records:
        by_difficulty[record.difficulty]['count'] += 1
        by_difficulty[record.difficulty]['correct'] += record.correct_answers
        by_difficulty[record.difficulty]['total'] += record.total_questions
        by_difficulty[record.difficulty]['score'] += record.score
    
    for difficulty in by_difficulty:
        data = by_difficulty[difficulty]
        data['accuracy'] = round((data['correct'] / data['total']) * 100, 2) if data['total'] > 0 else 0
        data['avg_score'] = round(data['score'] / data['count'], 1) if data['count'] > 0 else 0
    
    # 按运算类型统计
    by_operation = defaultdict(lambda: {'count': 0, 'correct': 0, 'total': 0, 'score': 0})
    for record in records:
        by_operation[record.operation_type]['count'] += 1
        by_operation[record.operation_type]['correct'] += record.correct_answers
        by_operation[record.operation_type]['total'] += record.total_questions
        by_operation[record.operation_type]['score'] += record.score
    
    for operation in by_operation:
        data = by_operation[operation]
        data['accuracy'] = round((data['correct'] / data['total']) * 100, 2) if data['total'] > 0 else 0
        data['avg_score'] = round(data['score'] / data['count'], 1) if data['count'] > 0 else 0
    
    # 最近7天的练习记录
    recent_records = {}
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_records = [r for r in records if r.created_at.strftime('%Y-%m-%d') == date]
        if day_records:
            total_correct_day = sum(r.correct_answers for r in day_records)
            total_questions_day = sum(r.total_questions for r in day_records)
            recent_records[date] = {
                'count': len(day_records),
                'accuracy': round((total_correct_day / total_questions_day) * 100, 2) if total_questions_day > 0 else 0,
                'total_score': sum(r.score for r in day_records)
            }
    
    stats = {
        'total_score': total_score,
        'total_quizzes': total_quizzes,
        'overall_accuracy': overall_accuracy,
        'total_time': total_time,
        'by_difficulty': dict(by_difficulty),
        'by_operation': dict(by_operation),
        'recent_records': recent_records
    }
    
    return render_template('statistics.html', stats=stats)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=12000, debug=True)