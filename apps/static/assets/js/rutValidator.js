// Función genérica para validar y formatear RUT en tiempo real
function configurarValidacionRut(selector, errorSelector) {
    document.querySelectorAll(selector).forEach((campo) => {
        campo.addEventListener('input', function () {
            let rut = this.value;

            // Eliminar caracteres no válidos
            rut = rut.replace(/[^0-9kK\-\.]/g, '');

            // Formatear el RUT
            rut = formatearRut(rut);

            // Actualizar el valor del campo
            this.value = rut;

            // Validar el RUT si tiene al menos 9 caracteres
            if (rut.length >= 9) {
                if (validarRut(rut)) {
                    this.style.borderColor = 'green'; // Válido
                    document.querySelector(errorSelector).innerHTML = '';
                } else {
                    this.style.borderColor = 'red'; // Inválido
                    document.querySelector(errorSelector).innerHTML = 'Formato de RUT incorrecto.';
                }
            } else {
                this.style.borderColor = ''; // Restablecer estilo
                document.querySelector(errorSelector).innerHTML = ''; // Limpiar errores
            }
        });
    });
}

// Función para formatear el RUT con puntos y guion
function formatearRut(rut) {
    // Eliminar puntos y guion anteriores
    rut = rut.replace(/\./g, '').replace(/-/g, '');

    // Agregar puntos y guion
    if (rut.length > 1) {
        const cuerpo = rut.slice(0, -1);
        const dv = rut.slice(-1);
        return cuerpo.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '-' + dv;
    }
    return rut;
}

// Función para validar el RUT
function validarRut(rut) {
    // Eliminar puntos y guion
    rut = rut.replace(/\./g, '').replace(/-/g, '');

    const cuerpo = rut.slice(0, -1);
    const dv = rut.slice(-1).toUpperCase();

    // Validar que el cuerpo sea numérico
    if (!/^\d+$/.test(cuerpo)) return false;

    // Calcular dígito verificador
    let suma = 0;
    let multiplicador = 2;

    for (let i = cuerpo.length - 1; i >= 0; i--) {
        suma += parseInt(cuerpo[i]) * multiplicador;
        multiplicador = multiplicador === 7 ? 2 : multiplicador + 1;
    }

    const resto = suma % 11;
    const dvCalculado = resto === 0 ? '0' : resto === 1 ? 'K' : (11 - resto).toString();
    return dv === dvCalculado;
}


function validarFormularioRut(event, rutCampoId, errorCampoId) 
{
    const rutCampo = document.querySelector(rutCampoId); // Obtener el campo del RUT
    const errorCampo = document.querySelector(errorCampoId); // Obtener el contenedor del error
   // alert("rutCampo" +  rutCampo + " - errorCampo  " + errorCampo);
    if (rutCampo && errorCampo) {
        const rut = rutCampo.value;

        if (!validarRut(rut)) {
            event.preventDefault(); // Evitar el envío del formulario
            errorCampo.innerHTML = 'Formato de RUT incorrecto.';
            rutCampo.style.borderColor = 'red'; // Marcar el campo como inválido
        }
    } else {
        console.error('No se encontraron los elementos con los IDs proporcionados:', rutCampoId, errorCampoId);
    }
}

// Función para validar el correo electrónico en tiempo real
function configurarValidacionEmail(selector, errorCampoId) {
    document.querySelectorAll(selector).forEach((campo) => {
        campo.addEventListener('input', function () {
            let email = this.value;

            // Expresión regular para validar el formato del correo electrónico
            const regexEmail = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

            // Verificar si el correo tiene un formato válido
            if (regexEmail.test(email)) {
                //this.style.borderColor = 'green'; // Válido
                document.querySelector(errorCampoId).innerHTML = ''; // Limpiar mensaje de error
            } else {
                //this.style.borderColor = 'red'; // Inválido
                document.querySelector(errorCampoId).innerHTML = 'Correo electrónico inválido'; // Mostrar error
            }
        });
    });
}


