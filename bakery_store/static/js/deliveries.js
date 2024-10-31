(function () {
    // Home pending deliveries

    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#recived-btn-container')) {

            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const recivedBtns = document.querySelectorAll('.deliveries__recived');

            if( recivedBtns ) {

                recivedBtns.forEach( btn => {
                    
                    const id = btn.dataset.id;
    
                    function utilityFunction() {
                        newBtnHandler(id, btn, utilityFunction);
                    }
                    
                    btn.addEventListener('click', utilityFunction);
                });
            }
            
            async function handleOrderChanges(url) {
                
                try {
                    const response = await fetch(url, {
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrftoken,
                        }
                    })
                    return response;
                    
                } catch (error) {
                    console.log(error);
                }
            }

            async function newBtnHandler(id, btn, listener){
                // Recived

                const url = `/orders/api/order/recived/${id}/`;
                const result = await handleOrderChanges(url);
                
                if(result.ok) {
                    alert('This order has been finished successfully')

                    btn.classList.remove('deliveries__recived');
                    btn.classList.add('btn-disabled');
                    btn.removeEventListener('click', listener);
                }
            }
         }
    });
})();