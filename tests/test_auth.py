"""
PRUEBAS DEL MÓDULO DE AUTENTICACIÓN
=================
EP (Partición de Equivalencia), BVA (Análisis de Valores Límite),
casos extremos y vectores de ataque para registro e inicio de sesión.
"""
import pytest
from tests.conftest import _cabeceras_auth






class TestRegistroEP:
    def test_registrar_usuario_valido(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "juan_perez", "first_name": "Prueba", "last_name": "Usuario", "email": "juan@prueba.com",
            "password": "FuerteP1", "role": "cliente",
        })
        assert respuesta.status_code == 201
        assert respuesta.json()["username"] == "juan_perez"

    @pytest.mark.parametrize("role", ["admin", "cajero", "delivery"])
    def test_registro_publico_no_escala_rol(self, cliente_api, role):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": f"user_{role}", "first_name": "Prueba", "last_name": "Usuario", "email": f"{role}@test.com",
            "password": "FuerteP1", "role": role,
        })
        assert respuesta.status_code == 201
        assert respuesta.json()["role"] == "cliente"

    def test_registrar_rol_invalido(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "baduser", "first_name": "Prueba", "last_name": "Usuario", "email": "bad@test.com",
            "password": "FuerteP1", "role": "superadmin",
        })
        assert respuesta.status_code == 422

    def test_registrar_default_role_is_cliente(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "default_role", "first_name": "Prueba", "last_name": "Usuario", "email": "def@test.com",
            "password": "FuerteP1",
        })
        assert respuesta.status_code == 201
        assert respuesta.json()["role"] == "cliente"






class TestRegistroBVA:
    @pytest.mark.parametrize("longitud,esperado", [
        (2, 422), (3, 201), (4, 201), (29, 201), (30, 201), (31, 422),
    ])
    def test_username_longitud(self, cliente_api, longitud, esperado):
        name = "a" * longitud
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": name, "first_name": "Prueba", "last_name": "Usuario", "email": f"{name[:10]}@t.com",
            "password": "FuerteP1",
        })
        assert respuesta.status_code == esperado, f"len={longitud} got {resp.status_code}"

    @pytest.mark.parametrize("longitud,esperado", [
        (7, 422), (8, 201), (9, 201), (19, 201), (20, 201), (21, 422),
    ])
    def test_contrasena_longitud(self, cliente_api, longitud, esperado):
        
        pwd = "Aa1" + "x" * (longitud - 3)
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": f"pwdtest_{longitud}", "first_name": "Prueba", "last_name": "Usuario", "email": f"pwd{longitud}@t.com",
            "password": pwd,
        })
        assert respuesta.status_code == esperado, f"len={longitud} got {resp.status_code}"






class TestRegistroCasosExtremos:
    def test_usuario_vacio(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "", "first_name": "Prueba", "last_name": "Usuario", "email": "e@t.com", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422

    def test_whitespace_username(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "   ", "first_name": "Prueba", "last_name": "Usuario", "email": "ws@t.com", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422

    def test_emoji_username(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "🍕user", "first_name": "Prueba", "last_name": "Usuario", "email": "emoji@t.com", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422

    def test_very_long_username(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "a" * 1000, "first_name": "Prueba", "last_name": "Usuario", "email": "long@t.com", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422

    def test_contrasena_sin_mayuscula(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "noup", "first_name": "Prueba", "last_name": "Usuario", "email": "noup@t.com", "password": "password1",
        })
        assert respuesta.status_code == 422

    def test_contrasena_sin_minuscula(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "nolow", "first_name": "Prueba", "last_name": "Usuario", "email": "nolow@t.com", "password": "PASSWORD1",
        })
        assert respuesta.status_code == 422

    def test_contrasena_sin_numero(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "nodig", "first_name": "Prueba", "last_name": "Usuario", "email": "nodig@t.com", "password": "Password",
        })
        assert respuesta.status_code == 422

    def test_duplicate_username(self, cliente_api):
        cliente_api.post("/api/auth/register", json={
            "username": "dupuser", "first_name": "Prueba", "last_name": "Usuario", "email": "dup1@t.com", "password": "FuerteP1",
        })
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "dupuser", "first_name": "Prueba", "last_name": "Usuario", "email": "dup2@t.com", "password": "FuerteP1",
        })
        assert respuesta.status_code in (400, 409)

    def test_duplicate_email(self, cliente_api):
        cliente_api.post("/api/auth/register", json={
            "username": "emaildup1", "first_name": "Prueba", "last_name": "Usuario", "email": "same@t.com", "password": "FuerteP1",
        })
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "emaildup2", "first_name": "Prueba", "last_name": "Usuario", "email": "same@t.com", "password": "FuerteP1",
        })
        assert respuesta.status_code in (400, 409)

    def test_invalid_email_format(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "bademail", "first_name": "Prueba", "last_name": "Usuario", "email": "notanemail", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422

    def test_registrar_empty_body(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={})
        assert respuesta.status_code == 422

    def test_contrasena_special_chars_only(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "usuarioname": "specialpw", "first_name": "Prueba", "last_name": "Usuario", "email": "special@t.com", "contrasena": "!@#$%^&*()",
        })
        assert respuesta.status_code == 422

    def test_null_byte_in_username(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "user\x00name", "first_name": "Prueba", "last_name": "Usuario", "email": "nullbyte@t.com", "password": "FuerteP1",
        })
        
        assert respuesta.status_code in (201, 422)






class TestRegistroAtaques:
    def test_sql_injection_username(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "' OR 1=1 --", "first_name": "Prueba", "last_name": "Usuario", "email": "sqli@t.com", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422

    def test_sql_injection_email(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/register", json={
            "username": "sqlimail", "first_name": "Prueba", "last_name": "Usuario", "email": "'; DROP TABLE users; --", "password": "FuerteP1",
        })
        assert respuesta.status_code == 422






class TestLoginEP:
    def test_iniciar_sesion_valid(self, cliente_api):
        cliente_api.post("/api/auth/register", json={
            "username": "loginuser", "first_name": "Prueba", "last_name": "Usuario", "email": "login@t.com", "password": "FuerteP1",
        })
        respuesta = cliente_api.post("/api/auth/login", data={
            "username": "loginuser", "password": "FuerteP1",
        })
        assert respuesta.status_code == 200
        assert "access_token" in respuesta.json()

    def test_iniciar_sesion_contrasena_incorrecta(self, cliente_api):
        cliente_api.post("/api/auth/register", json={
            "username": "wrongpw", "first_name": "Prueba", "last_name": "Usuario", "email": "wp@t.com", "password": "FuerteP1",
        })
        respuesta = cliente_api.post("/api/auth/login", data={
            "username": "wrongpw", "password": "WrongPass9",
        })
        assert respuesta.status_code == 401

    def test_iniciar_sesion_inexistente_user(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/login", data={
            "username": "noexist", "password": "FuerteP1",
        })
        assert respuesta.status_code == 401

    def test_iniciar_sesion_sql_injection(self, cliente_api):
        respuesta = cliente_api.post("/api/auth/login", data={
            "username": "' OR 1=1 --", "password": "anything",
        })
        assert respuesta.status_code == 401






class TestTokenAutenticacion:
    def test_access_protected_no_token(self, cliente_api):
        respuesta = cliente_api.get("/api/auth/me")
        assert respuesta.status_code == 401

    def test_access_with_token_invalido(self, cliente_api):
        respuesta = cliente_api.get("/api/auth/me", headers=_cabeceras_auth("not-a-valid-token"))
        assert respuesta.status_code == 401

    def test_access_with_malformed_jwt(self, cliente_api):
        respuesta = cliente_api.get("/api/auth/me", headers=_cabeceras_auth("eyJ.eyJ.sig"))
        assert respuesta.status_code == 401

    def test_obtener_me_valid(self, cliente_api, token_cliente):
        respuesta = cliente_api.get("/api/auth/me", headers=_cabeceras_auth(token_cliente))
        assert respuesta.status_code == 200
        assert respuesta.json()["username"] == "usuario_cliente"

    def test_token_expirado(self, cliente_api):
        from app.utils.security import create_access_token
        from datetime import timedelta
        
        expired_token = create_access_token({"sub": "1"}, expires_delta=timedelta(hours=-2))
        respuesta = cliente_api.get("/api/auth/me", headers=_cabeceras_auth(expired_token))
        assert respuesta.status_code == 401
