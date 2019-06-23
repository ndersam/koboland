import {Controller} from 'stimulus';

const Utils = require('../utils');

const URL_FOLLOW = '/api-auth/follow/topic/';
const DATA_TOPIC_IS_FOLLOWED = 'data-topic-is-followed';
const DATA_TOPIC_ID = 'data-topic-id';

export default class extends Controller {

    static get targets() {
        return ['follow'];
    }

    get topicId() {
        return this.element.getAttribute(DATA_TOPIC_ID);
    }


    get isFollowing() {
        return this.element.getAttribute(DATA_TOPIC_IS_FOLLOWED).toLowerCase() === 'true';
    }

    set isFollowing(is_following_topic) {
        this.element.setAttribute(DATA_TOPIC_IS_FOLLOWED, is_following_topic);
        this.followTarget.innerHTML = is_following_topic? 'Unfollow': 'Follow';
    }

    follow() {
        const toFollow = !this.isFollowing;

        const headers = new Headers();
        headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
        headers.set('Content-Type', 'application/json');

        const payload = {};
        payload['topic'] = this.topicId;
        payload['follow'] = toFollow;

        fetch(URL_FOLLOW, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: headers
        });

        this.isFollowing = !this.isFollowing;
    }

}