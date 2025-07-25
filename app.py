from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


#                                     database+driver+://username:password@server:port/databasename  (URI/URL Structure.)

DATABASE_URI = os.getenv("DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI']= DATABASE_URI

db = SQLAlchemy(app)
ma = Marshmallow(app)

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

    # __init__ function not necessary, as SQLAlchemy automatically initialises it for Marshmallow Schemas

    def __init__(self, name, description, price, stock):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock

class Category(db.Model):
    # Define table name
    __tablename__ = "categories"
    # Define primary key attribute
    id = db.Column(db.Integer, primary_key=True)
    # Define non-key attributes
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255))

    # No __init__ function.  Reason mentioned in previous class/model


# Create a class for ProductSchema
class ProductSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instace = True

# Create a class for CategorySchema
class CategorySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True

# ProductSchema instance to handle multiple products
products_schema = ProductSchema(many=True)

# ProductSchema instance to handle a single product
product_schema = ProductSchema()

# CategorySchema instance to handle multiple Categories
categories_schema = CategorySchema(many=True)

# CategorySchema instance to handle a single Category
category_schema = CategorySchema()

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

    product2 = Product(
        name = "Product 2",
        description= "This is product 2",
        price = 15,
        stock = 0
    )

    # Just like git operations, we must add the session
    db.session.add(product1)
    db.session.add(product2)

    # Create a list of categories object
    categories = [
        Category(
            name = "Electronics",
            description = "Gadgets and Tech"
        ), Category(
            name = "Books",
            description = "Fiction, Non-Fiction, and everything in between"
        ), Category(
            name = "Supplies"
        )
    ]

    # Add the list to the session
    db.session.add_all(categories)

    # Commit additions.
    db.session.commit()

    print("Tables seeded.")

# CRUD Operations on the Products Tables (GET, POST, PUT, PATCH, DELETE)
# READ Operation - GET Method
# GET /products
@app.route("/products")
def get_products():
    # Statement: SELECT * FROM products;
    stmt = db.select(Product)
    products_list = db.session.scalars(stmt)

    # Convert the object into a JSON format (i.e. Serialise)
    data = products_schema.dump(products_list)
    return jsonify(data)

# READ specific product from the products list
# GET /products/id
@app.route("/products/<int:product_id>")
def get_a_product(product_id):
    # SELECT * FROM products WHERE id = product_id;
    # product = Product.query.get(product_id)
    stmt = db.select(Product).where(Product.id == product_id)
    product = db.session.scalar(stmt)

    if product:
        data = product_schema.dump(product)
        return jsonify(data)
    else:
        return jsonify({"message": f"Product with id {product_id} does not exist."}), 404
    
# CREATE a product
# POST /products
@app.route("/products", methods=["POST"])
def create_product():
    # Statement: INSERT INTO products(arg1, arg2, etc.) VALUES (value1, value2, etc.).
    # Get the body JSON data
    body_data = request.get_json()
    # Create a Product object and pass on the values
    new_product = Product(
        name = body_data.get("name"),
        description= body_data.get("description"),
        price = body_data.get("price"),
        stock = body_data.get("stock")
    )
    # Add to the session and commit
    db.session.add(new_product)
    db.session.commit()

    # Serialise object
    data = product_schema.dump(new_product)

    # Return newly created product
    return jsonify(data), 201

# DELETE a product
# DELETE /products/id
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    # Statement: DELETE * FROM products WHERE id=product_id;
    # Find the product with the product_id from the database
    # Statement: SELECT * FROM products WHERE id=product_id;

    # Method 1:
    # Define statement
    stmt = db.select(Product).filter_by(id=product_id)
    # Implement/Run statment
    product = db.session.scalar(stmt)

    # OR
    # Method 2
    # product = Product.query.get(product_id)

    # If it exists
    if product:
        # Delete product
        db.session.delete(product)
        db.session.commit()
        # Send acknowledgement message
        return {"Message": f"Product with id {product_id} deleted succesfully."}
    # Else
    else:
        # Send acknowledgement message
        return {"Message": f"Product with id {product_id} does not exist."}


# UPDATE method: PUT, PATCH
# Main differences. PUT has DML and DDL capabilities. PATCH is mainly for DML
# PUT/PATCH /products/id
@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    # Statement: UPDATE products SET column_name=value;
    # product = Product.query.get(product_id)
    stmt = db.select(Product).filter_by(id=product_id)
    # Implement/Run statment
    product = db.session.scalar(stmt)
    # Find the product with the id = product_id
    # If product exists
    if product:
        # Fetch the updated values from the request body
        body_data = request.get_json()
        # Update the value(s) - SHORT CIRCUIT
        product.name = body_data.get("name") or product.name
        product.description = body_data.get("description") or product.description
        product.price = body_data.get("price") or product.price
        product.stock = body_data.get("stock") or product.stock

        db.session.commit()

        # Serialise
        return jsonify(product_schema.dump(product))
    # Else
    else:
        # Acknowledgement message
        return {"Message": f"Product with id {product_id} does not exist."}
    
# Define GET /categories
@app.route("/categories")
def get_categories():
    # Define the GET Statement/Write the query
    stmt = db.select(Category)
    # Execute it - using Scalar(s)
    categories_list = db.session.scalars(stmt)
    # Serialise it (Convert it to JSON)
    data = categories_schema.dump(categories_list)
    # Return it
    return jsonify(data)

# GET a category
# GET /categories/{id}
@app.route("/categories/<int:category_id>")
def get_single_category(category_id):
    # Define the GET Statement/Write the query
    stmt = db.select(Category).where(Category.id == category_id)
    # Execute it - using Scalar(s)
    category = db.session.scalar(stmt)

    if category:
        # Serialise it (Convert it to JSON)
        data = category_schema.dump(category)
        # Return it
        return jsonify(data)
    else:
        return jsonify({"message": f"Category with id {category_id} does not exist."}), 404

# CREATE a category
# POST /categories
@app.route("/categories", methods=["POST"])
def create_category():
    # Statement: INSERT INTO category(arg1, arg2, etc.) VALUES (value1, value2, etc.).
    # Get the body JSON data
    body_data = request.get_json()
    # Create a Product object and pass on the values
    new_category = Category(
        name = body_data.get("name"),
        description= body_data.get("description")
    )
    # Add to the session and commit
    db.session.add(new_category)
    db.session.commit()

    # Serialise object
    data = category_schema.dump(new_category)

    # Return newly created category
    return jsonify(data), 201


# DELETE a category
# DELETE /categories/id
@app.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    # Statement: DELETE * FROM categories WHERE id=category_id;
    # Find the category with the category_id from the database
    # Statement: SELECT * FROM categories WHERE id=category_id;

    # Method 1:
    # Define statement
    stmt = db.select(Category).filter_by(id=category_id)
    # Implement/Run statment
    category = db.session.scalar(stmt)

    # OR
    # Method 2
    # category = Catgeory.query.get(product_id)

    # If it exists
    if category:
        # Delete product
        db.session.delete(category)
        db.session.commit()
        # Send acknowledgement message
        return {"Message": f"Category with id {category_id} deleted succesfully."}
    # Else
    else:
        # Send acknowledgement message
        return {"Message": f"Category with id {category_id} does not exist."}


if __name__ == "__main__":
    app.run(debug=True)