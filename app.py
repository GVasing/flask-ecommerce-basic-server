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

@app.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped.")

@app.cli.command("seed")
def seed_tables():
    # Create an instance of products
    product1 = Product(
        name = "Product 1",
        description = "This is product 1",
        price = 12.99,
        stock = 5
    )

    product2 = Product()
    product2.name = "Product 2"
    product2.price = 15
    product2.stock = 0

    # Just like git operations, we must add and commit to the session
    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()

    print("Tables seeded.")