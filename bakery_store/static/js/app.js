
// Dashboard New product
(function (){

    if(document.querySelector('#create-product-ingredient')) {

        let itemCounter = 0;
        let ingredientsCost = 0;
        let option
        
        const ingredientSelector = document.querySelector('#create-product-ingredient');
        const quantity = document.querySelector('#create-product-quantity');
        const btnAdd = document.querySelector('#create-product-add');
        const btnSubmit = document.querySelector('#create-product-submit');
        const customPrice = document.querySelector('#price');
        const totalPrice = document.querySelector('#create-product-total');
        const hiddenList = document.querySelector('#inputs-hidden-container');
        const itemsList = document.querySelector('#create-product-items-list');

        window.onload = function() {
            ingredientSelector.selectedIndex = 0;
            quantity.value = ''
        };

        quantity.addEventListener('input', (e) => {
            if(e.target.value !== '' && ingredientSelector.selectedIndex !== 0) {
                btnAdd.classList.remove('btn-disabled');
            } else {
                btnAdd.classList.add('btn-disabled');
            }
        });
        
        ingredientSelector.addEventListener('change', function(e) {
            option = this.options[this.selectedIndex];
            document.querySelector('#create-product-unit-measurement').textContent = option.dataset.measurementUnit;

            if(customPrice.value !== '') {
                btnAdd.classList.remove('btn-disabled');
            }
        });

        customPrice.addEventListener('input', () => {
            if( ingredientsCost !== 0) {
                const price = customPrice.value ? customPrice.value : 0;
                totalPrice.textContent = '$' + (parseFloat(price) + parseFloat(ingredientsCost)).toFixed(2);
            }
        });

        btnAdd.addEventListener('click', () => {

            if(option && quantity.value) {
                
                const data = {
                    price: option.dataset.price,
                    name: option.textContent,
                    unit_measure: option.dataset.measurementUnit,
                    size: option.dataset.size,
                    quantity: quantity.value,
                    id: option.value
                }
    
                if( itemCounter < 30 ) {
                    // Add input hidden to HTML
                    const filteredData = {
                        id: data.id,
                        quantity: data.quantity
                    }
                    const hidden = document.createElement('INPUT');
                    hidden.type = 'hidden';
                    hidden.value = JSON.stringify(filteredData);
                    hiddenList.appendChild(hidden);
                    hidden.name = `ingredient_data`;

                    // Add ingredient
                    const item = formatItem(data, hidden);
                    itemsList.appendChild(item);
                    itemCounter++;

                    // Reset elements
                    ingredientSelector.selectedIndex = 0;
                    quantity.value = '';
                    document.querySelector('#create-product-unit-measurement').textContent = "empty";
                    option = undefined;
                    btnAdd.classList.add('btn-disabled');
                } else {
                    alert('You cannot add more than 30 ingredients')
                }
            }
            if( itemCounter !== 0 ) {
                btnSubmit.classList.remove('d-none');
            } else {
                btnSubmit.classList.add('d-none');
            }
        });



        // generar los LI con js (reutilizar codigo para que no pierdan funcionalidad)
        // Tambien marcar los selected del select multiple con Js
        if( document.querySelector('[data-previous-items]')) {
            const prevInputs = document.querySelectorAll('[data-previous-items]');

            prevInputs.forEach( input => {

                const jsonData = JSON.parse(input.value);
                const data = {
                    price: input.dataset.price,
                    name: input.dataset.previousItems,
                    unit_measure: input.dataset.measurementUnit,
                    size: input.dataset.size,
                    quantity: jsonData.quantity,
                    id: jsonData.id
                }

                const item = formatItem(data, input);
                itemCounter++;
                itemsList.appendChild(item);
            });
            if( itemCounter !== 0 ) {
                btnSubmit.classList.remove('d-none');
            } else {
                btnSubmit.classList.add('d-none');
            }
        }

        function formatItem(data, hidden) {

            const actualCost = parseFloat(((data.quantity * data.price) / data.size).toFixed(2));
            const item = document.createElement('LI');
            
            item.textContent = `${data.quantity}${data.unit_measure} of ${data.name} - $${actualCost}`;
            ingredientsCost += actualCost;
    
            if(customPrice.value) {
                totalPrice.textContent = '$' + (parseFloat(customPrice.value) + parseFloat(ingredientsCost)).toFixed(2);
            } else {
                totalPrice.textContent = '$' + (parseFloat(ingredientsCost)).toFixed(2);
            }
    
            item.addEventListener('click', (e) => {
                e.target.remove();
                hidden.remove();
                ingredientsCost -= actualCost;
                if(customPrice.value) {
                    totalPrice.textContent = '$' + (parseFloat(customPrice.value) + parseFloat(ingredientsCost)).toFixed(2);
                } else {
                    totalPrice.textContent = '$' + (parseFloat(ingredientsCost)).toFixed(2);
                }
                itemCounter--;
                if( itemCounter !== 0 ) {
                    btnSubmit.classList.remove('d-none');
                } else {
                    btnSubmit.classList.add('d-none');
                }
            });
    
            return item;
        }


    }







})();

// Availability change
(function() {
    // Ingredient page
    if(document.querySelector('#dashboard-ingredient-list')){
        const btns = document.querySelectorAll('.list-availability__btn');

        btns.forEach( btn => {
            const id = btn.dataset.id;

            btn.addEventListener('click', () => {
                const url = `/api/ingredient_availability/${id}`;
                changeAvailability(btn, url);
            });
        });
    }

    // // Product page
    // if(document.querySelector('#dashboard-product-list')){
    //     const btns = document.querySelectorAll('.list-availability__btn');

    //     btns.forEach( btn => {
    //         const id = btn.dataset.id;

    //         btn.addEventListener('click', () => {
    //             const url = `/api/ingredient_availability/${id}`;
    //             changeAvailability(btn, url);
    //         });
    //     });
    // }

    async function changeAvailability(btn, url) {
        try {
            const response = await fetch(url);
            const result = await response.json();

            if( result.item ) {
                if(result.item.availability) {
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
})();