import {Controller} from "stimulus";

const LIKE = 1;
const SHARE = 2;

const DATA_ITEM_CLASS = 'data-item-class';
const DATA_ITEM_ID = 'data-item';
const DATA_ITEM_CHECKED = 'data-item-checked';
const DATA_ITEM_VOTES = 'data-item-votes';


const URL_POST_VOTE = '/api-auth/post/vote/';
const URL_TOPIC_VOTE = '/api-auth/topic/vote/';
const POST_CLASS = 'post';
const TOPIC_CLASS = 'topic';

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
    get item() {
        return this.element.getAttribute(DATA_ITEM_ID);
    }

    get checked() {
        return Number.parseInt(this.element.getAttribute(DATA_ITEM_CHECKED)) === 1;
    }

    set checked(checked) {
        this.element.setAttribute(DATA_ITEM_CHECKED, checked ? '1' : '0');
    }

    get votes() {
        // Returns number of likes or shares, depending on the attribute (this.element)
        return Number.parseInt(this.element.getAttribute(DATA_ITEM_VOTES));
    }

    set votes(votes) {
        this.element.setAttribute(DATA_ITEM_VOTES, votes);
    }

    connect() {
        if (this.element.getAttribute(DATA_ITEM_CLASS) === POST_CLASS) {
            this.url = URL_POST_VOTE;
            this.payload_key = POST_CLASS;
        } else {
            this.url = URL_TOPIC_VOTE;
            this.payload_key = TOPIC_CLASS;
        }
    }

    vote(vote_type, method) {
        const headers = new Headers();
        headers.set('Content-type', 'application/json');
        headers.set('X-CSRFToken', getCookie('csrftoken'));

        const payload = {vote_type: vote_type};
        payload[this.payload_key] = Number.parseInt(this.item);


        fetch(this.url, {
            method: method,
            body: JSON.stringify(payload),
            headers: headers
        }).then(r => {
            // console.log(r.text());
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