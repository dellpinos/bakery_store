
// Dashboard New product

(function (){

    if(document.querySelector('#create-product-ingredient')) {

        let itemCounter = 0;
        let ingredientsCost = 0;
        
        const ingredientSelector = document.querySelector('#create-product-ingredient');

        let option
        ingredientSelector.addEventListener('change', function(e) {

            option = this.options[this.selectedIndex];
            document.querySelector('#create-product-unit-measurement').textContent = option.dataset.measurementUnit;
        });

        const btnSubmit = document.querySelector('#create-product-submit');


        // deshabilitar el boton hasta que haya ingreado los dos datos

        btnSubmit.addEventListener('click', () => {

            const itemsList = document.querySelector('#create-product-items-list');
            const quantity = document.querySelector('#create-product-quantity');

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
            } else {
                alert('You cannot add more than 30 ingredients')
            }



        });

        function formatItem(data) {

            // calcular valor
            const actualCost = ((data.quantity * data.price) / data.size).toFixed(2);
            const item = document.createElement('LI');
            item.textContent = `${data.quantity}${data.unit_measure} of ${data.name} - $${actualCost}`;

            ingredientsCost += actualCost;

            
            // De donde sale el NaN ????

            
            document.querySelector('#create-product-total').textContent = document.querySelector('#price').value+ + ingredientsCost;


            item.addEventListener('click', (e) => {
                e.target.remove();
                ingredientsCost -= actualCost;
                document.querySelector('#create-product-total').textContent = document.querySelector('#price').value+ + ingredientsCost;
                itemCounter--;
            });

            return item;


        }

    }
})();

