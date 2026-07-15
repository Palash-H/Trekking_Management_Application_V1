from flask import Flask
from werkzeug.security import generate_password_hash
from models import db,Admin
from flask_migrate import Migrate

app = Flask(__name__,template_folder="templates")

import config 
import models
app.config.from_object(config)

migrate = Migrate()
db.init_app(app)
migrate.init_app(app,db)
from routes import main_bp
app.register_blueprint(main_bp)
with app.app_context():
    # db.create_all()

    admin = models.Admin.query.filter_by(email='admin@gmail.com').first()

    if not admin:
        admin = models.Admin(
            name='Admin',
            email='admin@gmail.com',
            passhash='admin123'
        )

        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)