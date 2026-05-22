from flask import Flask
from .controllers.auth_controller import auth_bp
from .controllers.member_controller import member_bp
from .models.db_init import init_db

app = Flask(
    __name__,
    template_folder="views",
    static_folder="static"
)

app.secret_key = "secret123"

# Initialize database
init_db()

# Register controllers
app.register_blueprint(auth_bp)
app.register_blueprint(member_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
