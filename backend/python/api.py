from fastapi import FastAPI, HTTPException
import pandas as pd
import json
import psycopg2
import yaml
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware

try:
    with open("config.yaml", "r") as file:
        configs = yaml.safe_load(file)
except Exception as e:
    print(f"[ERRO] {e}")

try:
    with open("token.yaml", "r") as t_file:
        token_config = yaml.safe_load(t_file)
except Exception as e:
    print(f"[ERRO] {e}")

SECRET_KEY = token_config["configs"]["private_key"]
ALGORITHM = token_config["configs"]["algorithm"]

def criar_token(dados: dict):
    dados_copia = dados.copy()
    expiracao = datetime.utcnow() + timedelta(minutes=30)
    dados_copia.update({"exp": expiracao})
    
    # Gera a "pulseira" assinada
    token_jwt = jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

def connect_to_psql():
    connection = psycopg2.connect(
        database=configs["postgres"]["database"],
        host=configs["postgres"]["host"],
        user=configs["postgres"]["user"],
        password=configs["postgres"]["password"]
    )

    print("[SUCESSO] Conexão com o banco de dados foi realizada com sucesso")
    
    return connection

def desconnect_psql(connection):
    if connection:
        print("[PROCESSO] Desconectando do banco de dados")

        connection.close()

        print("[SUCESSO] Banco desconectado com sucesso")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/users-info")
async def getUsers():
    try:
        connection = connect_to_psql()
        query = "SELECT * FROM users;"

        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()

        desconnect_psql(connection)

        return results
    
    except Exception as e:
        print(f"[ERRO] {e}")

    finally:
        desconnect_psql(connection)

class Usuario(BaseModel):
    login: str
    senha: str

# Esse método está implementado na página inicial. Mover para a página de cadastro depois...
@app.post("/sign-up")
def cadastrarUsuario(usuario: Usuario):
    connection = None
    try:
        connection = connect_to_psql()
        cursor = connection.cursor()

        query = "INSERT INTO users (login, passwrd) VALUES (%s, %s);"
        cursor.execute(query, (usuario.login, usuario.senha))

        connection.commit()
        
        cursor.close()
        return {"status": "Sucesso", "usuario_recebido": usuario.login}

    except Exception as e:
        if connection:
            # Desfazer as alterações caso der erro 
            connection.rollback()
        print(f"Erro ao inserir: {e}")
        return {"status": "Erro", "mensagem": str(e)}
    
    finally:
        if connection:
            desconnect_psql(connection)

@app.post("/login")
def login(usuario: Usuario):
    connection = None
    try:
        connection = connect_to_psql()
        cursor = connection.cursor()

        query = "SELECT login, passwrd FROM users WHERE login = %s;"
        cursor.execute(query, (usuario.login,))
        user_found = cursor.fetchone()

        if user_found:
            db_login, db_password = user_found
            if db_password == usuario.senha:
                token = criar_token(dados={"sub": db_login})
                return {"access_token": token, "token_type": "bearer"}

        # Se chegou aqui, as credenciais estão erradas
        raise HTTPException(status_code=401, detail="Login ou senha incorretos")

    except HTTPException as http_e:
        # Se for erro de login, relança para o FastAPI responder 401
        raise http_e
    except Exception as e:
        print(f"[ERRO LOGIN] {e}")
        # Erro de banco/código, retorna 500
        raise HTTPException(status_code=500, detail="Erro interno no servidor")
    finally:
        if connection:
            desconnect_psql(connection)