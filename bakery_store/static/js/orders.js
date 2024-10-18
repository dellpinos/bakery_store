(function () {
    // Dashboard pending orders
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#pending-btn-confirm')) {

            formatAllPrices();

            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const cancelBtns = document.querySelectorAll('.pending__cancel');
            const confirmBtns = document.querySelectorAll('.pending__confirm');

            confirmBtns.forEach( btn => {

                const id = btn.dataset.id;
                btn.addEventListener('click', () => {
                    
                    confirmOrder(id);
                });
            });

            cancelBtns.forEach( btn => {
                
                const id = btn.dataset.id;
                btn.addEventListener('click', () => {

                    cancelOrder(id);
                });
            });

            async function cancelOrder(id) {

                const url = `/orders/api/order/delete/${id}/`;

                try {
                    const response = await fetch(url, {
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        }
                    })

                    const result = await response.json();

                    if ( result.ok) {

                        location.reload();
                    }


                } catch (error) {
                    console.log(error);
                }
            }

            async function confirmOrder(id) {

                const url = `/orders/api/order/confirm/${id}/`;

                try {
                    const response = await fetch(url, {
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        }
                    })
                    const result = await response.json();

                    console.log(result);

                } catch (error) {
                    console.log(error);
                }
            }
        }

        function formatAllPrices() {

            const prices = document.querySelectorAll('.format-price');
            prices.forEach(price => {
                price.textContent = formatPrice(price.textContent);
            })
        }

        function formatPrice(price) {
            return parseInt(price).toLocaleString('en-US', { 
                style: 'currency', currency: 'USD' 
            })
        }





    });
})();