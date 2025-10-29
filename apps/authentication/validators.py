import re
from django.core.exceptions import ValidationError

def validate_rut(value):
    # Eliminar puntos y guiones
    rut = re.sub(r'\.|-', '', value)
    
    # Verificar que el RUT tenga el formato correcto
    if not re.match(r'^\d{7,8}[0-9kK]$', rut):
        raise ValidationError('RUT inválido 1')

    # Separar el número del dígito verificador
    rut_number = int(rut[:-1])
    dv = rut[-1].upper()  # Convertir el dígito verificador a mayúscula si es 'k'
    
    # Calcular el dígito verificador usando el algoritmo de módulo 11
    m = 0
    s = 1
    while rut_number > 0:
        s = (s + rut_number % 10 * (9 - m % 6)) % 11
        rut_number //= 10
        m += 1
    
    # Si el resultado es 10, el dígito verificador es 'K', si es 11, es '0', y en otros casos es el número calculado
    calculated_dv = 'K' if s == 10 else '0' if s == 11 else str(s)
    
    # Comparar el dígito verificador calculado con el proporcionado
    if calculated_dv != dv:
        raise ValidationError('RUT inválido 2')

