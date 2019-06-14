import {Controller} from "stimulus";

const Utils = require('../js/utils');
const POST_URL = '/post/';

export default class extends Controller {
    connect() {
        this.addListeners();
    }


    addListeners() {
        // Before post is sent
        this.element.addEventListener('submit', function (event) {
            event.preventDefault();

            // Retrieve data from form
            const formData = new FormData(this);

            // AJAX request
            const headers = new Headers();
            headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
            fetch(POST_URL, {
                method: 'POST',
                body: formData,
                headers: headers
            }).then(r => {
                return r.text();
            }).then(res => {
                this.reset();
                let referrer = window.location.href;
                Turbolinks.controller.cache.put(referrer, Turbolinks.Snapshot.fromHTMLString(res));
                Turbolinks.visit(referrer, {action: 'restore'});
            });
        });

    }
}