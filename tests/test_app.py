import unittest
import tempfile
import os
from app import create_app
from models import db, User, QuizRecord
from config import config


class TestApp(unittest.TestCase):
    
    def setUp(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()
        
        # 创建测试用户
        self.test_user = User(username='testuser', email='test@example.com')
        self.test_user.set_password('testpass')
        db.session.add(self.test_user)
        db.session.commit()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_index_page(self):
        """测试首页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('口算练习'.encode('utf-8'), response.data)
    
    def test_login_page(self):
        """测试登录页面"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('登录'.encode('utf-8'), response.data)
    
    def test_register_page(self):
        """测试注册页面"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn('注册'.encode('utf-8'), response.data)
    
    def test_user_registration(self):
        """测试用户注册"""
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass',
            'password2': 'newpass'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        # 检查用户是否创建成功
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')
    
    def test_user_login(self):
        """测试用户登录"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('欢迎回来'.encode('utf-8'), response.data)
    
    def test_login_required_pages(self):
        """测试需要登录的页面"""
        # 未登录时访问需要登录的页面应该重定向到登录页
        protected_urls = ['/quiz_settings', '/history', '/statistics', '/leaderboard']
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login', response.location)
    
    def test_api_leaderboard_unauthorized(self):
        """测试未授权访问API"""
        response = self.client.get('/api/leaderboard')
        self.assertEqual(response.status_code, 302)
    
    def test_404_error(self):
        """测试404错误页面"""
        response = self.client.get('/nonexistent')
        self.assertEqual(response.status_code, 404)
    
    def login_user(self):
        """辅助方法：登录测试用户"""
        return self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass'
        }, follow_redirects=True)
    
    def test_quiz_settings_authenticated(self):
        """测试已登录用户访问练习设置"""
        self.login_user()
        response = self.client.get('/quiz_settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn('练习设置'.encode('utf-8'), response.data)
    
    def test_statistics_authenticated(self):
        """测试已登录用户访问统计页面"""
        self.login_user()
        response = self.client.get('/statistics')
        self.assertEqual(response.status_code, 200)
    
    def test_export_data_authenticated(self):
        """测试数据导出功能"""
        self.login_user()
        response = self.client.get('/export_data')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')


if __name__ == '__main__':
    unittest.main()