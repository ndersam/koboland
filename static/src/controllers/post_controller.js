import {Controller} from "stimulus";

const Utils = require('../js/utils');
const LIKE = 1;
const DISLIKE = -1;
const NO_VOTE = 0;
const SHARE = 2;
const UNSHARE = -2;
const URL = '/api-auth/vote/';

const DATA_ITEM_CLASS = 'data-item-class';
const DATA_ITEM_ID = 'data-item';
const DATA_ITEM_CHECKED = 'data-item-checked';
const DATA_ITEM_VOTES = 'data-item-votes';


const URL_POST_VOTE = '/api-auth/post/vote/';
const URL_TOPIC_VOTE = '/api-auth/topic/vote/';
const POST_CLASS = 'post';
const TOPIC_CLASS = 'topic';


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
            this.payload_key = POST_CLASS;
        } else {
            this.payload_key = TOPIC_CLASS;
        }
    }

    vote(vote_type) {

        const headers = new Headers();
        headers.set('Content-type', 'application/json');
        headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));

        const payload = {};
        payload['votable_id'] = Number.parseInt(this.item);
        payload['votable_type'] = this.payload_key;
        payload['vote_type'] = vote_type;


        fetch(URL, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: headers
        }).then(r => {
            // console.log(r.text());
        });
    }

    like() {
        this.vote(this.checked ? NO_VOTE : LIKE);
        if (this.checked) {
            this.votes--;
            this.element.innerHTML = `Like(${this.votes})`;
        } else {
            this.votes++;
            this.element.innerHTML = `Liked(${this.votes})`;
        }
        this.checked = !this.checked;
    }

    dislike() {
        this.vote(this.checked ? NO_VOTE : DISLIKE);
        if (this.checked) {
            this.votes--;
            this.element.innerHTML = `Dislike(${this.votes})`;
        } else {
            this.votes++;
            this.element.innerHTML = `Disliked(${this.votes})`;
        }
        this.checked = !this.checked;
    }

    share() {
        this.vote(this.checked ? UNSHARE : SHARE);

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