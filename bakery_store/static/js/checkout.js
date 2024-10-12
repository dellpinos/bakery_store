(function () {
    // Checkout
    document.addEventListener('DOMContentLoaded', () => {
        
        let total = 0;
        let deliveryDate
        const maxSellerQuantity = parseInt(document.querySelector('#seller-prod-max').value);
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');


        console.log(csrftoken);


        if (document.querySelector('#seller-prod-max')) {
            // Quantity Validation
            const qInputs = document.querySelectorAll('.checkout__quantity');


            qInputs.forEach( input => {
                total += parseInt(input.value);
                let value = parseInt(input.value);

                input.addEventListener('input', e => {

                    // doesn't allow negative numbers
                    if (parseInt(e.target.value) <= 0) {
                        e.target.value = 1
                    }

                    if ( e.target.value > 0 ) {
                        if ( value > parseInt(input.value)) {
                            // Substracting
                            if( total - (value - parseInt(input.value)) > 1) {
                                total -= value - parseInt(input.value);
                                value = parseInt(input.value);
                            }
    
                        } else {
                            // Adding
                            if( total + (parseInt(input.value) - value) <= maxSellerQuantity) {
                                total += parseInt(input.value) - value;
                                value = parseInt(input.value);
                            } else {
    
                                input.value = value;
                                console.log('You cannot add more products in this order.')
    
                            }
                        }
                    }

                })
            });
        }

        if (document.querySelector('#hidden-checkout-prev-dates')) {
            // Date picker


            /////

            let prev_dates
            // Look for previous days 
            if (document.querySelector('#hidden-checkout-prev-dates') && document.querySelector('#hidden-checkout-prev-dates').value) {
                prev_dates = JSON.parse(document.querySelector('#hidden-checkout-prev-dates').value);
            }

            const today = new Date();
            const maxDate = new Date(today);

            maxDate.setDate(today.getDay() + 90); // max 3 months

            flatpickr("#hidden-datepicker", {
                dateFormat: "Y-m-d", // Formato de fecha
                inline: true,
                minDate: "today", // Fecha mínima (hoy)
                maxDate: maxDate,
                // mode: "multiple", // Habilitar selección múltiple
                positionElement: "today",
                disable: [
                    function (date) {
                        // Deshabilitar los domingos
                        return date.getDay() === 0; // 0 es el domingo
                    },
                    function(date) {
                        // Deshabilitar fechas previas
                        if (Array.isArray(prev_dates)) {
                            return prev_dates.some(prev_date => {
                                // Convertir el string de fecha a objeto Date para comparar
                                return date.toDateString() === new Date(prev_date).toDateString();
                            });
                        }
                        return false; // Si prev_dates no es un array, no deshabilitar
                    }
                    // function(date) {
                    //     // Deshabilitar fechas previas
                    //     prev_dates.map(date => {
                    //         // Crear el objeto Date asegurando que sea el formato correcto
                    //         const parts = date.split('-'); // Separar la fecha
                    //         return new Date(parts[0], parts[1] - 1, parts[2]); // Crear el objeto Date (mes es 0-indexed)
                    //     })
                    // }
                ],
                // defaultDate: prev_dates.map(date => {
                //     // Crear el objeto Date asegurando que sea el formato correcto
                //     const parts = date.split('-'); // Separar la fecha
                //     return new Date(parts[0], parts[1] - 1, parts[2]); // Crear el objeto Date (mes es 0-indexed)
                // }),
                onChange: function (prev_dates) {

                    
                    // Actualizar el input hidden con las fechas seleccionadas
                    const formattedDates = prev_dates.map(date => {
                        return date.toISOString().split('T')[0]; // Formato YYYY-MM-DD
                    });
                    console.log('FIT')
                    console.log(formattedDates)

                    deliveryDate = formattedDates.join(', ');

                    // Actualizar el input hidden con las fechas formateadas
                    // document.querySelector('#hidden-datepicker').value = formattedDates.join(', '); // Cambia 'hidden-input' por el ID de tu input hidden
                },
            });




            ////


        }

        if( document.querySelector('#checkout-submit-btn')) {
        // Send POST
            console.log('FOX')
            const qInputs = document.querySelectorAll('.checkout__quantity');
            const btn = document.querySelector('#checkout-submit-btn');





            btn.addEventListener('click', async e => {
                e.preventDefault();
                console.log('FIX')

                if( total <= maxSellerQuantity && deliveryDate) {

                    let products = [];
                    qInputs.forEach( input => {
                        console.log('FAT')
                        products.push({
                            id: input.dataset.id,
                            quantity: input.value
                        })

                    })

                    await sendProd({
                        products,
                        date: deliveryDate
                    })
                    console.log(products)

                }


            })

            async function sendProd(body) {

                const url = '/orders/api/order/create';

                console.log(csrftoken)

                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                        body
                    });
                    const result = await response.json()
    
                    console.log(result)


                } catch (error) {
                    throw error;
                }
            }

            
        }
    });
})();