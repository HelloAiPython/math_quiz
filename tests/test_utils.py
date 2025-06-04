import unittest
from utils import (
    generate_question, 
    calculate_statistics, 
    format_time, 
    validate_quiz_settings,
    get_difficulty_display,
    get_operation_display
)


class TestUtils(unittest.TestCase):
    
    def test_generate_question_addition(self):
        """测试加法题目生成"""
        question, answer = generate_question('easy', 'add')
        self.assertIn('+', question)
        self.assertIn('=', question)
        self.assertIsInstance(answer, int)
        self.assertGreater(answer, 0)
    
    def test_generate_question_subtraction(self):
        """测试减法题目生成"""
        question, answer = generate_question('easy', 'subtract')
        self.assertIn('-', question)
        self.assertIn('=', question)
        self.assertIsInstance(answer, int)
        self.assertGreaterEqual(answer, 0)  # 结果应该非负
    
    def test_generate_question_multiplication(self):
        """测试乘法题目生成"""
        question, answer = generate_question('easy', 'multiply')
        self.assertIn('×', question)
        self.assertIn('=', question)
        self.assertIsInstance(answer, int)
        self.assertGreater(answer, 0)
    
    def test_generate_question_division(self):
        """测试除法题目生成"""
        question, answer = generate_question('easy', 'divide')
        self.assertIn('÷', question)
        self.assertIn('=', question)
        self.assertIsInstance(answer, int)
        self.assertGreater(answer, 0)
    
    def test_generate_question_mixed(self):
        """测试混合运算题目生成"""
        question, answer = generate_question('easy', 'mixed')
        self.assertIn('=', question)
        self.assertIsInstance(answer, int)
        # 应该包含四种运算符之一
        operators = ['+', '-', '×', '÷']
        self.assertTrue(any(op in question for op in operators))
    
    def test_format_time(self):
        """测试时间格式化"""
        self.assertEqual(format_time(30), "30秒")
        self.assertEqual(format_time(90), "1分30秒")
        self.assertEqual(format_time(3661), "1小时1分钟")
    
    def test_validate_quiz_settings(self):
        """测试练习设置验证"""
        # 有效设置
        self.assertTrue(validate_quiz_settings('easy', 'add', 10))
        self.assertTrue(validate_quiz_settings('medium', 'mixed', 20))
        
        # 无效设置
        self.assertFalse(validate_quiz_settings('invalid', 'add', 10))
        self.assertFalse(validate_quiz_settings('easy', 'invalid', 10))
        self.assertFalse(validate_quiz_settings('easy', 'add', 0))
        self.assertFalse(validate_quiz_settings('easy', 'add', 100))
    
    def test_get_difficulty_display(self):
        """测试难度显示名称"""
        self.assertEqual(get_difficulty_display('easy'), '简单')
        self.assertEqual(get_difficulty_display('medium'), '中等')
        self.assertEqual(get_difficulty_display('hard'), '困难')
        self.assertEqual(get_difficulty_display('unknown'), 'unknown')
    
    def test_get_operation_display(self):
        """测试运算类型显示名称"""
        self.assertEqual(get_operation_display('add'), '加法')
        self.assertEqual(get_operation_display('subtract'), '减法')
        self.assertEqual(get_operation_display('multiply'), '乘法')
        self.assertEqual(get_operation_display('divide'), '除法')
        self.assertEqual(get_operation_display('mixed'), '混合运算')
        self.assertEqual(get_operation_display('unknown'), 'unknown')
    
    def test_calculate_statistics_empty(self):
        """测试空记录的统计计算"""
        stats = calculate_statistics([])
        expected = {
            'total_score': 0,
            'total_quizzes': 0,
            'overall_accuracy': 0,
            'total_time': 0,
            'by_difficulty': {},
            'by_operation': {},
            'recent_records': {}
        }
        self.assertEqual(stats, expected)


if __name__ == '__main__':
    unittest.main()