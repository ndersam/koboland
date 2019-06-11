import {Controller} from "stimulus";

const LIKE = 1;
const SHARE = 2;
const DATA_POST_ID = 'data-post';
const DATA_CHECKED_STATE = 'data-checked-state';
const DATA_POST_VOTES = 'data-post-votes';
const URL_POST_VOTE = '/api-auth/post/vote/';

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


export default class extends Controller {
    get post() {
        return this.element.getAttribute(DATA_POST_ID);
    }

    get checked() {
        return Number.parseInt(this.element.getAttribute(DATA_CHECKED_STATE)) === 1;
    }

    set checked(checked) {
        this.element.setAttribute(DATA_CHECKED_STATE, checked ? '1' : '0');
    }

    get votes() {
        // Returns number of likes or shares, depending on the attribute (this.element)
        return Number.parseInt(this.element.getAttribute(DATA_POST_VOTES));
    }

    set votes(votes) {
        this.element.setAttribute(DATA_POST_VOTES, votes);
    }

    vote(vote_type, method) {
        const headers = new Headers();
        headers.set('Content-type', 'application/json');
        headers.set('X-CSRFToken', getCookie('csrftoken'));

        const payload = JSON.stringify({post: Number.parseInt(this.post), vote_type: vote_type});

        fetch(URL_POST_VOTE, {
            method: method,
            body: payload,
            headers: headers
        }).then(r => {
            console.log(r.text());
        });
    }

    like() {
        this.vote(LIKE, get_method(this.checked));
        if (this.checked) {
            this.votes--;
            this.element.innerHTML = `Like(${this.votes})`;
        } else {
            this.votes++;
            this.element.innerHTML = `Liked(${this.votes})`;
        }
        this.checked = !this.checked;
    }

    share() {
        this.vote(SHARE, get_method(this.checked));

        if (this.checked) {
            this.votes--;
            this.element.innerHTML = `Share(${this.votes})`;
        } else {
            this.votes++;
            this.element.innerHTML = `Shared(${this.votes})`;
        }
        this.checked = !this.checked;

    }

}