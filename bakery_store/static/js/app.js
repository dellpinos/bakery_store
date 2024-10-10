(function () {
    // Cart
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#header-cart-icon')) {

            const cartIcon = document.querySelector('#header-cart-btn');

            cartIcon.addEventListener('mouseover', () => {
                document.querySelector('#cart-triangle').classList.remove('d-none');
                document.querySelector('#cart-header').classList.remove('d-none');
            });

            cartIcon.addEventListener('mouseout', () => {
                document.querySelector('#cart-triangle').classList.add('d-none');
                document.querySelector('#cart-header').classList.add('d-none');
            });

            getCart();
        }

        if (document.querySelector('#btn-add-cart')) {

            const btn = document.querySelector('#btn-add-cart');
            const productId = btn.dataset.product;

            btn.addEventListener('click', handlerClick);

            async function handlerClick() {

                try {
                    const url = `/orders/api/cart/create/${productId}`;
                    const response = await fetch(url);
                    const result = await response.json();

                    if (!result.error) {
                        // Deletes empty message
                        if (document.querySelector('.msg-empty')) {
                            document.querySelector('.msg-empty').remove();

                        }
                        await getCart();

                        btn.removeEventListener('click', handlerClick);
                        const card = btn.parentElement;
                        btn.remove();
                        const msg = document.createElement('P');
                        msg.classList.add('mt-3')
                        msg.textContent = "This product is in your cart. You can update the quantity at checkout. Remember, you must complete your order with this seller before ordering products from other sellers."

                        card.appendChild(msg);

                    } else {
                        console.log(result.error)
                    }

                } catch (error) {
                    throw Error('Something went wrong.')
                }
            }
        }

        async function getCart() {

            const counter = document.querySelector('#header-cart-icon');
            try {
                const url = `/orders/api/cart/`;

                const response = await fetch(url);
                const result = await response.json();

                if (result.response > 0) {
                    counter.textContent = result.response;
                }

                cartFormat(result);
                return true;

            } catch (error) {
                throw Error('Something went wrong.')
            }
        };

        function cartFormat(data) {
            const list = document.querySelector('#cart-header-list');

            if (data.response > 0) {

                const cart = document.querySelector('#cart-header');

                // Deletes previous elements
                list.innerHTML = '';
                if (cart.querySelector('.btn')) {
                    cart.querySelector('.btn').remove();
                }

                data.products.forEach(prod => {
                    const item = formatItem(prod);
                    list.appendChild(item);

                });

                const cartButton = document.createElement('A');
                cartButton.href = '/orders/checkout';

                cartButton.classList.add("btn");
                cartButton.textContent = "Checkout";
                cart.appendChild(cartButton);

            } else {
                list.innerHTML = `
                <p class="msg-empty">There are no products to show</p>
            `;
            }
        }

        function formatItem(product) {

            const item = document.createElement('LI');
            item.classList.add("cart__item");
            item.innerHTML = `
                <img src="${product.image}" alt="${product.name}">
                <div class="cart__desc">
                    <p>${product.name}</p>
                    <p>$${product.price}</p>
                    <p>Production time: ${product.production_time} days</p>
                </div>
        `;
            return item;
        }
    });
})();