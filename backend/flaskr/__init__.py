import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from sqlalchemy.sql.expression import true

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginated_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # Set up cors
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    # @TODO: Use the after_request decorator to set Access-Control-Allow

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'POST, GET, PUT, PATCH, DELETE, OPTIONS')
        return response

# @TODO:Create an endpoint to GET requests for all available categories.

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            formated_categories = {}
            for category in categories:
                formated_categories[category.id] = category.type
            return jsonify({
                'success': True,
                'categories': formated_categories,
                'total_categories': len(formated_categories)
            })
        except:
            abort(500)

    # @TODO: Create an endpoint to handle GET requests for questions

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginated_questions(request, selection)
            categories = Category.query.all()
            formated_categories = {}
            for category in categories:
                formated_categories[category.id] = category.type

            if (len(current_questions) == 0):
                abort(404)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories': formated_categories

            })
        except BaseException:
            abort(500)

    #  @TODO: Create an endpoint to DELETE question using a question ID.

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        question = Question.query.filter_by(id=id).one_or_none()

        if question is None:
            abort(404)
        else:
            try:
                question.delete()

                return jsonify({
                    'success': True,
                    'deleted': id
                })
            except BaseException:
                abort(422)

    # @TODO: Create an endpoint to POST a new question.

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        if not ('question' in body or 'answer' in body or 'difficulty' in
                body or 'category' in body):
            abort(422)

        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')

        if ((new_question is None) and (new_answer is None) and
                (new_category is None) and (new_difficulty is None)):
            abort(422)

        else:
            try:
                question = Question(question=new_question, answer=new_answer,
                                    category=new_category,
                                    difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginated_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(selection)

                })

            except BaseException:
                abort(422)

    # @TODO: Create a POST endpoint to get questions based on a search term.

    @app.route('/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        searchTerm = body.get('searchTerm')
        selection = Question.query.filter(
            Question.question.ilike('%' + searchTerm + '%')).all()

        if selection == []:
            abort(404)
        else:
            current_questions = paginated_questions(request, selection)
            return jsonify(
                {
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection)
                }
            )

    # @TODO:Create a GET endpoint to get questions based on category.

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def questions_by_category(category_id):
        category = Category.query.get(category_id)
        if category is None:
            abort(404)
        else:
            selection = Question.query.filter_by(category=category_id).all()
            current_questions = paginated_questions(request, selection)
            return jsonify({
                'success': True,
                'questions': current_questions,
                'current_category': category.type,
                'total_questions': len(selection)

            }
            )

    # @TODO: Create a POST endpoint to get questions to play the quiz.

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        body = request.get_json(force=True)
        quiz_category = body.get('quiz_category')
        prev_questions = body.get('previous_questions')

        if (quiz_category['id'] == '0'):
            questions = Question.query.filter(
                Question.id not in prev_questions).all()
        else:
            questions = Question.query.filter(
                Question.id not in prev_questions,
                Question.category == quiz_category['id']).all()

        next_question = random.choice(questions)

        return jsonify({
            'success': True,
            'question': {
                "id": next_question.id,
                "question": next_question.question,
                "difficulty": next_question.difficulty,
                "category": next_question.category,
                "answer": next_question.answer
            },
            'previous_question': prev_questions,
        }
        )

    # @TODO:Create error handlers

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Invalid Method"
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
