(function () {
    // Availability change
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#dashboard-product-list')) {

            const btns = document.querySelectorAll('.list-availability__btn');

            btns.forEach(btn => {
                const id = btn.dataset.id;

                btn.addEventListener('click', () => {
                    const url = `/api/product_availability/${id}`;
                    changeAvailability(btn, url);
                });
            });
        }

        async function changeAvailability(btn, url) {
            try {
                const response = await fetch(url);
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
            } catch (error) {
                throw new Error(error);
            }
        }
    });
})();