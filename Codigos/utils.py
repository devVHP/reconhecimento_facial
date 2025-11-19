import cv2
import numpy as np
from deepface import DeepFace
import pandas as pd

### ANÁLISE FACIAL
def analyze_face_components(img):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")

    if img is None:
        return False, "❌ Erro: imagem não encontrada."

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))

    if len(faces) == 0:
        return False, "❌ Nenhum rosto detectado."
    
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 8, minSize=(20, 20))
        if len(eyes) >= 2:
            return True, "✅ Rosto completo identificado."
        else:
            return False, f"⚠️ Rosto incompleto: olhos detectados = {len(eyes)}"
    return False, "❌ Erro desconhecido na análise facial."

### VERIFICAÇÃO BIOMÉTRICA
def verificar_acesso_biometrico(img_entrada, img_banco):
    if img_entrada is None or img_banco is None:
        return False, "❌ Imagem inválida para verificação biométrica."

    try:
        resultado = DeepFace.verify(img_banco, img_entrada)
        if resultado['verified']:
            return True, "✅ Acesso biométrico liberado!"
        else:
            return False, "❌ Faces não correspondem, acesso negado."
    except Exception as e:
        return False, f"❌ Erro durante verificação biométrica: {str(e)}"

### SQL / BANCO DE DADOS
def criar_usuario(nome, senha, imagem, cur):
    if imagem is None:
        raise ValueError("❌ Imagem inválida ao criar usuário.")
    _, buffer = cv2.imencode('.jpg', imagem)
    imagem_bytes = buffer.tobytes()
    cur.execute("""
        INSERT INTO usuarios (nome, senha, id_permissao, dados_face)
        VALUES (?, ?, 1, ?);
    """, (nome, senha, imagem_bytes))

def verificar_usuario(usuario, cur):
    cur.execute("SELECT nome FROM usuarios WHERE nome = ?", (usuario,))
    return cur.fetchone() is not None

def verificar_acesso(usuario, senha, cur):
    cur.execute("SELECT senha FROM usuarios WHERE nome = ?", (usuario,))
    res = cur.fetchone()
    if res is None:
        return False
    return senha == res[0]

def carregar_imagem_sqlite(usuario, cur):
    cur.execute("SELECT dados_face FROM usuarios WHERE nome = ?", (usuario,))
    dado = cur.fetchone()
    if dado is None:
        return None
    np_arr = np.frombuffer(dado[0], np.uint8)
    imagem = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if imagem is None:
        raise ValueError("❌ Imagem do banco corrompida.")
    return imagem

def verificar_nivel_acesso(usuario, cur):
    cur.execute("""select permissao from permissao
                    left join main.usuarios u on permissao.id_permissao = u.id_permissao
                    where u.nome = ?""", (usuario,))
    return cur.fetchone()[0]

def listar_usuarios(cur):
    cur.execute("""select id_usuario, nome, permissao  from usuarios
    left join permissao p on usuarios.id_permissao = p.id_permissao""")
    return cur.fetchall()

def atualizar_usuario(user_id, novos_campos, cur):

    sets = ", ".join([f"{campo} = ?" for campo in novos_campos.keys()])
    valores = list(novos_campos.values()) + [user_id]

    cur.execute(f"UPDATE usuarios SET {sets} WHERE id_usuario = ?", valores)

def buscar_usuario_por_id_e_nome(user_id, nome, cur):
    cur.execute("SELECT * FROM usuarios WHERE id_usuario = ? AND nome = ?", (user_id, nome))
    resultado = cur.fetchone()
    return resultado

def deletar_usuario(user_id, cur):
    cur.execute("DELETE FROM usuarios WHERE id_usuario = ?", (user_id,))

def carregar_usuarios(con):
    df = pd.read_sql_query("""select id_usuario as ID, nome Usuário, permissao as Permissão  from usuarios
    left join permissao p on usuarios.id_permissao = p.id_permissao""", con)
    return df