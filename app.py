from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import json

# Configurações
app = Flask(__name__)

# Conectar ao MongoDB local
client = MongoClient("mongodb://localhost:27017/")
db = client["catalogo"]
colecao_discos = db["discos"]
colecao_eventos = db["eventos"]


# Função para validar dados de discos
def validar_dados_disco(dados):
    campos_obrigatorios = ["titulo", "descricao", "local", "capacidade"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            return False, f"Campo '{campo}' é obrigatório."
        if campo == "capacidade" and (
            not isinstance(dados[campo], int) or dados[campo] <= 0
        ):
            return False, "Campo 'capacidade' deve ser um inteiro maior que zero."
    return True, ""


# Função para validar dados de eventos
def validar_dados_evento(dados):
    campos_obrigatorios = ["nome", "data", "local"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            return False, f"Campo '{campo}' é obrigatório."
    return True, ""


# Rota para criar um novo disco
@app.route("/discos", methods=["POST"])
def criar_disco():
    dados = request.json
    valido, mensagem = validar_dados_disco(dados)
    if not valido:
        return jsonify({"erro": mensagem}), 400

    resultado = colecao_discos.insert_one(dados)
    return (
        jsonify(
            {"mensagem": "Disco criado com sucesso!", "id": str(resultado.inserted_id)}
        ),
        201,
    )


# Rota para consultar discos
@app.route("/discos", methods=["GET"])
def consultar_discos():
    discos = list(colecao_discos.find())
    for disco in discos:
        disco["_id"] = str(disco["_id"])
    return jsonify(discos), 200


# Rota para consultar um disco específico
@app.route("/discos/<id>", methods=["GET"])
def consultar_disco(id):
    disco = colecao_discos.find_one({"_id": ObjectId(id)})
    if disco:
        disco["_id"] = str(disco["_id"])
        return jsonify(disco), 200
    return jsonify({"erro": "Disco não encontrado"}), 404


# Rota para atualizar um disco
@app.route("/discos/<id>", methods=["PUT"])
def atualizar_disco(id):
    dados = request.json
    valido, mensagem = validar_dados_disco(dados)
    if not valido:
        return jsonify({"erro": mensagem}), 400

    resultado = colecao_discos.update_one({"_id": ObjectId(id)}, {"$set": dados})
    if resultado.matched_count:
        return jsonify({"mensagem": "Disco atualizado com sucesso!"}), 200
    return jsonify({"erro": "Disco não encontrado"}), 404


# Rota para deletar um disco
@app.route("/discos/<id>", methods=["DELETE"])
def deletar_disco(id):
    resultado = colecao_discos.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count:
        return jsonify({"mensagem": "Disco deletado com sucesso!"}), 200
    return jsonify({"erro": "Disco não encontrado"}), 404


# Rota para criar um novo evento
@app.route("/eventos", methods=["POST"])
def criar_evento():
    dados = request.json
    valido, mensagem = validar_dados_evento(dados)
    if not valido:
        return jsonify({"erro": mensagem}), 400

    resultado = colecao_eventos.insert_one(dados)
    return (
        jsonify(
            {"mensagem": "Evento criado com sucesso!", "id": str(resultado.inserted_id)}
        ),
        201,
    )


# Rota para listar todos os eventos
@app.route("/eventos", methods=["GET"])
def listar_eventos():
    eventos = list(colecao_eventos.find())
    for evento in eventos:
        evento["_id"] = str(evento["_id"])
    return jsonify(eventos), 200


# Rota para buscar um evento por ID ou parâmetros
@app.route("/eventos/<id>", methods=["GET"])
def buscar_evento(id):
    evento = colecao_eventos.find_one({"_id": ObjectId(id)})
    if evento:
        evento["_id"] = str(evento["_id"])
        return jsonify(evento), 200
    return jsonify({"erro": "Evento não encontrado"}), 404


@app.route("/eventos", methods=["GET"])
def buscar_eventos():
    parametros = request.args.to_dict()
    eventos = list(colecao_eventos.find(parametros))
    for evento in eventos:
        evento["_id"] = str(evento["_id"])
    return jsonify(eventos), 200


# Rota para atualizar um evento por ID ou parâmetros
@app.route("/eventos/<id>", methods=["PUT"])
def atualizar_evento(id):
    dados = request.json
    valido, mensagem = validar_dados_evento(dados)
    if not valido:
        return jsonify({"erro": mensagem}), 400

    resultado = colecao_eventos.update_one({"_id": ObjectId(id)}, {"$set": dados})
    if resultado.matched_count:
        return jsonify({"mensagem": "Evento atualizado com sucesso!"}), 200
    return jsonify({"erro": "Evento não encontrado"}), 404


@app.route("/eventos", methods=["PUT"])
def atualizar_eventos():
    parametros = request.args.to_dict()
    dados = request.json
    valido, mensagem = validar_dados_evento(dados)
    if not valido:
        return jsonify({"erro": mensagem}), 400

    resultado = colecao_eventos.update_many(parametros, {"$set": dados})
    if resultado.matched_count:
        return (
            jsonify(
                {
                    "mensagem": f"{resultado.matched_count} eventos atualizados com sucesso!"
                }
            ),
            200,
        )
    return jsonify({"erro": "Nenhum evento encontrado"}), 404


# Rota para deletar um evento por ID ou parâmetros
@app.route("/eventos/<id>", methods=["DELETE"])
def deletar_evento(id):
    resultado = colecao_eventos.delete_one({"_id": ObjectId(id)})
    if resultado.deleted_count:
        return jsonify({"mensagem": "Evento deletado com sucesso!"}), 200
    return jsonify({"erro": "Evento não encontrado"}), 404


@app.route("/eventos", methods=["DELETE"])
def deletar_eventos():
    parametros = request.args.to_dict()
    resultado = colecao_eventos.delete_many(parametros)
    if resultado.deleted_count:
        return (
            jsonify(
                {
                    "mensagem": f"{resultado.deleted_count} eventos deletados com sucesso!"
                }
            ),
            200,
        )
    return jsonify({"erro": "Nenhum evento encontrado"}), 404


# Iniciar a aplicação
if __name__ == "__main__":
    app.run(debug=True)
