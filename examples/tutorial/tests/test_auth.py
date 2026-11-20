import pytest
from flask import g
from flask import session

from flaskr.db import get_db


def test_register(client):
    # Comprueba que la página de registro carga correctamente (código 200)
    response = client.get("/auth/register")
    assert response.status_code == 200
    # Comprueba que el formulario contiene el botón de registro
    assert b"Register" in response.data

    # Realiza un registro con datos válidos (contraseña >= 8 caracteres)
    response = client.post(
        "/auth/register", data={"username": "a", "password": "testpassword"}
    )
    # Comprueba que después del registro correcto, redirige al login
    assert response.headers["Location"] == "/auth/login"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", b"Username is required."),
        ("a", "", b"Password is required."),
        # Nuevo caso de test para contraseñas demasiado cortas (< 8 caracteres)
        ("a", "short", b"Password must be at least 8 characters long."),
        # Se actualiza la contraseña a una válida (>= 8 caracteres) para probar el usuario duplicado
        ("test", "testpassword", b"already registered"),
    ),
)
def test_register_validate_input(client, username, password, message):
    # Envía el formulario con diferentes combinaciones de datos inválidos o duplicados
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    # Comprueba que el mensaje de error esperado aparece en la respuesta
    assert message in response.data


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", b"Incorrect username."), ("test", "a", b"Incorrect password.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
