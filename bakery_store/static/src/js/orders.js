(function () {
    // Dashboard pending orders

    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('#pending-btn-container')) {

            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const cancelBtns = document.querySelectorAll('.pending__cancel');
            const confirmBtns = document.querySelectorAll('.pending__confirm');
            const archiveBtns = document.querySelectorAll('.pending__archive');

            if( confirmBtns) {

                confirmBtns.forEach( btn => {

                    const id = btn.dataset.id;
                    btn.addEventListener('click', async () => {
                        
                        // Confirm
                        const url = `/orders/api/order/confirm/${id}/`;
                        const result = await handleOrderChanges(url);

                        if( result.ok) {
                            
                            alert('The order is confirmed!')
        
                            const container = btn.parentElement;
                            while (container.firstElementChild) {
                                container.firstElementChild.remove()
                            }

                            function utilityFunction() {
                                newBtnHandler(id, btn, utilityFunction);
                            }

                            newBtn.addEventListener('click', () => utilityFunction);
                            
                        }
                    });
                });
            }

            if( cancelBtns) {

                cancelBtns.forEach( btn => {
                    
                    const id = btn.dataset.id;
                    btn.addEventListener('click', async () => {

                        // Cancel
                        if( confirm("Do you want to delete this order? This action can't be undone.")) {

                            const url = `/orders/api/order/delete/${id}/`;
                            const result = await handleOrderChanges(url);

                            if ( result.ok) {
                                alert('This order has been canceled successfully. The page will be reloaded.')

                                // Remove order card
                                setTimeout(() => {
                                    location.reload();
                                }, 1000);
                            }
                        }
                    });
                });
            }

            if( archiveBtns ) {

                archiveBtns.forEach( btn => {
                    
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
                // Archive
                const url = `/orders/api/order/archive/${id}/`;
                const result = await handleOrderChanges(url);
                
                if(result.ok) {
                    alert('This order has been archived successfully')

                    btn.classList.remove('pending__archive');
                    btn.classList.add('btn-disabled');
                    btn.removeEventListener('click', listener);
                }
            }
        }
    });
})();