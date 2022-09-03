import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_USER, DB_PASSWORD

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://{}:{}@{}/{}'.format(DB_USER\
        ,DB_PASSWORD,'localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context(): 
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_new_question(self): 
        question = {
            'question': 'Where was Obama born?',
            'answer': 'Kenya',
            'difficulty': '1',
            'category': '2'
        }
        result = self.client().post('/questions', json=question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
    def test_unable_to_create_question(self):
        test_question = {
                    "question": "What is the capital of Italy?",
                    "answer": "Rome",
                    "category": "4",
                    "difficulty": "1"
                }
        result = self.client().post('/questions/3', json=test_question)
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unauthorized request")

    def test_search(self):
        search = {'searchTerm': 'Which'}
        res = self.client().post('/search', json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["questions"])

    def test_search_failed(self): 
        keyword = {'searchTerm': 'keyword'}
        results = self.client().post('/search', json=keyword)
        data = json.loads(results.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(results.status_code, 405)
        
    def test_begin_quiz(self):
        quiz_question = {'previous_questions': [],'quiz_category': {
                'type': 'Science',
                'id': 1}
        }
        results = self.client().post('/quizzes', json=quiz_question)
        data = json.loads(results.data)
        self.assertEqual(results.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question']['category'], 1)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['id'], 20)

    def test_404_page_not_found(self):
        result = self.client().get('/questions?page=100')
        data = json.loads(result.data)

        self.assertEqual(result.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], 'Resource not Found')

    def test_question_does_not_exist(self):
        result = self.client().delete('/questions/200')
        data = json.loads(result.data)
        #data ={}
        self.assertEqual(result.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Unprocessable")

    def test_404_begin_quiz(self):
        question = {'previous_questions': [9],
            'quiz_category': {
                'type': 'Sports',
                'id': '9'}
        }
        result = self.client().post('/quizzes', json=question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 404)
        self.assertEqual(data['success'], False)
    

    def test_begin_quiz(self):
        quiz_question = {'previous_questions': [],'quiz_category': {
                'type': 'Sports',
                'id': 6}
        }
        res = self.client().post('/quizzes', json=quiz_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

        self.assertEqual(data['question']['category'], 6)
        self.assertEqual(data['question']['id'], 10)
      

    def test_paginate_questions(self):
        result = self.client().get('/questions')
        data = json.loads(result.data)
        self.assertTrue(data["categories"])
        self.assertTrue(data["questions"])
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)

        
    def test_delete_question(self):
        result = self.client().delete('/questions/5')
        data = json.loads(result.data)
        self.assertEqual(data["deleted"], 5)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_fetch_categories(self): 
        results = self.client().get('/categories')
        data = json.loads(results.data)
        self.assertEqual(results.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()