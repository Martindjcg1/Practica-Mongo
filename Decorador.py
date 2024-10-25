from pymongo import MongoClient


class Grupo:
    def _init_(self, id_grupo, db, nombre=None, permisos=None):

        self.db = db
        self.coleccion = db['Usuarios']
        self.id_grupo = id_grupo

        grupo = self.coleccion.find_one({'IGRUPO': id_grupo})

        if grupo:

            self.nombre = grupo['NOMBRE']
            self.permisos = grupo['PERMISOS']
        else:
            # Si no existe, creamos uno nuevo
            self.nombre = nombre
            self.permisos = permisos or []
            self.guardar()

    def guardar(self):

        grupo_data = {
            'IGRUPO': self.id_grupo,
            'NOMBRE': self.nombre,
            'PERMISOS': self.permisos
        }
        self.coleccion.update_one(
            {'IGRUPO': self.id_grupo},
            {'$set': grupo_data},
            upsert=True
        )
        print(f"Grupo '{self.nombre}' guardado/actualizado en la base de datos.")

    def tiene_permiso(self, permiso):

        return permiso in self.permisos

    def agregar_permiso(self, permiso):

        if permiso not in self.permisos:
            self.permisos.append(permiso)
            self.guardar()
            print(f"Permiso '{permiso}' agregado correctamente.")
        else:
            print(f"El permiso '{permiso}' ya existe.")

    def eliminar_permiso(self, permiso):

        if permiso in self.permisos:
            self.permisos.remove(permiso)
            self.guardar()
            print(f"Permiso '{permiso}' eliminado correctamente.")
        else:
            print(f"El permiso '{permiso}' no se encontró en el grupo.")

    def listar_permisos(self):

        return self.permisos

    def eliminar_grupo(self):

        self.coleccion.delete_one({'IGRUPO': self.id_grupo})
        print(f"Grupo '{self.nombre}' eliminado de la base de datos.")

    def _str_(self):

        return f"Grupo {self.id_grupo} - {self.nombre}, Permisos: {', '.join(self.permisos)}"


client = MongoClient('mongodb://localhost:27017/')
db = client['Ejemplo']

grupo_clientes = Grupo(100, db)
# Verificar si el grupo tiene un permiso específico
# print(grupo_clientes.tiene_permiso("Agregar-Carritoj"))  # True si existe, False si no

# Agregar un permiso
# grupo_clientes.agregar_permiso("Nuevo-Permiso2222")

# Eliminar un permiso
# grupo_clientes.eliminar_permiso("Ver-Carrito")

# Listar permisos
# print(grupo_clientes.listar_permisos())

# Eliminar el grupo
# grupo_clientes.eliminar_grupo()