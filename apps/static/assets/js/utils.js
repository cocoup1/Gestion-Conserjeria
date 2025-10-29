/**
 * Función para configurar la validación en tiempo real de campos que solo permiten letras y espacios
 * @param {string} selector - El selector de los campos a validar
 */
function configurarValidacionLetrasYEspacios(selector)
{

    document.querySelectorAll(selector).forEach((campo) => {
        // Agrega un listener al evento 'input' para capturar cambios mientras el usuario escribe
        campo.addEventListener('input', function (event) {
            // Elimina cualquier carácter no permitido en tiempo real
            const valorFiltrado = this.value.replace(/[^a-zA-Z\s]/g, '');
            if (this.value !== valorFiltrado) {
                this.value = valorFiltrado; // Actualiza el campo solo si es necesario
            }
        });

        // Agrega un listener al evento 'blur' para validar cuando el usuario sale del input
        campo.addEventListener('blur', function () {
            this.value = this.value.trim(); // Elimina espacios al principio y al final
        });
    });
}

/**
 * Función para configurar la validación en tiempo real de campos que solo permiten números
 * @param {string} selector - El selector de los campos a validar
 */
function configurarValidacionSoloNumeros(selector) {
    document.querySelectorAll(selector).forEach((campo) => {
        // Agrega un listener al evento 'input' para capturar cambios mientras el usuario escribe
        campo.addEventListener('input', function () {
            // Elimina cualquier carácter no permitido (que no sea un número)
            const valorFiltrado = this.value.replace(/[^0-9]/g, '');
            if (this.value !== valorFiltrado) {
                this.value = valorFiltrado; // Actualiza el campo solo si es necesario
            }
        });

        // Agrega un listener al evento 'blur' para validar cuando el usuario sale del input
        campo.addEventListener('blur', function () {
            this.value = this.value.trim(); // Elimina espacios al principio y al final
        });
    });
}
