def test_get_products_return_empty_list(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_products_success(client):
    response = client.get('/products')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_create_product_success(client):
    new_product = {
        "name": "Test product",
        "price": 19.99
    }

    response = client.post('/products', json=new_product)
    assert response.status_code == 201
    product = response.get_json()
    assert 'id' in product
    assert product['name'] == "Test product"

def test_update_product_success(client):
    # Create a new product to update
    new_product = {
        "name": "Old product",
        "description": "This prooduct's name will be changed.",
        "price": 19.99
    }

    response = client.post('/products', json=new_product)
    product = response.get_json()

    product_id = product["id"]

    # Then Make an update
    update_data = {
        "name": "New product value"
    }

    response = client.patch(f"/products/{product_id}", json=update_data)

    # Test if it worked
    assert response.status_code == 200
    updated = response.get_json()
    assert updated["name"] == "New product value"

def test_update_nonexistent_product(client):
    fake_id = 99999
    update_data = {
        "name": "Ghost product",
        "price": 19.99
    }
    response = client.patch(f"/products/{fake_id}", json=update_data)
    assert response.status_code == 404
    assert "does not exist." in response.get_json()["Message"]