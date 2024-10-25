from functools import wraps
from pymongo import MongoClient
from src.Usuarios.Case1_1 import Grupo
client = MongoClient('mongodb://localhost:27017/')
db = client['Ejemplo']


def verifica_permiso(permiso_requerido):


    def decorador(func):
        @wraps(func)
        def wrapper(grupo_id, db, *args, **kwargs):

            grupo = Grupo(grupo_id, db)


            if grupo.tiene_permiso(permiso_requerido):
                return func(*args, **kwargs)
            else:
                print("No hay permiso")
                return None

        return wrapper

    return decorador


@verifica_permiso("Ver-Pedidos")
def ver_pedidos():
    print("Carrito mostrado")





ver_pedidos(400, db)