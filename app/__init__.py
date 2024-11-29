from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from .models import db

def create_app():
    app = Flask(__name__)

    
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

    return app  