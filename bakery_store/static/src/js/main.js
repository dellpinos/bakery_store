// Main Js entry file
import 'vite/modulepreload-polyfill';
import flatpickr from "flatpickr";
import "flatpickr/dist/flatpickr.min.css";

import app from './app';
import changeAvailability from './changeAvailability';
import checkout from './checkout';
import deliveries from './deliveries';
import newProduct from './newProduct';
import orders from './orders';
import passwordValidation from './passwordValidation';
import settings from './settings';

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