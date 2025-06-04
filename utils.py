"""
工具函数模块
"""
import random
from typing import Tuple, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict


def generate_question(difficulty: str, operation_type: str) -> Tuple[str, int]:
    """
    根据难度和运算类型生成题目
    
    Args:
        difficulty: 难度等级 (easy, medium, hard)
        operation_type: 运算类型 (add, subtract, multiply, divide, mixed)
    
    Returns:
        Tuple[str, int]: (题目文本, 正确答案)
    """
    # 根据难度设置数字范围
    if difficulty == 'easy':
        min_num, max_num = 1, 20
    elif difficulty == 'medium':
        min_num, max_num = 1, 100
    else:  # hard
        min_num, max_num = 1, 1000
    
    # 如果是混合模式，随机选择运算类型
    if operation_type == 'mixed':
        operation_type = random.choice(['add', 'subtract', 'multiply', 'divide'])
    
    if operation_type == 'add':
        return _generate_addition(min_num, max_num)
    elif operation_type == 'subtract':
        return _generate_subtraction(min_num, max_num)
    elif operation_type == 'multiply':
        return _generate_multiplication(difficulty)
    elif operation_type == 'divide':
        return _generate_division(difficulty)
    else:
        raise ValueError(f"不支持的运算类型: {operation_type}")


def _generate_addition(min_num: int, max_num: int) -> Tuple[str, int]:
    """生成加法题目"""
    a = random.randint(min_num, max_num)
    b = random.randint(min_num, max_num)
    question = f"{a} + {b} = ?"
    answer = a + b
    return question, answer


def _generate_subtraction(min_num: int, max_num: int) -> Tuple[str, int]:
    """生成减法题目"""
    a = random.randint(min_num, max_num)
    b = random.randint(min_num, a)  # 确保结果为正数
    question = f"{a} - {b} = ?"
    answer = a - b
    return question, answer


def _generate_multiplication(difficulty: str) -> Tuple[str, int]:
    """生成乘法题目"""
    if difficulty == 'easy':
        a = random.randint(1, 10)
        b = random.randint(1, 10)
    elif difficulty == 'medium':
        a = random.randint(1, 20)
        b = random.randint(1, 20)
    else:  # hard
        a = random.randint(1, 50)
        b = random.randint(1, 50)
    
    question = f"{a} × {b} = ?"
    answer = a * b
    return question, answer


def _generate_division(difficulty: str) -> Tuple[str, int]:
    """生成除法题目"""
    if difficulty == 'easy':
        b = random.randint(1, 10)
        answer = random.randint(1, 10)
    elif difficulty == 'medium':
        b = random.randint(1, 20)
        answer = random.randint(1, 20)
    else:  # hard
        b = random.randint(1, 50)
        answer = random.randint(1, 50)
    
    a = b * answer  # 确保整除
    question = f"{a} ÷ {b} = ?"
    return question, answer


def calculate_statistics(records) -> Dict[str, Any]:
    """
    计算用户统计信息
    
    Args:
        records: 用户的练习记录列表
    
    Returns:
        Dict: 统计信息字典
    """
    if not records:
        return {
            'total_score': 0,
            'total_quizzes': 0,
            'overall_accuracy': 0,
            'total_time': 0,
            'by_difficulty': {},
            'by_operation': {},
            'recent_records': {}
        }
    
    # 基本统计
    total_score = sum(r.score for r in records)
    total_quizzes = len(records)
    total_questions = sum(r.total_questions for r in records)
    total_correct = sum(r.correct_answers for r in records)
    overall_accuracy = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0
    total_time = sum(r.time_spent for r in records)
    
    # 按难度统计
    by_difficulty = _calculate_by_category(records, 'difficulty')
    
    # 按运算类型统计
    by_operation = _calculate_by_category(records, 'operation_type')
    
    # 最近7天的练习记录
    recent_records = _calculate_recent_records(records)
    
    return {
        'total_score': total_score,
        'total_quizzes': total_quizzes,
        'overall_accuracy': overall_accuracy,
        'total_time': total_time,
        'by_difficulty': dict(by_difficulty),
        'by_operation': dict(by_operation),
        'recent_records': recent_records
    }


def _calculate_by_category(records, category_field: str) -> defaultdict:
    """按指定字段分类统计"""
    by_category = defaultdict(lambda: {'count': 0, 'correct': 0, 'total': 0, 'score': 0})
    
    for record in records:
        category = getattr(record, category_field)
        by_category[category]['count'] += 1
        by_category[category]['correct'] += record.correct_answers
        by_category[category]['total'] += record.total_questions
        by_category[category]['score'] += record.score
    
    # 计算准确率和平均分
    for category in by_category:
        data = by_category[category]
        data['accuracy'] = round((data['correct'] / data['total']) * 100, 2) if data['total'] > 0 else 0
        data['avg_score'] = round(data['score'] / data['count'], 1) if data['count'] > 0 else 0
    
    return by_category


def _calculate_recent_records(records) -> Dict[str, Dict]:
    """计算最近7天的练习记录"""
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
    
    return recent_records


def format_time(seconds: int) -> str:
    """
    格式化时间显示
    
    Args:
        seconds: 秒数
    
    Returns:
        str: 格式化后的时间字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}分{remaining_seconds}秒"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"


def get_difficulty_display(difficulty: str) -> str:
    """获取难度的中文显示名称"""
    difficulty_map = {
        'easy': '简单',
        'medium': '中等',
        'hard': '困难'
    }
    return difficulty_map.get(difficulty, difficulty)


def get_operation_display(operation_type: str) -> str:
    """获取运算类型的中文显示名称"""
    operation_map = {
        'add': '加法',
        'subtract': '减法',
        'multiply': '乘法',
        'divide': '除法',
        'mixed': '混合运算'
    }
    return operation_map.get(operation_type, operation_type)


def validate_quiz_settings(difficulty: str, operation_type: str, question_count: int) -> bool:
    """
    验证练习设置参数
    
    Args:
        difficulty: 难度等级
        operation_type: 运算类型
        question_count: 题目数量
    
    Returns:
        bool: 是否有效
    """
    valid_difficulties = ['easy', 'medium', 'hard']
    valid_operations = ['add', 'subtract', 'multiply', 'divide', 'mixed']
    
    return (
        difficulty in valid_difficulties and
        operation_type in valid_operations and
        1 <= question_count <= 50
    )