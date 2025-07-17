import pytest
from app import app, db

@pytest.fixture
def client():
    # Configure our app for testing
    app.config["TESTING"] = True
    app.config["SQLACLHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()