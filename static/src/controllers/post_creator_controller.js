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
            const data = {};
            const children = this.querySelectorAll('textarea, input');
            for (let idx = 0; idx < children.length; idx++) {
                let child = children.item(idx);
                data[child.name] = child.value;
            }

            // AJAX request
            const headers = new Headers();
            headers.set('Content-type', 'application/json');
            headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
            fetch(POST_URL, {
                method: 'POST',
                body: JSON.stringify(data),
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