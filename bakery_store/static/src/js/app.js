(function () {

    // Cart & Notifications
    document.addEventListener('DOMContentLoaded', () => {
        
        // Cart
        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        // Gives format to all prices
        formatAllPrices();

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

                const result = await addToCart(productId);

                if (!result.error) {
                    // Deletes empty message
                    if (document.querySelector('.popup__msg-empty')) {
                        document.querySelector('.popup__msg-empty').remove();

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
                    btn.removeEventListener('click', handlerClick);
                    const card = btn.parentElement;
                    btn.remove();
                    const msg = document.createElement('P');
                    msg.classList.add('mt-3')
                    msg.textContent = result.error

                    card.appendChild(msg);
                }
            }
        }

        async function addToCart(productId) {
            
            const url = `/orders/api/cart/create/${productId}/`;

            try {
                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    }
                });

                const result = await response.json();
                return result;

            } catch (error) {
                throw Error('Something went wrong.')
            }
        }

        async function getCart() {

            const counter = document.querySelector('#header-cart-icon');
            const counterMobile = document.querySelector('#mobile-cart-counter');

            const url = `/orders/api/cart/`;
            try {

                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    }
                });
                const result = await response.json();

                if (result.response > 0) {
                    counter.textContent = result.response;
                    counterMobile.textContent = result.response;
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
                <p class="popup__msg-empty">There are no products to show</p>
            `;
            }
        }

        function formatItem(product) {

            const item = document.createElement('LI');
            item.classList.add("popup__item");
            item.innerHTML = `
                <div class="popup__img-cont">
                    <img src="${product.image}" alt="${product.name}">
                </div>
                <div class="popup__desc ellipsis">
                    <p>${product.name}</p>
                    <p>${formatPrice(product.price)}</p>
                    <p>Production time: ${product.production_time} days</p>
                </div>
            `;
            return item;
        }

        function formatAllPrices(){

            const prices = document.querySelectorAll('.format-price');
            prices.forEach(price => {
                price.textContent = formatPrice(price.textContent);
            });
        }

        function formatPrice(price) {
            return parseFloat(price).toLocaleString('en-US', { 
                style: 'currency', currency: 'USD' 
            })
        }

        // Notifications

        if (document.querySelector('#header-notif-icon')) {

            const notifIcon = document.querySelector('#header-notif-btn');

            notifIcon.addEventListener('mouseover', () => {
                document.querySelector('#notif-triangle').classList.remove('d-none');
                document.querySelector('#notif-header').classList.remove('d-none');

            });

            notifIcon.addEventListener('mouseleave', () => {
                document.querySelector('#notif-triangle').classList.add('d-none');
                document.querySelector('#notif-header').classList.add('d-none');
                getNotifications();
            });

            getNotifications();
            
            
            // Mobile Notifications
            const btnNotif = document.querySelector('#nav-mobile-btn-notif');
            btnNotif.addEventListener('click', () => {
                
                // Mostrar ventana con notificaciones
                document.querySelector('#notif-mobile-menu').classList.remove('d-none');
                getNotifications();
                
            });

        }
        async function getNotifications() {

            const counter = document.querySelector('#header-notif-icon');
            const counterMobile = document.querySelector('#mobile-notif-counter');


            const url = `/users/api/notifications/`;
            try {

                const response = await fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    }
                });
                const result = await response.json();

                if (result.response > 0) {
                    counter.textContent = result.response;
                    counterMobile.textContent = result.response;
                } else {
                    counter.textContent = '';
                    counterMobile.textContent = '';
                }

                notifFormat(result);

                return true;

            } catch (error) {
                throw Error('Something went wrong.')
            }
        };

        function notifFormat(data) {
            
            const list = document.querySelector('#notif-header-list');
            const listMobile = document.querySelector('#notif-mobile-list');
            
            if (data.notifications.length > 0) {
                
                const cart = document.querySelector('#notif-header');
                
                // Deletes previous elements
                list.innerHTML = '';
                listMobile.innerHTML = '';

                if (cart.querySelector('.btn')) {
                    cart.querySelector('.btn').remove();
                }
                
                data.notifications.forEach(notif => {
                    const item = formatNotifItem(notif);
                    list.appendChild(item);

                    // Clone to mobile version
                    const itemClone = formatNotifItem(notif);
                    listMobile.appendChild(itemClone);

                });
                
            } else {

                list.innerHTML = `
                    <p class="popup__msg-empty">There are no notifications to show</p>
                `;
                listMobile.innerHTML = `
                    <p class="popup__msg-empty">There are no notifications to show</p>
                `;
            }
        }
        function formatNotifItem(notif) {
            
            const item = document.createElement('LI');
            item.classList.add("popup__item");
            
            if( !notif.is_read ) {
                item.classList.add("popup__item--new");
            }

            const rawDate = new Date(notif.created_at);

            const options = {
                year: "2-digit",
                month: "2-digit",
                day: "2-digit",
                hour: "numeric",
                minute: "numeric"
            };

            const formatedDate = rawDate.toLocaleString('en-US', options);

            const date = document.createElement('P');
            date.textContent = formatedDate;

            const dateCont = document.createElement('DIV');
            dateCont.classList.add('flex-end')

            dateCont.appendChild(date);

            const btn = document.createElement('BUTTON');
            btn.classList.add('popup__close');
            btn.textContent = 'X';

            const cont = document.createElement('DIV');
            cont.classList.add('popup__desc');

            const msg = document.createElement('P');
            msg.textContent = notif.message

            cont.appendChild(dateCont);
            cont.appendChild(msg);

            item.appendChild(btn);
            item.appendChild(cont);

            item.addEventListener('mouseover', markAsRead);

            async function markAsRead() {
                if( notif.is_read ) return

                const url = `/users/api/mark_read/${notif.id}`;
                try {
                    const response = await fetch(url, {
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        }
                    });
                    await response.json();

                    item.classList.remove("popup__item--new");
                    item.removeEventListener('mouseover', markAsRead);

                } catch (error) {
                    console.log(error)
                }
            }

            btn.addEventListener('click', async () => {

                const url = `/users/api/notification_delete/${notif.id}`;
                try {
                    const response = await fetch(url, {
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        }
                    });
                    await response.json();

                    getNotifications();

                } catch (error) {
                    console.log(error)
                }
            })
            return item;
        }

        // Mobile Menu
        if( document.querySelector('#nav-mobile-btn')){

            const btnMenu = document.querySelector('#nav-mobile-btn');
            const menuMobile = document.querySelector('#menu-mobile');
            
            btnMenu.addEventListener('click', () => {
                
                if( document.querySelector('#notif-mobile-menu') ) {
                    // Authenticated user
                    document.querySelector('#notif-mobile-menu').classList.add('d-none');
                }
                
                document.querySelector('body').classList.toggle('no-scroll');
                menuMobile.classList.toggle('menu-mobile--active');
                
                btnMenu.classList.toggle('menu-mobile__btn--rotate');
                
            });
        }
        
        if( document.querySelector('#nav-mobile-btn-cat') ) {
            
            const btnCat = document.querySelector('#nav-mobile-btn-cat');

            btnCat.addEventListener('click', () => {

                // Show Categories
                const containers = document.querySelectorAll('.categories-section__item-container');

                containers.forEach( cont => {
                    cont.classList.toggle('categories-section__item-container--visible');
                    document.querySelector('.categories-section').classList.toggle('categories-section--visible');
                });
            });
        }
    });
})();