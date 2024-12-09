// Main Js entry file
import 'vite/modulepreload-polyfill';
import flatpickr from "flatpickr";
import "flatpickr/dist/flatpickr.min.css";

import app from './app.js';
import changeAvailability from './changeAvailability.js';
import checkout from './checkout.js';
import deliveries from './deliveries.js';
import newProduct from './newProduct.js';
import orders from './orders.js';
import passwordValidation from './passwordValidation.js';
import settings from './settings.js';

document.addEventListener('DOMContentLoaded', () => {
    app();
    changeAvailability();
    checkout();
    deliveries();
    newProduct();
    orders();
    passwordValidation();
    settings();
});