import {Controller} from "stimulus";

const Utils = require('../utils');

const DATA_ITEM = 'data-item';
const DATA_IS_FOLLOWING = 'data-is-following';
const DATA_IS_FOLLOWED = 'data-is-followed';

const URL_CHAT = '/chat/';
const URL_FOLLOW = '/api/user/follow/';


export default class extends Controller {

    static get targets() {
        return ["chat", "follow"];
    }

    get item() {
        return this.element.getAttribute(DATA_ITEM);
    }

    get chat_url() {
        return URL_CHAT + 'user/' + this.item;
    }

    /**
     * Returns true is the user, who's profile is being viewed, follows the logged-in user.
     * @returns {boolean}
     */
    get isFollowing() {
        return this.element.getAttribute(DATA_IS_FOLLOWING).toLowerCase() === 'true';
    }

    /**
     * Returns true is the logged-in user follows the user, whose profile is being viewed.
     * @returns {boolean}
     */
    get isFollowed() {
        return this.element.getAttribute(DATA_IS_FOLLOWED).toLowerCase() === 'true';
    }

    set isFollowed(is_followed) {
        this.element.setAttribute(DATA_IS_FOLLOWED, `${is_followed}`);
        this.followTarget.innerHTML = is_followed ? 'Unfollow' : 'Follow';
    }

    chat() {
        const headers = new Headers();
        headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));

        // const payload = {};
        // payload['user'] = this.item;
        fetch(this.chat_url, {
            method: 'GET',
            // body: payload,
            headers: headers
        }).then(function (r) {
            return r.text();
        }.bind(this)).then(function (res) {
            Turbolinks.controller.cache.put(this.chat_url, Turbolinks.Snapshot.fromHTMLString(res));
            Turbolinks.visit(this.chat_url, {action: 'restore'});
        }.bind(this));
    }

    follow() {
        const new_follow = !this.isFollowed;
        const headers = new Headers();
        headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
        headers.set('Content-Type', 'application/json');

        const payload = {};
        payload['user'] = this.item;
        payload['follow'] = new_follow;

        fetch(URL_FOLLOW, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: headers
        });

        this.isFollowed = new_follow;
    }
}