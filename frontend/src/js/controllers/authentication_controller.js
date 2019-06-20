import {Controller} from "stimulus";

const Utils = require('../utils');


const URL_LOGOUT = '/logout/';


export default class extends Controller {
    addListeners() {
        // Before post is sent
        this.element.addEventListener('turbolinks:before-visit', function (event) {
            if (event.data.url === URL_LOGOUT)
                event.preventDefault();
        });
    }

    logout() {
        // const headers = new Headers();
        // headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
        // Turbolinks.clearCache();
        fetch(URL_LOGOUT, {
            method: 'GET',
            // headers: headers
        }).then(r => {
            return r.text();
        }).then(res => {
            this.reset();
            Turbolinks.clearCache();
            let referrer = window.location.href;
            Turbolinks.controller.cache.put(referrer, Turbolinks.Snapshot.fromHTMLString(res));
            Turbolinks.visit(referrer, {action: 'replace'});
        });
    }
}