
(function () {

    // Checkout
    document.addEventListener('DOMContentLoaded', () => {

        if (document.querySelector('#seller-prod-max')) {

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

            // Quantity Validation
            const qInputs = document.querySelectorAll('.checkout__quantity');

            qInputs.forEach(input => {

                total += parseInt(input.value) || 0;
                let value = parseInt(input.value) || 0;

                input.addEventListener('input', async e => {
                    let currentValue = e.target.value;

                    // Allows to delete the value
                    if (currentValue === '') {
                        return;
                    }

                    currentValue = parseInt(currentValue);

                    // doesn't allow negative numbers
                    if (currentValue <= 0) {
                        e.target.value = 1;
                        currentValue = 1;
                    }

                    if (value > currentValue) {
                        // Subtracting
                        total -= value - currentValue;
                        value = currentValue;

                        const response = await updateDates(total);
                        const new_dates = JSON.parse(response.disabled_days);

                        setCalendar(new_dates);
                        priceCalculates();
                    } else {
                        // Adding
                        if (total + (currentValue - value) <= maxSellerQuantity) {
                            total += currentValue - value;
                            value = currentValue;

                            const response = await updateDates(total);
                            const new_dates = JSON.parse(response.disabled_days);

                            setCalendar(new_dates);
                            priceCalculates();
                        } else {
                            input.value = value;
                            console.log('You cannot add more products in this order.');
                        }
                    }
                });
            });

            async function updateDates(quantity) {

                const url = `/dashboard/api/calendar_info/${quantity}/${sellerUserId}/`;

                try {
                    const response = await fetch(url);
                    const result = await response.json();

                    return result;

                } catch (error) {
                    throw error;
                }
            }


            function setCalendar(new_dates) {
                flatpickrInstance.set({
                    disable: [
                        function (date) {
                            return date.getDay() === 0; // Disabled sundays
                        },
                        function (date) {
                            if (Array.isArray(new_dates)) {
                                return new_dates.some(prev_date => {
                                    const formattedDate = date.toISOString().split('T')[0]; // ISO Format
                                    return new_dates.includes(formattedDate);
                                });
                            }
                            return false; // If disabledDates isn't an array, don't disable any date
                        }
                    ]
                });
            }

            function priceCalculates() {
                // Makes the prices calculations
                const priceInputs = document.querySelectorAll('.checkout__card-price');
                let totalPrice = 0;

                priceInputs.forEach(price => {
                    const unitPrice = price.dataset.unitPrice;

                    if (parseFloat(unitPrice)) {
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

            // Date picker
            if (document.querySelector('#hidden-checkout-prev-dates')) {

                // Look for previous days 
                if (document.querySelector('#hidden-checkout-prev-dates') && document.querySelector('#hidden-checkout-prev-dates').value) {
                    disabledDates = JSON.parse(document.querySelector('#hidden-checkout-prev-dates').value);
                }

                flatpickrInstance = flatpickr("#hidden-datepicker", {
                    dateFormat: "Y-m-d", // Date format
                    inline: true,
                    minDate: minDay,
                    maxDate: maxDate,
                    disable: [
                        function (date) {
                            return date.getDay() === 0; // Disabled sundays
                        },
                        function (date) {
                            // Disable previous dates
                            if (Array.isArray(disabledDates)) {
                                return disabledDates.some(prev_date => {
                                    const formattedDate = date.toISOString().split('T')[0]; // ISO Format
                                    return disabledDates.includes(formattedDate);
                                });
                            }
                            return false; // If disabledDates isn't an array, don't disable any date
                        }
                    ],

                    onChange: function (disabledDates) {

                        // Update hidden input with selected dates 
                        const formattedDates = disabledDates.map(date => {
                            return date.toISOString().split('T')[0]; // ISO Format
                        });

                        deliveryDate = formattedDates.join(', ');
                    }
                });

            }

            // Removes cart item
            if (document.querySelector('.checkout__card-remove')) {
                const btns = document.querySelectorAll('.checkout__card-remove');

                btns.forEach(btn => {
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

                            if (result.result) {
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

            // Submit order - send POST
            if (document.querySelector('#checkout-submit-btn')) {

                const qInputs = document.querySelectorAll('.checkout__quantity');
                const btn = document.querySelector('#checkout-submit-btn');

                btn.addEventListener('click', async e => {
                    e.preventDefault();

                    if (total <= maxSellerQuantity && deliveryDate) {

                        let products = [];
                        qInputs.forEach(input => {

                            products.push({
                                id: input.dataset.id,
                                quantity: input.value
                            });
                        });

                        const result = await sendProd({
                            products,
                            date: deliveryDate
                        })

                        if (result.ok) {
                            window.location.href = '/orders/pending_deliveries/';
                        } else {
                            console.error('Something went wrong');

                            const response = await result.json();

                            alert(`${response.message}. You'll be redirected.`);

                            // This code is usefull if the library Flatpickr fails

                            const dates = response.prev_invalid_dates.replace(/[\[\]]/g, "")

                            alert(`Some browsers may have problems with the date picker. We strongly recommend trying another browser for a better experience. That said, these dates cannot be used for the current quantity: ${dates}`)

                            setTimeout(() => {
                                location.reload()
                            }, 1000);
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

                        return response;

                    } catch (error) {
                        throw error;
                    }
                }
            }
        }
    });

    function formatPrice(price) {
        return parseFloat(price).toLocaleString('en-US', {
            style: 'currency', currency: 'USD'
        });
    }
})();
