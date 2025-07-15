from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#                                     database+driver+://username:password@server:port/databasename  (URI/URL Structure.)

app.config['SQLALCHEMY_DATABASE_URI']="postgresql+psycopg2://mar_user:123456@localhost:5432/mar_ecommerce"

db = SQLAlchemy(app)

class Product(db.Model):
    # Define table name
    __tablename__ = "products"
    # Define primary key
    id = db.Column(db.Integer, primary_key=True)
    # Define non-key attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

@app.cli.command("create")
def create_table():
    db.create_all()
    print("Tables created.")