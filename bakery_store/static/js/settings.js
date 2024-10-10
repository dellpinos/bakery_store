(function () {
    // Calendar & Settings
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#hidden-datepicker')) {

            let prev_dates
            // Look for previous days 
            if (document.querySelector('#hidden-prev-dates') && document.querySelector('#hidden-prev-dates').value) {
                prev_dates = JSON.parse(document.querySelector('#hidden-prev-dates').value);
            }

            const today = new Date();
            const maxDate = new Date(today);

            maxDate.setDate(today.getDay() + 90); // max 3 months

            flatpickr("#hidden-datepicker", {
                dateFormat: "Y-m-d", // Formato de fecha
                inline: true,
                minDate: "today", // Fecha mínima (hoy)
                maxDate: maxDate,
                mode: "multiple", // Habilitar selección múltiple
                positionElement: "today",
                disable: [
                    function (date) {
                        // Deshabilitar los domingos
                        return date.getDay() === 0; // 0 es el domingo
                    },
                    // function(date) {
                    //     // Deshabilitar fechas previas
                    //     if (Array.isArray(prev_dates)) {
                    //         return prev_dates.some(prev_date => {
                    //             // Convertir el string de fecha a objeto Date para comparar
                    //             return date.toDateString() === new Date(prev_date).toDateString();
                    //         });
                    //     }
                    //     return false; // Si prev_dates no es un array, no deshabilitar
                    // }
                ],
                defaultDate: prev_dates.map(date => {
                    // Crear el objeto Date asegurando que sea el formato correcto
                    const parts = date.split('-'); // Separar la fecha
                    return new Date(parts[0], parts[1] - 1, parts[2]); // Crear el objeto Date (mes es 0-indexed)
                }),
                onChange: function (prev_dates) {
                    // Actualizar el input hidden con las fechas seleccionadas
                    const formattedDates = prev_dates.map(date => {
                        return date.toISOString().split('T')[0]; // Formato YYYY-MM-DD
                    });
                    console.log('FIT')
                    console.log(formattedDates)

                    // Actualizar el input hidden con las fechas formateadas
                    document.querySelector('#hidden-datepicker').value = formattedDates.join(', '); // Cambia 'hidden-input' por el ID de tu input hidden
                },
            });
        }
    });
})();