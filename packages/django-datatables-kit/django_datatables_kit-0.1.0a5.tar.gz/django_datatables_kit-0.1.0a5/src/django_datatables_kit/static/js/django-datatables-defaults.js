"use strict";
/*!
 * Copyright (C) 2024-2025 Aalap Shah aka fishfin <shah.aalap@gmail.com>
 * Proprietary and confidential. All right reserved.
 * Permission is granted to Protective General Engineering Private Limited,
 * Jamshedpur, to use or modify this code for own use only.
 * Unauthorized copying of contents of this file or package, in part or full,
 * is strictly prohibited.
 */
document.addEventListener("DOMContentLoaded", function (event) {
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;
    // https://datatables.net/examples/advanced_init/defaults.html
    // Object.assign(target, ...sources) merges properties from multiple sources
    // into a single target object, equivalent to Python dict.update()
    Object.assign(DataTable.defaults, DJDTK_DATATABLES_DEFAULTS);
    Object.assign(DataTable.defaults, {
        ajax: {
            type: "POST",
            headers: {
                "X-CSRFToken": csrfToken
            },
            dataSrc: {
                data: "data",
                draw: "draw",
                recordsTotal: "recordsTotal",
                recordsFiltered: "recordsFiltered",
            },
            // https://datatables.net/reference/option/ajax.data
            data: function (dataToServer, settings) {
                dataToServer.author = "fishfin";
                dataToServer.htmlEscape = DJDTK_DATATABLES_CONFIG.globalSearchHtmlEscape;
                // Send custom htmlEscape parameter for each column
                var customParms = {};
                // Access the columns definition dynamically via DataTable defaults
                var columns = settings.aoColumns;
                columns.forEach(function (column, index) {
                    // Use the 'htmlEscape' property from each column's definition
                    customParms[`columns[${index}][htmlEscape]`] = column.htmlEscape !== undefined ? column.htmlEscape : false;
                });
                Object.assign(dataToServer, customParms);
            },
        },
        _drawCallback: function (settings) {
            let api = this.api();
            // Iterate through each row
            api.rows().every(function () {
                var row = this.node(); // Get the row element
                // Iterate through each column in the row
                $('td', row).each(function () {
                    var cell = $(this); // Get the cell element
                    var cellData = cell.html(); // Get the cell data
                    console.log("more fuck " + cellData);
                    // Check if the cell data is a string
                    if (typeof cellData === 'string') {
                        // HTML escape the string
                        var escapedData = $('<div>').text(cellData).html();
                        // Update the cell with the escaped data
                        cell.html(escapedData);
                    }
                });
            });
        },
        _rowCallback: function (row, data, displayNum, displayIndex, dataIndex) {
            console.log(data);
            console.log(displayNum + " = " + displayIndex + " = " + dataIndex);
        },
    });
});
