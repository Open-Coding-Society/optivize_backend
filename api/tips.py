from flask import Blueprint, jsonify
from flask_restful import Api, Resource

# Set up the Blueprint
tips_api = Blueprint('tips_api', __name__, url_prefix='/api')

api = Api(tips_api)

# Static data for tips and tricks
class TipsAPI:
    @staticmethod
    def get_tips(class_name):
        tips = {
            "AP Physics": [
                "Understand the core concepts before solving problems.",
                "Practice solving past exam questions regularly.",
                "Use diagrams to visualize problems."
            ],
            "AP Chemistry": [
                "Memorize periodic trends and key reactions.",
                "Practice balancing chemical equations.",
                "Understand stoichiometry thoroughly."
            ],
            "AP CSP": [
                "Learn Python basics thoroughly.",
                "Use online tools to practice coding concepts.",
                "Understand binary systems and algorithms."
            ],
            "AP Statistics": [
                "Understand data visualization techniques.",
                "Practice calculating probabilities.",
                "Master regression and correlation concepts."
            ]
        }
        return tips.get(class_name)

# Resource for each class
class PhysicsResource(Resource):
    def get(self):
        tips = TipsAPI.get_tips("AP Physics")
        if tips:
            return jsonify({"class_name": "AP Physics", "tips": tips})
        return {"message": "No tips found for AP Physics"}, 404

class ChemistryResource(Resource):
    def get(self):
        tips = TipsAPI.get_tips("AP Chemistry")
        if tips:
            return jsonify({"class_name": "AP Chemistry", "tips": tips})
        return {"message": "No tips found for AP Chemistry"}, 404

class CSPResource(Resource):
    def get(self):
        tips = TipsAPI.get_tips("AP CSP")
        if tips:
            return jsonify({"class_name": "AP CSP", "tips": tips})
        return {"message": "No tips found for AP CSP"}, 404

class StatisticsResource(Resource):
    def get(self):
        tips = TipsAPI.get_tips("AP Statistics")
        if tips:
            return jsonify({"class_name": "AP Statistics", "tips": tips})
        return {"message": "No tips found for AP Statistics"}, 404

# Add routes for each class
api.add_resource(PhysicsResource, '/tips/Physics')       # /api/tips/Physics
api.add_resource(ChemistryResource, '/tips/Chemistry')   # /api/tips/Chemistry
api.add_resource(CSPResource, '/tips/CSP')              # /api/tips/CSP
api.add_resource(StatisticsResource, '/tips/Statistics') # /api/tips/Statistics