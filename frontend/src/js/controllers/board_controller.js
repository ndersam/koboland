import {Controller} from 'stimulus';

const Utils = require('../utils');

const URL_FOLLOW = '/api/board/follow/';
const URL_NEW_TOPIC = '/topic/add';
const DATA_BOARD_IS_FOLLOWED = 'data-board-is-followed';
const DATA_BOARD_ID = 'data-board-id';

export default class extends Controller {

    static get targets() {
        return ['follow', 'new_topic'];
    }

    get boardId() {
        return this.element.getAttribute(DATA_BOARD_ID);
    }

    get newTopicUrl() {
        return `${URL_NEW_TOPIC}?board=${this.boardId}`;
    }

    get isFollowing() {
        return this.element.getAttribute(DATA_BOARD_IS_FOLLOWED).toLowerCase() === 'true';
    }

    set isFollowing(is_following_board) {
        this.element.setAttribute(DATA_BOARD_IS_FOLLOWED, is_following_board);
        this.followTarget.innerHTML = is_following_board? 'Unfollow': 'Follow';
    }

    follow() {
        const toFollow = !this.isFollowing;

        const headers = new Headers();
        headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
        headers.set('Content-Type', 'application/json');

        const payload = {};
        payload['board'] = this.boardId;
        payload['follow'] = toFollow;

        fetch(URL_FOLLOW, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: headers
        });

        this.isFollowing = !this.isFollowing;
    }

    new_topic() {
        Turbolinks.visit(this.newTopicUrl);
    }
}