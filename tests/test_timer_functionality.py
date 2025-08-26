#!/usr/bin/env python3
"""
Simple tests for Pomodoro Timer functionality
Tests the Flask app routing and basic functionality
"""

import unittest
import sys
import os

# Add the parent directory to the path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestPomodoroApp(unittest.TestCase):
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """Test that the main route returns 200 OK"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_content(self):
        """Test that the index page contains expected elements"""
        response = self.app.get('/')
        data = response.get_data(as_text=True)
        
        # Check for main elements
        self.assertIn('ポモドーロタイマー', data)
        self.assertIn('timer.js', data)
        self.assertIn('style.css', data)
        
        # Check for new customization elements
        self.assertIn('settings-btn', data)
        self.assertIn('settings-panel', data)
        self.assertIn('作業時間:', data)
        self.assertIn('休憩時間:', data)
        self.assertIn('テーマ:', data)
        self.assertIn('サウンド:', data)

    def test_static_files_accessible(self):
        """Test that static files are accessible"""
        # Test CSS
        response = self.app.get('/static/css/style.css')
        self.assertEqual(response.status_code, 200)
        
        # Test JS
        response = self.app.get('/static/js/timer.js')
        self.assertEqual(response.status_code, 200)

    def test_css_contains_themes(self):
        """Test that CSS contains theme classes"""
        response = self.app.get('/static/css/style.css')
        css_content = response.get_data(as_text=True)
        
        self.assertIn('theme-dark', css_content)
        self.assertIn('theme-light', css_content)
        self.assertIn('theme-focus', css_content)

    def test_js_contains_settings(self):
        """Test that JavaScript contains settings functionality"""
        response = self.app.get('/static/js/timer.js')
        js_content = response.get_data(as_text=True)
        
        self.assertIn('settings', js_content)
        self.assertIn('localStorage', js_content)
        self.assertIn('workTime', js_content)
        self.assertIn('breakTime', js_content)
        self.assertIn('theme', js_content)

if __name__ == '__main__':
    unittest.main()