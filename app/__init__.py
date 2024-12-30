from flask import Flask
from .extension import db
from .models import Item, User
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db
from flask_restful import Api, Resource, reqparse
import os


def create_app():
    app = Flask(__name__)

    app.secret_key = os.urandom(24)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    with app.app_context():
        print("creating all tables...")
        db.create_all()
        print("all tables created.")
        print(app.url_map)

    from .routes import main  
    app.register_blueprint(main)  

    api = Api(app)

    from flask_restful import reqparse
    parser = reqparse.RequestParser()
    parser.add_argument('name', required=True)
    parser.add_argument('description', required=True)

    class ItemResource(Resource):
        def get(self, item_id):
            item = Item.query.get(item_id)
            if item:
                return {'id': item.id, 'name': item.name, 'description': item.description}
            return {'message': 'Item Not Found'}, 404
        
        def post(self, item_id):
            args = parser.parse_args()
            new_item = Item(name=args['name'], description=args['description'])
            db.session.add(new_item)
            db.session.commit
            return {'message': 'Item created', 'id': new_item.id}, 201
        
    api.add_resource(ItemResource, '/api/items', '/api/items/<int:item_id>')

    return app  