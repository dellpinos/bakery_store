(function () {
    // Checkout
    document.addEventListener('DOMContentLoaded', () => {
        
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const maxSellerQuantity = parseInt(document.querySelector('#seller-prod-max').value);
        const sellerUserId = parseInt(document.querySelector('#seller-prod-max').dataset.id);
        const minDay = document.querySelector('#hidden-checkout-min-date').value;

        let total = 0;
        let deliveryDate
        const today = new Date();
        const maxDate = new Date(today);

        // Flatpickr
        let flatpickrInstance;
        let disabledDates;
        let markedDay = "today";
        maxDate.setDate(today.getDay() + 90); // max 3 months

        priceCalculates()




        if (document.querySelector('#seller-prod-max')) {
            // Quantity Validation
            const qInputs = document.querySelectorAll('.checkout__quantity');


            qInputs.forEach( input => {
                total += parseInt(input.value);
                let value = parseInt(input.value);

                input.addEventListener('input', async e => {

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

                                const response = await updateDates(total);
                                const new_dates = JSON.parse(response.disabled_days);

                                flatpickrInstance.set({
                                    disable: [
                                        function (date) {
                                            return date.getDay() === 0; // Deshabilitar domingos
                                        },
                                        function(date) {

                                            if (Array.isArray(new_dates)) {
                                                return new_dates.some(prev_date => {
                                                    const formattedDate = date.toISOString().split('T')[0]; // Fecha en formato "YYYY-MM-DD"
                                                    return new_dates.includes(formattedDate);
                                                });
                                            }
                                            return false; // Si disabledDates no es un array, no deshabilitar

                                        }
                                    ]
                                });

                                priceCalculates();
        
                                
                            }
                            
                        } else {
                            // Adding
                            if( total + (parseInt(input.value) - value) <= maxSellerQuantity) {
                                total += parseInt(input.value) - value;
                                value = parseInt(input.value);
                                

                                const response = await updateDates(total);
                                const new_dates = JSON.parse(response.disabled_days);


                                flatpickrInstance.set({
                                    disable: [
                                        function (date) {
                                            return date.getDay() === 0; // Deshabilitar domingos
                                        },
                                        function(date) {
                                            if (Array.isArray(new_dates)) {
                                                return new_dates.some(prev_date => {
                                                    const formattedDate = date.toISOString().split('T')[0]; // Fecha en formato "YYYY-MM-DD"
                                                    return new_dates.includes(formattedDate);
                                                });
                                            }
                                            return false; // Si disabledDates no es un array, no deshabilitar
                                        }

                                    ]
                                });
                                priceCalculates()
                            } else {
    
                                input.value = value;
                                console.log('You cannot add more products in this order.')
    
                            }
                        }
                    }

                })
            });

            async function updateDates(quantity) {

                const url = `/dashboard/api/calendar_info/${quantity}/${sellerUserId}/`;


                try {
                    const response = await fetch(url);
                    const result = await response.json();

                    console.log(result)
                    return result;

                } catch (error) {
                    throw error;
                }
            }




        }

        function priceCalculates() {
            // Makes the prices calculations
            const priceInputs = document.querySelectorAll('.checkout__card-price');
            let totalPrice = 0;

            priceInputs.forEach( price => {
                const unitPrice = price.dataset.unitPrice;

                if( parseFloat(unitPrice) ) {
                    const quantity = document.querySelector(`.checkout__quantity[data-id="${price.dataset.id}"]`);
                    const pageTotalPrice = document.querySelector('#checkout-total-price');

                    const formatedPrice = formatPrice(unitPrice * parseInt(quantity.value));
                    price.textContent = formatedPrice;


                    totalPrice += (unitPrice * parseInt(quantity.value));

                    // Assing total price
                    const formatedTotal = formatPrice(totalPrice);
                    pageTotalPrice.textContent = formatedTotal;

                } else {
                    console.error('Something was wrong')
                }
            });
        }

        if (document.querySelector('#hidden-checkout-prev-dates')) {
            // Date picker




            // Look for previous days 
            if (document.querySelector('#hidden-checkout-prev-dates') && document.querySelector('#hidden-checkout-prev-dates').value) {
                disabledDates = JSON.parse(document.querySelector('#hidden-checkout-prev-dates').value);
            }



            flatpickrInstance = flatpickr("#hidden-datepicker", {
                dateFormat: "Y-m-d", // Formato de fecha
                inline: true,
                minDate: minDay, // Fecha mínima (hoy)
                maxDate: maxDate,
                // mode: "multiple", // Habilitar selección múltiple
                positionElement: markedDay,
                disable: [
                    function (date) {
                        // Deshabilitar los domingos
                        return date.getDay() === 0; // 0 es el domingo
                    },
                    function(date) {
                        // Deshabilitar fechas previas
                        if (Array.isArray(disabledDates)) {
                            return disabledDates.some(prev_date => {
                                const formattedDate = date.toISOString().split('T')[0]; // Fecha en formato "YYYY-MM-DD"
                                return disabledDates.includes(formattedDate);
                            });
                        }
                        return false; // Si disabledDates no es un array, no deshabilitar
                    }
                ],

                onChange: function (disabledDates) {

                    
                    // Actualizar el input hidden con las fechas seleccionadas
                    const formattedDates = disabledDates.map(date => {
                        return date.toISOString().split('T')[0]; // Formato YYYY-MM-DD
                    });

                    deliveryDate = formattedDates.join(', ');

                    // Actualizar el input hidden con las fechas formateadas
                    // document.querySelector('#hidden-datepicker').value = formattedDates.join(', '); // Cambia 'hidden-input' por el ID de tu input hidden
                },
            });


        }

        // Removes item
        if ( document.querySelector('.checkout__card-remove')) {
            const btns = document.querySelectorAll('.checkout__card-remove');
            
            btns.forEach( btn => {
                const productId = btn.dataset.id;
                
                btn.addEventListener('click', async () => {

                    try {
                        const url = `/orders/api/cart/item_delete/${productId}/`;
                        const response = await fetch(url, {
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': csrftoken,
                            }
                        });
                        const result = await response.json();
    
                        if(result.result) {
                            location.reload();
                        } else {
                            console.error('Something went wrong');
                        }
    
                    } catch (error) {
                        console.log(error);
                    }
                });
            });
        }

        if( document.querySelector('#checkout-submit-btn')) {
        // Send POST

            const qInputs = document.querySelectorAll('.checkout__quantity');
            const btn = document.querySelector('#checkout-submit-btn');





            btn.addEventListener('click', async e => {
                e.preventDefault();

                // Falta validar que la fecha no sea inferior al tiempo de produccion mas alto de los productos
                // También hay que validar que dias tiene disponibles el vendedor y
                // cuantas ordenes y productos tiene para ese dia

                if( total <= maxSellerQuantity && deliveryDate ) {

                    let products = [];
                    qInputs.forEach( input => {

                        products.push({
                            id: input.dataset.id,
                            quantity: input.value
                        });
                    });

                    const result = await sendProd({
                        products,
                        date: deliveryDate
                    })

                    if( result.ok ) {
                        location('/orders/pending_deliveries/')
                    } else {
                        console.error('Something went wrong');
                    }


                } else {
                    document.querySelector('#alert-msg-date').classList.remove('g-alert');
                    document.querySelector('#alert-msg-date').classList.add('r-alert');
                }
            })

            async function sendProd(data) {

                const url = '/orders/api/order/create/';

                try {
                    const response = await fetch(url, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();
                    return result;

                } catch (error) {
                    throw error;
                }
            }
        }
    });

    function formatPrice(price) {
        return parseInt(price).toLocaleString('en-US', { 
            style: 'currency', currency: 'USD' 
        })
    }
    function parsePrice(formattedPrice) {
        const cleanPrice = formattedPrice.replace(/[$,]/g, '');
        return parseFloat(cleanPrice);
    }

})();