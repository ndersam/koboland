import {Controller} from "stimulus";

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function get_method(is_checked) {
    return is_checked ? 'DELETE' : 'POST';
}

const LIKE = 1;
const SHARE = 2;

export default class extends Controller {
    vote(vote_type, method) {
        console.log("refresh!!!!!!!!!!", this.element.getAttribute('data-post'));

        const csrftoken = getCookie('csrftoken');
        const url = '/api-auth/post/vote/';
        const post = this.element.getAttribute('data-post');


        const headers = new Headers();
        headers.set('Content-type', 'application/json');
        headers.set('X-CSRFToken', csrftoken);

        const payload = JSON.stringify({post: Number.parseInt(post), vote_type: vote_type});
        console.log(payload);

        fetch(url, {
            method: method,
            body: payload,
            headers: headers
        }).then(r => {
            console.log(r.text());
        });
    }

    is_checked() {
        return Number.parseInt(this.element.getAttribute('data-checked-state')) === 1;
    }

    like() {
        const checked = this.is_checked();
        this.vote(LIKE, get_method(checked));
        if (checked) {
            this.element.innerHTML = 'Like';
        } else {
            this.element.innerHTML = 'Liked';
        }
    }
}