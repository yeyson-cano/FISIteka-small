from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Nombre de la vista de inicio de sesión

from app import models, views

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

# Importa la función can_edit_resource para que esté disponible en el contexto global
from app.views import can_edit_resource
app.jinja_env.globals.update(can_edit_resource=can_edit_resource)