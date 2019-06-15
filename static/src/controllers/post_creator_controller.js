import {Controller} from "stimulus";

const Utils = require('../js/utils');
const POST_URL = 'api-auth/submit/post/';
const TOPIC_URL = 'api-auth/submit/topic/';
const DATA_ITEM_CLASS = 'data-item-class';
const POST_CLASS = 'post';
const TOPIC_CLASS = 'topic';

export default class extends Controller {
    connect() {
        const itemType = this.element.getAttribute(DATA_ITEM_CLASS);
        this.url = null;
        if (itemType === POST_CLASS) {
            this.url = POST_URL;
        } else if (itemType === TOPIC_CLASS) {
            this.url = TOPIC_URL;
        }

        if (this.url != null) {
            this.addListeners();
        }
    }


    addListeners() {
        // Before post is sent
        this.element.addEventListener('submit', function (event) {
            event.preventDefault();
            console.log('hi there');
            // Retrieve data from form
            const formData = new FormData(this);

            // AJAX request
            const headers = new Headers();
            headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
            fetch(this.url, {
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