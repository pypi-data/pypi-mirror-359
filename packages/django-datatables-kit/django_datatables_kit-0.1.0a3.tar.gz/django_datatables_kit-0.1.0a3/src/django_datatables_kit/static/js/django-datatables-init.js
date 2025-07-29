"use strict";
/*!
 * Copyright (C) 2024-2025 Aalap Shah aka fishfin <shah.aalap@gmail.com>
 * Proprietary and confidential. All right reserved.
 * Permission is granted to Protective General Engineering Private Limited,
 * Jamshedpur, to use or modify this code for own use only.
 * Unauthorized copying of contents of this file or package, in part or full,
 * is strictly prohibited.
 */
// Always wrap these functions with:
// document.addEventListener("DOMContentLoaded", function (event) {
//   readDtParms(...);
//   initDataTable(...);
// });
function readDtParms(attrId) {
    attrId = attrId.replace(/^#/, "");
    const hashAttrId = "#" + attrId;
    const element = document.querySelector(hashAttrId);
    return JSON.parse(element === null || element === void 0 ? void 0 : element.dataset.dtParms);
}
function initDataTable(tableId, columns, order = [[0, "asc"]]) {
    var _a, _b;
    tableId = tableId.replace(/^#/, "");
    const hashTableId = "#" + tableId;
    const pageLengthLocalStorageName = `dt-${tableId}PageLength`;
    const urlParams = new URLSearchParams(window.location.search);
    const tableElement = document.querySelector(hashTableId);
    const tableWrapperId = `${tableId}_wrapper`;
    const searchInputId = `dt-search-${tableId}`;
    const dtParms = JSON.parse(tableElement === null || tableElement === void 0 ? void 0 : tableElement.dataset.dtParms);
    const minSearchChars = (_a = dtParms["minSearchChars"]) !== null && _a !== void 0 ? _a : 3;
    let tableWrapperElement;
    let searchInputElement;
    let searchCaptionElement;
    const reIdSearchInputInsertCaption = function () {
        tableWrapperElement = document.querySelector(`#${tableWrapperId}`);
        searchInputElement = tableWrapperElement.querySelector(" .dt-search > input");
        searchInputElement.setAttribute("id", searchInputId);
        // searchInputElement.parentElement.insertAdjacentHTML("beforeend", '<div class="dt-search-caption text-danger"></div>')
        searchCaptionElement = document.createElement("div");
        searchCaptionElement.setAttribute("class", "dt-search-caption text-danger");
        searchInputElement.parentElement.insertAdjacentElement("beforeend", searchCaptionElement);
    };
    const minCharInSearchInput = function () {
        let $searchInput = $(searchInputElement);
        $searchInput.unbind();
        $searchInput.bind("input", function (event) {
            if (this.value.length >= DJDTK_DATATABLES_CONFIG.minSearchChars) {
                $(searchCaptionElement).hide();
                dataTable.search(this.value).draw();
            }
            else if (this.value.length > 0) {
                $(searchCaptionElement).text(DJDTK_DATATABLES_CONFIG.language.notMinSearchCharsMessage.replace("_MIN_SEARCH_CHARS_", DJDTK_DATATABLES_CONFIG.minSearchChars)).show();
            }
            else {
                dataTable.search(this.value).draw();
                $(searchCaptionElement).hide();
            }
        });
    };
    let dataTable = new DataTable(hashTableId, {
        initComplete: function (settings, json) {
            reIdSearchInputInsertCaption();
            minCharInSearchInput();
            if (dtParms.qKey && urlParams.get(dtParms.qKey)) {
                dataTable.search(urlParams.get(dtParms.qKey)).draw();
            }
        },
        ajax: {
            url: dtParms.apiUrl,
            error: function (xhr, error, thrown) {
                if (xhr.status === 401) {
                    $(`${hashTableId} tbody td`).html('<b class="text-danger">An error occurred: ' + thrown + " login url: " + `<a href="${xLoginUrl}">Link</a>` + "</b>");
                }
                else {
                    $(`${hashTableId} tbody td`).html('<b class="text-danger">An error occurred: ' + thrown + "</b>");
                }
            }
        },
        pageLength: localStorage.getItem(pageLengthLocalStorageName),
        lengthMenu: (_b = dtParms.lengthMenu) !== null && _b !== void 0 ? _b : DJDTK_DATATABLES_DEFAULTS.lengthMenu,
        order: order,
        columnDefs: [{ targets: "_all", searchable: false, orderable: false }],
        columns: columns,
        responsive: true,
    });
    dataTable.on("length", function () {
        localStorage.setItem(pageLengthLocalStorageName, dataTable.page.info().length);
    });
}
;
