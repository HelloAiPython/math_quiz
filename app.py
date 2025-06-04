from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, QuizRecord, Question
from forms import LoginForm, RegisterForm, QuizSettingsForm, AnswerForm
from config import config
from utils import generate_question, calculate_statistics, format_time, validate_quiz_settings
import time
import logging
from datetime import datetime

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = '请先登录以访问此页面。'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 错误处理装饰器
    def handle_errors(f):
        """错误处理装饰器"""
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {f.__name__}: {str(e)}")
                flash('发生了一个错误，请稍后重试。', 'error')
                return redirect(url_for('index'))
        wrapper.__name__ = f.__name__
        return wrapper
    
    # 路由定义
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
            # 验证设置
            if not validate_quiz_settings(form.operation.data, form.difficulty.data, form.question_count.data):
                flash('练习设置无效，请检查输入。', 'error')
                return render_template('quiz_settings.html', form=form)
            
            # 保存设置到session
            session['quiz_settings'] = {
                'operation': form.operation.data,
                'difficulty': form.difficulty.data,
                'question_count': form.question_count.data
            }
            return redirect(url_for('quiz'))
        
        return render_template('quiz_settings.html', form=form)

    @app.route('/quiz')
    @login_required
    def quiz():
        # 检查是否有练习设置
        if 'quiz_settings' not in session:
            flash('请先设置练习参数。', 'warning')
            return redirect(url_for('quiz_settings'))
        
        settings = session['quiz_settings']
        
        # 初始化练习会话
        if 'current_quiz' not in session:
            session['current_quiz'] = {
                'questions': [],
                'answers': [],
                'start_time': time.time(),
                'current_question': 0
            }
            
            # 生成题目
            for _ in range(settings['question_count']):
                question = generate_question(settings['operation'], settings['difficulty'])
                session['current_quiz']['questions'].append(question)
        
        current_quiz = session['current_quiz']
        current_q_index = current_quiz['current_question']
        
        # 检查是否完成所有题目
        if current_q_index >= len(current_quiz['questions']):
            return redirect(url_for('quiz_result'))
        
        current_question = current_quiz['questions'][current_q_index]
        form = AnswerForm()
        
        return render_template('quiz.html', 
                             question=current_question,
                             question_number=current_q_index + 1,
                             total_questions=len(current_quiz['questions']),
                             form=form)

    @app.route('/submit_answer', methods=['POST'])
    @login_required
    def submit_answer():
        if 'current_quiz' not in session:
            flash('练习会话已过期，请重新开始。', 'error')
            return redirect(url_for('quiz_settings'))
        
        form = AnswerForm()
        if form.validate_on_submit():
            current_quiz = session['current_quiz']
            current_q_index = current_quiz['current_question']
            
            if current_q_index < len(current_quiz['questions']):
                # 记录答案
                current_quiz['answers'].append({
                    'answer': form.answer.data,
                    'time': time.time()
                })
                
                # 移动到下一题
                current_quiz['current_question'] += 1
                session['current_quiz'] = current_quiz
        
        return redirect(url_for('quiz'))

    @app.route('/quiz_result')
    @login_required
    def quiz_result():
        if 'current_quiz' not in session:
            flash('没有找到练习记录。', 'error')
            return redirect(url_for('quiz_settings'))
        
        current_quiz = session['current_quiz']
        questions = current_quiz['questions']
        answers = current_quiz['answers']
        
        # 计算结果
        correct_count = 0
        total_time = time.time() - current_quiz['start_time']
        
        results = []
        for i, (question, answer_data) in enumerate(zip(questions, answers)):
            user_answer = answer_data['answer']
            correct_answer = question['answer']
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            results.append({
                'question': question,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct
            })
        
        # 保存记录到数据库
        quiz_record = QuizRecord(
            user_id=current_user.id,
            operation=session['quiz_settings']['operation'],
            difficulty=session['quiz_settings']['difficulty'],
            total_questions=len(questions),
            correct_answers=correct_count,
            total_time=int(total_time),
            score=round((correct_count / len(questions)) * 100, 2)
        )
        db.session.add(quiz_record)
        db.session.commit()
        
        # 清除会话数据
        session.pop('current_quiz', None)
        session.pop('quiz_settings', None)
        
        return render_template('quiz_result.html',
                             results=results,
                             correct_count=correct_count,
                             total_questions=len(questions),
                             total_time=format_time(total_time),
                             score=quiz_record.score)

    @app.route('/history')
    @login_required
    def history():
        page = request.args.get('page', 1, type=int)
        records = QuizRecord.query.filter_by(user_id=current_user.id)\
                                 .order_by(QuizRecord.created_at.desc())\
                                 .paginate(page=page, per_page=10, error_out=False)
        return render_template('history.html', records=records)

    @app.route('/statistics')
    @login_required
    def statistics():
        records = QuizRecord.query.filter_by(user_id=current_user.id).all()
        stats = calculate_statistics(records)
        return render_template('statistics.html', stats=stats)

    @app.route('/leaderboard')
    @login_required
    def leaderboard():
        # 获取排行榜数据
        top_users = db.session.query(
            User.username,
            db.func.avg(QuizRecord.score).label('avg_score'),
            db.func.count(QuizRecord.id).label('total_quizzes')
        ).join(QuizRecord).group_by(User.id)\
         .order_by(db.func.avg(QuizRecord.score).desc())\
         .limit(10).all()
        
        return render_template('leaderboard.html', top_users=top_users)

    # API路由
    @app.route('/api/leaderboard')
    @login_required
    def api_leaderboard():
        top_users = db.session.query(
            User.username,
            db.func.avg(QuizRecord.score).label('avg_score'),
            db.func.count(QuizRecord.id).label('total_quizzes')
        ).join(QuizRecord).group_by(User.id)\
         .order_by(db.func.avg(QuizRecord.score).desc())\
         .limit(10).all()
        
        return jsonify([{
            'username': user.username,
            'avg_score': round(user.avg_score, 2),
            'total_quizzes': user.total_quizzes
        } for user in top_users])

    @app.route('/export_data')
    @login_required
    def export_data():
        records = QuizRecord.query.filter_by(user_id=current_user.id).all()
        
        # 生成CSV数据
        import io
        import csv
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入标题行
        writer.writerow(['日期', '运算类型', '难度', '总题数', '正确数', '用时(秒)', '得分'])
        
        # 写入数据行
        for record in records:
            writer.writerow([
                record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                record.operation,
                record.difficulty,
                record.total_questions,
                record.correct_answers,
                record.total_time,
                record.score
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=quiz_history.csv'}
        )

    # 错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    return app

# 创建应用实例
import os
config_name = os.environ.get('FLASK_ENV', 'default')
app = create_app(config_name)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)