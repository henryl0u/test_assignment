from flask import Flask
import config
from database import db
from routes import bp

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)
app.register_blueprint(bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
