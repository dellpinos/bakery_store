import imgFullCheck from '../../img/full-check.svg';
import imgEmptyCheck from '../../img/empty-check.svg';

(function () {

    console.log('here')
    // Validates password requirements
    document.addEventListener('DOMContentLoaded', () => {

        if (document.querySelector('#input-pass')) {

            const inputPass = document.querySelector('#input-pass');
            const inputConf = document.querySelector('#input-pass-conf');

            const conditions = {
                car: false,
                up: false,
                low: false,
                num: false,
                equal: false
            };

            inputPass.addEventListener('input', e => {
                const value = e.target.value;

                const regUp = /[A-Z]/;
                const regLow = /[a-z]/;
                const regNum = /\d/;

                if( value.length >= 8) {
                    changeStatus('car', true);
                } else {
                    changeStatus('car', false);
                }

                if( regUp.test(value)) {
                    changeStatus('up', true);
                } else {
                    changeStatus('up', false);
                }

                if( regLow.test(value)) {
                    changeStatus('low', true);
                } else {
                    changeStatus('low', false);
                }

                if( regNum.test(value)) {
                    changeStatus('num', true);
                } else {
                    changeStatus('num', false);
                }

                if( value === inputConf.value && value !== '' ) {
                    changeStatus('equal', true);
                } else {
                    changeStatus('equal', false);
                }

                btnStatus();

            });

            inputConf.addEventListener('input', e => {

                const value = e.target.value;
                if( value === inputPass.value && value !== '' ) {
                    changeStatus('equal', true);
                } else {
                    changeStatus('equal', false);
                }

                btnStatus();
            });

            function changeStatus(itemName, status) {

                const item = document.querySelector(`#pass-item-${itemName}`);
                const img = document.querySelector(`#pass-check-${itemName}`);

                if( status) {
                    // Checked
                    item.classList.remove('c-red');
                    item.classList.add('c-green');
                    img.src = imgFullCheck
                    conditions[itemName] = true

                } else {
                    // Unchecked
                    item.classList.remove('c-green');
                    item.classList.add('c-red');
                    img.src = imgEmptyCheck
                    conditions[itemName] = false
                }
            }

            function btnStatus() {

                // Check if all conditions are met
                const allTrue = Object.values(conditions).every(value => value === true);
                const btn = document.querySelector('#form-btn-submit');
                
                if (allTrue) {
                    btn.disabled = false;
                    btn.classList.remove('btn-disabled');
                    
                } else {
                    btn.disabled = true
                    btn.classList.add('btn-disabled');
                }
            }
        }
    });
})();