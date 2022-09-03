from crypt import methods
import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r'*':{'origins':'*'}})
    """
    @DONE: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers decorator
    @app.after_request
    def after_request(response): #must return the response object
        response.headers.add("Access-Control-Allow-Headers","Content-Type,Authorization,true")
        #allowed methods from cross domains
        response.headers.add('Access-Control-Allow-Headers','POST,PATCH,GET,DELETE,OPTIONS') 
        return response #must return this to the caller

    """
    @DONE:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')#can add methods=['GET'] but by default it is get
    def get_all_categories():
        categories = Category.query.all()
        cat_count = len(categories) #total number of categories
        available_cat = {} #holds available categories 
        for cat in categories: #loop through categories
            available_cat[cat.id] =cat.type #add element to dictionary, keys are the ids
        return jsonify({ #create and return json object
            'success': True,
            'categories': available_cat,
            'total_categories': cat_count
        })

    #pagination utility
    def paginate(request,results):
        page = request.args.get('page',1,type=int)
        begin =(page -1)*QUESTIONS_PER_PAGE
        stop = begin + QUESTIONS_PER_PAGE
        #format the object into nice string representation
        objects = [obj.format() for obj in results] 
        return objects[begin:stop] #list slicing

    """
    @DONE:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions',methods=['GET'])
    def get_all_questions(): 
        #fetch and order questions in order of creation
        questions = Question.query.order_by(Question.id).all()
        ques_count =len(questions)
        question = paginate(request,questions) 
        if len(question)==0:
            abort(404)#unauthorized action
        for q in questions:
            current_category = q.category
            break
        categories = Category.query.all()
        available_cat ={}
        for cat in categories:
            available_cat[cat.id]=cat.type
        #create json object and return
        return jsonify({
            'success':True,
            'questions':question,
            'current_category':current_category,
            'total_questions':ques_count,
            'categories':available_cat
            
        })
        

    """
    @DONE:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    #delete a question, requires question id to know which to delete
    @app.route('/questions/<int:q_id>',methods=['DELETE'])
    def delete_question(q_id):
        #use a try-catch for exception handling
        try:
            question = Question.query.filter(Question.id==q_id).one_or_none()
            #check if a question with specified id was found
            if question is None:
                abort(404) #can't delete question that does not exist
            question.delete() #remove the question from the system
            return jsonify({
                'success':True,
                'deleted':q_id,
                'message':'Question successfully deleted!'
            })
        except Exception as e:
            abort(422) #action forbidden
    

    """
    @DONE:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions',methods=['POST'])
    def create_question():
        data = request.get_json()
        #extract attributes from the data
        q = data.get('question', None)
        ans= data.get('answer', None) 
        dificulty = data.get('difficulty', None)
        cat = data.get('category', None)

        try: #attempt creating a new question
            question = Question(question=q,answer=ans,difficulty=dificulty,category=cat)
            question.insert()#persist the object
            questions = Question.query.order_by(Question.id).all()
            q_count = len(questions)
            paginated_questions =paginate(request,questions)
            return jsonify({
                'success':True,
                'questions':paginated_questions,
                'total_question':q_count,
                'created':question.id #get the id of the newly created question
            })
        except Exception as e:
            abort(403) #not allowed
    """
    @DONE:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/search',methods=['POST'])
    def find_question():
        data = request.get_json() #extract data from the post
        key_word = data.get('searchTerm')
        questions = Question.query.filter(Question.question.ilike('%' \
            +key_word + '%'
            )).all()#used wildcard expression to search
        q_count = len(questions)
        if q_count>0:
            paginated_questions = paginate(request,questions)
            return jsonify({
                'success':True,
                'total_questions':q_count,
                'questions':paginated_questions,
                
            })
        else:
            abort(405) #one could use redirect here to go back to the original page


    """
    @DONE:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions',methods=['GET'])
    def get_questions_by_category(category_id):
        #fetch the category 
        questions = Question.query.filter_by(category=category_id).all()
        q_count = len(questions)
        if q_count>0:
            cat =Category.query.filter_by(id=category_id).one_or_none()
            paginated_questions = paginate(request,questions)
            return jsonify({
                'success':True,
                'total_questions':q_count,
                'questions':paginated_questions,
                'total_questions':q_count,
                'current_category':cat.type
                
            })
        else:
            abort(405) #one could use redirect here to go back to the original page



    """
    @DONE:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes',methods=['POST'])
    def begin_quiz():
        data = request.get_json()
               # Store ids previous questions
        previous_questions = data.get('previous_questions')
        category = data.get('quiz_category')
 
        if (previous_questions is None) or (category is None):
            abort(400)
        try:
            
            if (category['id'] == 0): # no category specified so get all questions
                questions = Question.query.all()
                formatted_questions = [q.format() for q in questions]
               
            else:
                # fetch questions for specific category
                questions = Question.query.filter_by(category=category['id']).all()
                formatted_questions = [q.format() for q in questions]

            q_count = len(formatted_questions)
            # random question
            rand = random.randrange(0, q_count, 1)
            for q in formatted_questions:
                if q['id'] not in previous_questions:
                    question_collection = formatted_questions[rand]
            if (len(previous_questions) == q_count):
                return jsonify({"success":True})
            else:
                return jsonify ({
                            "success": True,
                            "question": question_collection})
            
        except Exception as e:
            abort(404)


    """
    @DONE:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(405)
    def unsuccessful(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Unauthorized request"
        }), 405
    
    @app.errorhandler(404)
    def resource_not_found(error):
        return jsonify({
            'success': False,
            'error': '404',
            'message': 'Resource not Found'
        }), 404

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
            }), 400
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': '422',
            'message': 'Unprocessable'
        }), 422


    return app

