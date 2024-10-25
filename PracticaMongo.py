from pymongo import MongoClient, errors
from pymongo.errors import OperationFailure
import hashlib
from pymongo import MongoClient, errors
from pymongo.errors import OperationFailure

# Conexión a MongoDB
def conectar_mongodb(MONGO_HOST="localhost", MONGO_PORT="27017", MONGO_DB="Ejemplo", MONGO_TIMEOUT=1000):
    try:
        MONGO_URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
        MONGO_CLIENT = MongoClient(MONGO_URI, serverSelectionTimeoutMS=MONGO_TIMEOUT)
        try:
            print(MONGO_CLIENT.server_info())  # Confirmación de conexión
            return MONGO_CLIENT
        except OperationFailure as error_operation:
            print("Error en operación:", error_operation)
            return None
    except errors.ServerSelectionTimeoutError as error:
        print("Tiempo excedido para la conexión:", error)
        return None

# Definición de roles y permisos
ROLES = {
    'Cliente': ["Ver-Productos", "Agregar-Carrito", "Ver-Carrito", "EliminarCarrito", "Realizar-Pedido", "Ver-Pedido", "Cancelar-Pedido"],
    'Administrador-Productos': ["Agregar-Producto", "Editar-Producto", "Eliminar-Producto", "Ver-Productos"],
    'Administrador-Pedidos': ["Ver-Pedidos", "Procesar-Pedido", "Cancelar-Pedido", "VerDetalle-Pedido"],
    'Soporte-Cliente': ["Ver-Clientes", "Ver-Pedidos", "Gestionar-Reclamos"]
}

# Clase Grupo
class Grupo:
    def __init__(self, id_grupo, nombre, permisos):
        self.id_grupo = id_grupo
        self.nombre = nombre
        self.permisos = permisos

    def tiene_permiso(self, permiso):
        return permiso in self.permisos

# Clase Usuario
class Usuario:
    def __init__(self, nombre_usuario, rol_usuario, id_grupo):
        self.nombre_usuario = nombre_usuario
        self.rol_usuario = rol_usuario
        self.id_grupo = id_grupo

    def __str__(self):
        return f'Usuario: {self.nombre_usuario}, Rol: {self.rol_usuario}, Grupo ID: {self.id_grupo}'

# Asignación de ID de grupo según el rol
def obtener_id_grupo(rol_usuario):
    return {
        "Cliente": 100,
        "Administrador-Productos": 200,
        "Administrador-Pedidos": 300,
        "Soporte-Cliente": 400
    }.get(rol_usuario, None)

# Clase GestorUsuarios
class GestorUsuarios:
    def __init__(self, conexion):
        self.conexion = conexion

    def insertar_usuario(self, usuario, db='Practica', collection='Practica'):
        usuario_data = {
            "nombre": usuario.nombre_usuario,
            "rol": usuario.rol_usuario,
            "id_grupo": usuario.id_grupo
        }
        self.conexion[db][collection].insert_one(usuario_data)
        print(f"Usuario {usuario.nombre_usuario} agregado a la colección MongoDB en el grupo ID {usuario.id_grupo}")

    def obtener_usuario_por_email(self, email, db='Practica', collection='Practica'):
        usuario = self.conexion[db][collection].find_one({'email': email})
        if usuario:
            return Usuario(usuario['nombre'], usuario['rol'], usuario['id_grupo'])
        print("Usuario no encontrado en la base de datos.")
        return None

    def obtener_usuarios_por_id_grupo(self, id_grupo, db='Practica', collection='Practica'):
        print(f"Consultando usuarios con id_grupo {id_grupo} en la base de datos '{db}', colección '{collection}'...")
        usuarios = self.conexion[db][collection].find({'id_grupo': id_grupo})

        lista_usuarios = []
        for usuario in usuarios:
            lista_usuarios.append(
                Usuario(usuario.get('nombre'), usuario.get('rol'), usuario.get('id_grupo'))
            )

        if lista_usuarios:
            return lista_usuarios
        else:
            print(f"No se encontraron usuarios en el grupo con ID {id_grupo}.")
            return []


# Método para verificar permiso de un usuario directamente desde MongoDB
def verificar_permiso_usuario(conexion, nombre, permiso, db='Practica', collection='Practica'):
    usuario = conexion[db][collection].find_one({'nombre': nombre})
    if usuario:
        grupo_permisos = ROLES.get(usuario['rol'], [])
        return permiso in grupo_permisos
    else:
        print("Usuario no encontrado en la base de datos.")
        return False

# Menú para interacción
def menu():
    conexion = conectar_mongodb()
    if conexion:
        gestor_usuarios = GestorUsuarios(conexion)

        while True:
            print("\nOpciones:")
            print("1. Agregar usuario y guardar en MongoDB")
            print("2. Verificar permiso de un usuario")
            print("3. Listar usuarios por ID de grupo")
            print("0. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                nombre = input("Ingrese el nombre del usuario: ")
                rol = input("Ingrese el rol del usuario: ")
                id_grupo = obtener_id_grupo(rol)

                if id_grupo:
                    usuario = Usuario(nombre, rol, id_grupo)
                    gestor_usuarios.insertar_usuario(usuario)
                else:
                    print("Rol no válido. Por favor, elija un rol válido.")

            elif opcion == "2":
                nombre = input("Ingrese el nombre del usuario: ")
                permiso = input("Ingrese el permiso a verificar (ej., 'EliminarCarrito'): ")
                tiene_permiso = verificar_permiso_usuario(conexion, nombre, permiso)
                print(f"Permiso {'otorgado' if tiene_permiso else 'denegado'} para el permiso '{permiso}'")

            elif opcion == "3":
                id_grupo = int(input("Ingrese el ID del grupo para listar usuarios: "))
                usuarios_grupo = gestor_usuarios.obtener_usuarios_por_id_grupo(id_grupo)
                if usuarios_grupo:
                    for usuario in usuarios_grupo:
                        print(usuario)
                else:
                    print(f"No se encontraron usuarios en el grupo con ID {id_grupo}.")

            elif opcion == "0":
                print("Saliendo del programa...")
                break
            else:
                print("Opción inválida. Por favor, intente de nuevo.")
    else:
        print("Error al conectar con la base de datos.")

# Ejecutar menú
if __name__ == "__main__":
    menu()
