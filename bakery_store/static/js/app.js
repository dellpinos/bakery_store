
// Dashboard New product

(function (){

    if(document.querySelector('#create-product-ingredient')) {

        let itemCounter = 0;
        let ingredientsCost = 0;
        let option
        
        const ingredientSelector = document.querySelector('#create-product-ingredient');
        const quantity = document.querySelector('#create-product-quantity');
        const btnSubmit = document.querySelector('#create-product-submit');
        const customPrice = document.querySelector('#price');
        const totalPrice = document.querySelector('#create-product-total');

        window.onload = function() {
            ingredientSelector.selectedIndex = 0;
            quantity.value = ''
        };

        quantity.addEventListener('input', (e) => {
            if(e.target.value !== '' && ingredientSelector.selectedIndex !== 0) {
                btnSubmit.classList.remove('btn-disabled');
            } else {
                btnSubmit.classList.add('btn-disabled');
            }
        });
        
        ingredientSelector.addEventListener('change', function(e) {
            option = this.options[this.selectedIndex];
            document.querySelector('#create-product-unit-measurement').textContent = option.dataset.measurementUnit;

            if(customPrice.value !== '') {
                btnSubmit.classList.remove('btn-disabled');
            }
        });

        customPrice.addEventListener('input', () => {
            if( ingredientsCost !== 0) {
                const price = customPrice.value ? customPrice.value : 0;
                totalPrice.textContent = '$' + (parseFloat(price) + parseFloat(ingredientsCost)).toFixed(2);
            }
        });

        btnSubmit.addEventListener('click', () => {
            if(option && quantity.value) {
                const itemsList = document.querySelector('#create-product-items-list');
                const data = {
                    price: option.dataset.price,
                    name: option.textContent,
                    unit_measure: option.dataset.measurementUnit,
                    size: option.dataset.size,
                    quantity: quantity.value
                }
    
                if(itemCounter < 30) {
                    const item = formatItem(data);
                    itemsList.appendChild(item);
                    itemCounter++;
                    ingredientSelector.selectedIndex = 0;
                    quantity.value = '';
                    document.querySelector('#create-product-unit-measurement').textContent = "empty";
                    option = undefined;
                    btnSubmit.classList.add('btn-disabled');
                } else {
                    alert('You cannot add more than 30 ingredients')
                }
            }
        });

        function formatItem(data) {

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
                ingredientsCost -= actualCost;
                if(customPrice.value) {
                    totalPrice.textContent = '$' + (parseFloat(customPrice.value) + parseFloat(ingredientsCost)).toFixed(2);
                } else {
                    totalPrice.textContent = '$' + (parseFloat(ingredientsCost)).toFixed(2);
                }
                itemCounter--;
            });

            return item;
        }
    }
})();

// Availability change
(function() {
    
    if(document.querySelector('#ingredient-list-availability')){


        const btn = document.querySelector('#ingredient-list-availability');
        const id = btn.dataset.id;

        // Enviar request con el id y cambiar el estilo del botón
        btn.addEventListener('click', () => {

        });




    }

})();