from django.db import connection

cursor = connection.cursor()
cursor.execute('DESCRIBE authentication_comuna')
print("Estructura de la tabla authentication_comuna:")
print("-" * 80)
for row in cursor.fetchall():
    print(f"Campo: {row[0]}, Tipo: {row[1]}, Null: {row[2]}, Key: {row[3]}")
