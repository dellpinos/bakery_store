(function () {

    // Availability change
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#dashboard-product-list')) {
            
            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const btns = document.querySelectorAll('.list-availability__btn');
            
            btns.forEach(btn => {
                const id = btn.dataset.id;
                
                btn.addEventListener('click', () => {
                    const url = `/api/product_availability/${id}/`;
                    changeAvailability(btn, url, csrftoken);
                });
            });
        }

        async function changeAvailability(btn, url, csrftoken) {
            try {

                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    }
                });

                if (response.ok) {
                    const result = await response.json();

                    if (result.item) {
                        if (result.item.availability) {
                            btn.classList.remove('content__btn-disabled');
                            btn.classList.add('content__btn-enabled');
                            btn.textContent = "Enabled";
                        } else {
                            btn.classList.remove('content__btn-enabled');
                            btn.classList.add('content__btn-disabled');
                            btn.textContent = "Disabled";
                        }
                    }
                } else {
                    const result = await response.json();
                    alert( result.error);
                }

            } catch (error) {
                throw new Error(error);
            }
        }
    });
})();