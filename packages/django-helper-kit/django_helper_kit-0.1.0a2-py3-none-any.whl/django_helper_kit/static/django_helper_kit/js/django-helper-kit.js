"use strict";
/*!
 * Copyright (C) 2024-2025 Aalap Shah aka fishfin <shah.aalap@gmail.com>
 * Proprietary and confidential. All right reserved.
 * Permission is granted to Protective General Engineering Private Limited,
 * Jamshedpur, to use or modify this code for own use only.
 * Unauthorized copying of contents of this file or package, in part or full,
 * is strictly prohibited.
 */
document.addEventListener('DOMContentLoaded', function () {
    djhkSetDjangoDefaultDropdownEmptyOption();
});
const djhkSetDjangoDefaultDropdownEmptyOption = function () {
    document.querySelectorAll("select").forEach(function (select) {
        const options = select.options;
        for (let i = 0; i < options.length; i++) {
            if (options[i].value === "" && options[i].textContent.trim() === "---------") {
                options[i].textContent = XLangTranslations.dropdownSelect || "-- Select --";
                break; // Exit the loop once the match is found and replaced
            }
        }
    });
};
const djhkHTMLEscape = function (str) {
    const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    };
    return str.replace(/[&<>"']/g, function (k) { return map[k]; });
};
const djhkHTMLUnescape = function (str) {
    const map = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
    };
    return str.replace(/[(&amp;)|(&lt;)|(&gt;)|(&quot;)|(&#39;)"]/g, function (k) { return map[k]; });
};
