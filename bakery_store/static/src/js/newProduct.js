(function () {
    // Dashboard New product
    
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#create-product-ingredient')) {

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

            window.onload = function () {
                ingredientSelector.selectedIndex = 0;
                quantity.value = ''
            };

            quantity.addEventListener('input', (e) => {
                if (e.target.value !== '' && ingredientSelector.selectedIndex !== 0) {
                    btnAdd.classList.remove('btn-disabled');
                } else {
                    btnAdd.classList.add('btn-disabled');
                }
            });

            ingredientSelector.addEventListener('change', function (e) {
                option = this.options[this.selectedIndex];
                document.querySelector('#create-product-unit-measurement').textContent = option.dataset.measurementUnit;

                if (customPrice.value !== '') {
                    btnAdd.classList.remove('btn-disabled');
                }
            });

            customPrice.addEventListener('input', () => {
                if (ingredientsCost !== 0) {
                    const price = customPrice.value ? customPrice.value : 0;
                    totalPrice.textContent = formatPrice(parseFloat(price) + parseFloat(ingredientsCost));
                }
            });

            btnAdd.addEventListener('click', () => {

                if (option && quantity.value) {

                    const data = {
                        price: option.dataset.price,
                        name: option.textContent,
                        unit_measure: option.dataset.measurementUnit,
                        size: option.dataset.size,
                        quantity: quantity.value,
                        id: option.value
                    }

                    if (itemCounter < 30) {
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
                if (itemCounter !== 0) {
                    btnSubmit.classList.remove('d-none');
                } else {
                    btnSubmit.classList.add('d-none');
                }
            });

            if (document.querySelector('[data-previous-items]')) {
                const prevInputs = document.querySelectorAll('[data-previous-items]');

                prevInputs.forEach(input => {

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
                if (itemCounter !== 0) {
                    btnSubmit.classList.remove('d-none');
                } else {
                    btnSubmit.classList.add('d-none');
                }
            }

            function formatItem(data, hidden) {

                const actualCost = parseFloat(((data.quantity * data.price) / data.size).toFixed(2));
                const item = document.createElement('LI');

                item.textContent = `${data.quantity}${data.unit_measure} of ${data.name} - ${formatPrice(actualCost)}`;
                ingredientsCost += actualCost;

                if (customPrice.value) {
                    totalPrice.textContent = formatPrice(parseFloat(customPrice.value) + parseFloat(ingredientsCost));
                } else {
                    totalPrice.textContent = formatPrice(parseFloat(ingredientsCost));
                }

                item.addEventListener('click', (e) => {
                    e.target.remove();
                    hidden.remove();
                    ingredientsCost -= actualCost;
                    if (customPrice.value) {
                        totalPrice.textContent = formatPrice(parseFloat(customPrice.value) + parseFloat(ingredientsCost));
                    } else {
                        totalPrice.textContent = formatPrice(parseFloat(ingredientsCost));
                    }
                    itemCounter--;
                    if (itemCounter !== 0) {
                        btnSubmit.classList.remove('d-none');
                    } else {
                        btnSubmit.classList.add('d-none');
                    }
                });

                return item;
            }

            function formatPrice(price) {
                return parseFloat(price).toLocaleString('en-US', { 
                    style: 'currency', currency: 'USD' 
                })
            }
        }
    });
})();