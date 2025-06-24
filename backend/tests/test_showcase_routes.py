import os
import io
import pytest
from app import create_app, db
from app.models import User, ShowcaseItem
from flask_jwt_extended import create_access_token


@pytest.fixture(scope="module")
def test_client():
    flask_app = create_app()
    flask_app.config.update(
        {
            "TESTING": True,
            "PROPAGATE_EXCEPTIONS": False,  # Force custom error handlers
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "JWT_SECRET_KEY": "test_jwt_secret",
            "UPLOAD_FOLDER": os.path.join(
                os.path.dirname(__file__), "test_uploads"
            ),
            "MAX_CONTENT_LENGTH": 5 * 1024 * 1024,  # 5MB
            "ALLOWED_EXTENSIONS": {
                "png",
                "jpg",
                "jpeg",
                "gif",
                "mp4",
                "txt",
            },  # Add txt for easy testing
        }
    )

    # Ensure test upload folder exists
    if not os.path.exists(flask_app.config["UPLOAD_FOLDER"]):
        os.makedirs(flask_app.config["UPLOAD_FOLDER"])

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            # Create a test user
            user = User(username="testuser", email="test@example.com")
            user.set_password("password")
            db.session.add(user)
            db.session.commit()
        yield testing_client
        with flask_app.app_context():
            db.drop_all()
        # Clean up test upload folder
        if os.path.exists(flask_app.config["UPLOAD_FOLDER"]):
            for f in os.listdir(flask_app.config["UPLOAD_FOLDER"]):
                os.remove(os.path.join(flask_app.config["UPLOAD_FOLDER"], f))
            os.rmdir(flask_app.config["UPLOAD_FOLDER"])


@pytest.fixture(scope="module")
def auth_headers(test_client):
    app = test_client.application
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        access_token = create_access_token(
            identity=str(user.id) if user else "fallback_identity_string"
        )  # Ensure token creation uses string identity
    return {"Authorization": f"Bearer {access_token}"}


# --- Test ShowcaseItem CRUD and File Uploads ---


def test_create_showcase_item_no_file(test_client, auth_headers):
    response = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data={
            "title": "My First Showcase",
            "description": "This is a test item without a file.",
        },
    )
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["title"] == "My First Showcase"
    assert json_data["media_url"] is None
    assert ShowcaseItem.query.count() == 1


def test_create_showcase_item_with_allowed_file(test_client, auth_headers):
    data = {
        "title": "Image Showcase",
        "description": "Test with an image.",
        "media_file": (io.BytesIO(b"test image data"), "test.jpg"),
    }
    response = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["title"] == "Image Showcase"
    assert json_data["media_url"] is not None
    assert ".jpg" in json_data["media_url"]

    # Check if file exists in upload folder
    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    assert os.path.exists(os.path.join(upload_folder, json_data["media_url"]))
    ShowcaseItem.query.filter_by(
        id=json_data["id"]
    ).delete()  # Clean up this item
    db.session.commit()


def test_create_showcase_item_disallowed_file_type(test_client, auth_headers):
    data = {
        "title": "Disallowed File Test",
        "media_file": (io.BytesIO(b"some script"), "test.exe"),
    }
    response = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    json_data = response.get_json()
    assert "File type not allowed" in json_data["msg"]


def test_create_showcase_item_file_too_large(test_client, auth_headers):
    # Test file exceeding MAX_CONTENT_LENGTH.
    # Werkzeug typically handles this early, resulting in a 413.

    # Create a file larger than 5MB (default test limit in fixture)
    large_content = b"a" * (6 * 1024 * 1024)
    data = {
        "title": "Large File Test",
        "media_file": (io.BytesIO(large_content), "large.txt"),
    }
    response = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    # Flask/Werkzeug typically returns 413 Request Entity Too Large
    assert response.status_code == 413  # HTTPStatus.REQUEST_ENTITY_TOO_LARGE


def test_get_showcase_items(test_client, auth_headers):
    # Create a couple of items first
    test_client.post(
        "/api/showcase_items", headers=auth_headers, data={"title": "Item A"}
    )
    test_client.post(
        "/api/showcase_items", headers=auth_headers, data={"title": "Item B"}
    )

    response = test_client.get("/api/showcase_items", headers=auth_headers)
    assert response.status_code == 200
    json_data = response.get_json()
    # Checks for items created here; DB state might have other items.
    assert len(json_data) >= 2
    titles = [item["title"] for item in json_data]
    assert "Item A" in titles
    assert "Item B" in titles


def test_get_specific_showcase_item(test_client, auth_headers):
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data={"title": "Specific Item"},
    )
    item_id = post_resp.get_json()["id"]

    response = test_client.get(
        f"/api/showcase_items/{item_id}", headers=auth_headers
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["title"] == "Specific Item"


def test_get_nonexistent_showcase_item(test_client, auth_headers):
    response = test_client.get(
        "/api/showcase_items/9999", headers=auth_headers
    )
    assert response.status_code == 404


def test_update_showcase_item_details(test_client, auth_headers):
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data={"title": "Original Title"},
    )
    item_id = post_resp.get_json()["id"]

    response = test_client.put(
        f"/api/showcase_items/{item_id}",
        headers=auth_headers,
        data={
            "title": "Updated Title",
            "description": "Now with description.",
        },
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["title"] == "Updated Title"
    assert json_data["description"] == "Now with description."


def test_update_showcase_item_with_new_file(test_client, auth_headers):
    # Create item without file
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data={"title": "Item to get a file"},
    )
    item_id = post_resp.get_json()["id"]
    original_media_url = post_resp.get_json().get("media_url")
    assert original_media_url is None

    # Update with a new file
    data = {"media_file": (io.BytesIO(b"new file content"), "new_image.png")}
    response = test_client.put(
        f"/api/showcase_items/{item_id}",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["media_url"] is not None
    assert ".png" in json_data["media_url"]

    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    new_file_path = os.path.join(upload_folder, json_data["media_url"])
    assert os.path.exists(new_file_path)
    with open(new_file_path, "rb") as f:
        assert f.read() == b"new file content"


def test_update_showcase_item_replace_file(test_client, auth_headers):
    # Create item with an initial file
    initial_data = {
        "title": "Item with replaceable file",
        "media_file": (io.BytesIO(b"old data"), "old.txt"),
    }
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data=initial_data,
        content_type="multipart/form-data",
    )
    item_id = post_resp.get_json()["id"]
    old_media_url = post_resp.get_json()["media_url"]
    assert old_media_url is not None
    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    old_file_path = os.path.join(upload_folder, old_media_url)
    assert os.path.exists(old_file_path)

    # Update with a new file
    updated_data = {"media_file": (io.BytesIO(b"new data"), "new.txt")}
    response = test_client.put(
        f"/api/showcase_items/{item_id}",
        headers=auth_headers,
        data=updated_data,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    json_data = response.get_json()
    new_media_url = json_data["media_url"]
    assert new_media_url is not None
    assert new_media_url != old_media_url

    new_file_path = os.path.join(upload_folder, new_media_url)
    assert os.path.exists(new_file_path)  # New file should exist
    assert not os.path.exists(old_file_path)  # Old file should be deleted


def test_update_showcase_item_clear_file(test_client, auth_headers):
    # Create item with a file
    initial_data = {
        "title": "Item to clear file from",
        "media_file": (io.BytesIO(b"data to be cleared"), "clear_me.txt"),
    }
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data=initial_data,
        content_type="multipart/form-data",
    )
    item_id = post_resp.get_json()["id"]
    media_url_to_clear = post_resp.get_json()["media_url"]
    assert media_url_to_clear is not None
    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    file_to_clear_path = os.path.join(upload_folder, media_url_to_clear)
    assert os.path.exists(file_to_clear_path)

    # Update, clearing the file
    response = test_client.put(
        f"/api/showcase_items/{item_id}",
        headers=auth_headers,
        data={"clear_media_file": "true"},
    )
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["media_url"] is None
    assert not os.path.exists(file_to_clear_path)  # File should be deleted


def test_delete_showcase_item_no_file(test_client, auth_headers):
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data={"title": "Item to delete (no file)"},
    )
    item_id = post_resp.get_json()["id"]

    response = test_client.delete(
        f"/api/showcase_items/{item_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert "Showcase item deleted successfully" in response.get_json()["msg"]
    assert ShowcaseItem.query.get(item_id) is None


def test_delete_showcase_item_with_file(test_client, auth_headers):
    # Create item with a file
    data = {
        "title": "Item to delete (with file)",
        "media_file": (
            io.BytesIO(b"this file will be deleted"),
            "delete_this.txt",
        ),
    }
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    item_id = post_resp.get_json()["id"]
    media_url_to_delete = post_resp.get_json()["media_url"]
    assert media_url_to_delete is not None

    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    file_to_delete_path = os.path.join(upload_folder, media_url_to_delete)
    assert os.path.exists(file_to_delete_path)

    # Delete the item
    response = test_client.delete(
        f"/api/showcase_items/{item_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert "Showcase item deleted successfully" in response.get_json()["msg"]
    assert ShowcaseItem.query.get(item_id) is None
    assert not os.path.exists(
        file_to_delete_path
    )  # File should also be deleted


# --- Test File Retrieval Endpoint ---
def test_get_uploaded_file(test_client, auth_headers):
    # Upload a file first
    file_content = b"retrievable content"
    data = {
        "title": "File for retrieval test",
        "media_file": (io.BytesIO(file_content), "retrievable.txt"),
    }
    post_response = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data=data,
        content_type="multipart/form-data",
    )
    assert post_response.status_code == 201
    media_filename = post_response.get_json()["media_url"]
    assert media_filename is not None

    # Attempt to retrieve it
    response = test_client.get(f"/uploads/{media_filename}")
    assert response.status_code == 200
    assert response.data == file_content
    # print(response.mimetype) # For debugging content type if needed


def test_get_nonexistent_uploaded_file(test_client):
    response = test_client.get("/uploads/nonexistentfile.jpg")
    assert response.status_code == 404
    json_data = response.get_json()
    assert (
        "Resource not found" in json_data["msg"]
    )  # Corrected expected message


# --- Test access control ---
def test_access_other_user_showcase_item(test_client, auth_headers):
    # Create an item as current testuser
    post_resp = test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data={"title": "User1 Item"},
    )
    item_id = post_resp.get_json()["id"]

    # Create another user and token
    app = test_client.application
    with app.app_context():
        other_user = User(username="otheruser", email="other@example.com")
        other_user.set_password("password")
        db.session.add(other_user)
        db.session.commit()
        other_access_token = create_access_token(
            identity=str(other_user.id)
        )  # Cast to string
    other_auth_headers = {"Authorization": f"Bearer {other_access_token}"}

    # Try to GET User1's item as otheruser
    response_get = test_client.get(
        f"/api/showcase_items/{item_id}", headers=other_auth_headers
    )
    assert (
        response_get.status_code == 404
    )  # Access denied / not found for this user

    # Try to PUT User1's item as otheruser
    response_put = test_client.put(
        f"/api/showcase_items/{item_id}",
        headers=other_auth_headers,
        data={"title": "Attempted Update"},
    )
    assert response_put.status_code == 404

    # Try to DELETE User1's item as otheruser
    response_delete = test_client.delete(
        f"/api/showcase_items/{item_id}", headers=other_auth_headers
    )
    assert response_delete.status_code == 404

    # Ensure User1 can still access their item
    response_original_user_get = test_client.get(
        f"/api/showcase_items/{item_id}", headers=auth_headers
    )
    assert response_original_user_get.status_code == 200
    assert response_original_user_get.get_json()["title"] == "User1 Item"


def test_get_showcase_items_only_returns_own_items(test_client, auth_headers):
    # User1 (testuser) creates an item
    test_client.post(
        "/api/showcase_items",
        headers=auth_headers,
        data={"title": "Item For User1 Only"},
    )

    # Create another user and token
    app = test_client.application
    with app.app_context():
        user2 = User.query.filter_by(username="user2").first()
        if not user2:
            user2 = User(username="user2", email="user2@example.com")
            user2.set_password("password")
            db.session.add(user2)
            db.session.commit()
        user2_token = create_access_token(
            identity=str(user2.id)
        )  # Cast to string
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # User2 creates an item
    test_client.post(
        "/api/showcase_items",
        headers=user2_headers,
        data={"title": "Item For User2 Only"},
    )

    # Get items for User1
    response_user1 = test_client.get(
        "/api/showcase_items", headers=auth_headers
    )
    assert response_user1.status_code == 200
    items_user1 = response_user1.get_json()
    titles_user1 = [item["title"] for item in items_user1]
    assert "Item For User1 Only" in titles_user1
    assert "Item For User2 Only" not in titles_user1

    # Get items for User2
    response_user2 = test_client.get(
        "/api/showcase_items", headers=user2_headers
    )
    assert response_user2.status_code == 200
    items_user2 = response_user2.get_json()
    titles_user2 = [item["title"] for item in items_user2]
    assert "Item For User2 Only" in titles_user2
    assert "Item For User1 Only" not in titles_user2
