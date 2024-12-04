// Calendar & Settings
export default function settings() {

    if (document.querySelector('#hidden-prev-dates')) {

        let prev_dates
        let pending_dates // Pending orders

        // Look for previous days 
        if (document.querySelector('#hidden-prev-dates') && document.querySelector('#hidden-prev-dates').value) {
            prev_dates = JSON.parse(document.querySelector('#hidden-prev-dates').value);
        }

        if (document.querySelector('#hidden-pending-dates') && document.querySelector('#hidden-pending-dates').value) {
            pending_dates = JSON.parse(document.querySelector('#hidden-pending-dates').value);
        }

        const today = new Date();
        const maxDate = new Date(today);

        maxDate.setDate(today.getDay() + 120); // max 4 months

        flatpickr("#hidden-datepicker", {
            dateFormat: "Y-m-d", // Date format
            inline: true,
            minDate: "today",
            mode: "multiple", // Enable multiple selection
            positionElement: "today",
            disable: [
                function (date) {
                    return date.getDay() === 0; // Disabled sundays
                },
                function (date) {
                    // Disable previous dates
                    if (Array.isArray(pending_dates)) {
                        return pending_dates.some(prev_date => {
                            const formattedDate = date.toISOString().split('T')[0]; // ISO Format
                            return pending_dates.includes(formattedDate);
                        });
                    }
                    return false; // If disabledDates isn't an array, don't disable any date
                }
            ],
            defaultDate: prev_dates.map(date => {
                // Build Date instance, making sure it's in the right format
                const parts = date.split('-'); // Divide date
                return new Date(parts[0], parts[1] - 1, parts[2]); // Year - Month ( -1, Js index correction) - Day
            }),
            onChange: function (prev_dates) {
                // Update hidden input with selected dates 
                const formattedDates = prev_dates.map(date => {
                    return date.toISOString().split('T')[0]; // ISO Format
                });

                // Update hidden input with formated dates 
                document.querySelector('#hidden-datepicker').value = formattedDates.join(', ');
            },
        });
    }
};