/** @odoo-module **/


export function removeLoader(){
    const loader = document.querySelector('.loader-component');
    if (loader) {
        loader.remove();
    }
}
