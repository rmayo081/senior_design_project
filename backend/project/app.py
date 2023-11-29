from flask import Flask, request, g
from Data_model.helpers import create
from Data_model.models import db, Period, PeriodEnum, Subject, Administrator, Role, RoleEnum, Theme
import Data_model.init_db
from flask_principal import Principal, identity_loaded, Identity, RoleNeed, identity_changed
from pathlib import Path
import os

def get_database_uri():
    return 'mysql+pymysql://root:my_root_password@database/my_database'

def load_user():
    unityId = request.environ.get('HTTP_X_SHIB_UID')

    if unityId == None:
        return None

    user = Administrator.query.filter_by(unity_id=unityId).first()
    return user if user else create(db.session, Administrator, unity_id=unityId, role_id=Role.query.filter_by(role=RoleEnum.UNAUTHORIZED).first().id)

def before_request():
    g.user: Administrator | None = load_user()

    if g.user:
        identity = Identity(g.user.unity_id)
        identity_changed.send(app, identity=identity)


def create_app(database_uri=get_database_uri()):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri or "sqlite:///:memory:"
    app.secret_key = "SECRERT_KEY"
    
    DIR = Path(__file__, "..").resolve()
    IMAGE_PATH = DIR.joinpath("image_uploads/")
    
    if not os.path.exists(IMAGE_PATH):
        IMAGE_PATH.mkdir()

    db.init_app(app)

    
    
    with app.app_context():
        db.create_all()

                
        
    from Controllers.api_controller import api
    app.before_request(before_request)
    app.register_blueprint(api)

    return app

app = create_app()
principal = Principal(app)

@identity_loaded.connect_via(app)
def on_identity_loaded(_: Flask, identity: Identity):
    if g.user:
        identity.provides.add(RoleNeed(g.user.role.role))
           

if __name__=='__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

