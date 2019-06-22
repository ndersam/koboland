import {Controller} from "stimulus";

const Utils = require('../utils');

const LIKE = 1;
const DISLIKE = -1;
const NO_VOTE = 0;
const SHARE = 2;
const UNSHARE = -2;
const URL = '/api-auth/vote/';
const URL_POST = '/comment/';

const POST_CLASS = 'post';
const TOPIC_CLASS = 'topic';
const DATA_ITEM_CLASS = 'data-item-class';
const DATA_ITEM_ID = 'data-item-id';
const DATA_ITEM_VOTE_STATE = 'data-item-vote-state';
const DATA_ITEM_LIKE_COUNT = 'data-item-like-count';
const DATA_ITEM_DISLIKE_COUNT = 'data-item-dislike-count';
const DATA_ITEM_SHARE_COUNT = 'data-item-share-count';
const DATA_ITEM_SHARED = 'data-item-shared';

const CHECKED_STATE_CLASS = 'btn-toggled';

export default class extends Controller {

    static get targets() {
        return ["like", "dislike", "share", "likeCount", "dislikeCount", "shareCount", "topic"];
    }

    get vote_type() {
        return Number.parseInt(this.element.getAttribute(DATA_ITEM_VOTE_STATE));
    }

    set vote_type(vote_type) {
        this.element.setAttribute(DATA_ITEM_VOTE_STATE, vote_type);
    }

    get item() {
        return this.element.getAttribute(DATA_ITEM_ID);
    }

    get likeCount() {
        return Number.parseInt(this.element.getAttribute(DATA_ITEM_LIKE_COUNT));
    }

    set likeCount(likes) {
        this.element.setAttribute(DATA_ITEM_LIKE_COUNT, likes);
        this.showVotes(this.likeCountTarget, likes);
    }

    get dislikeCount() {
        return Number.parseInt(this.element.getAttribute(DATA_ITEM_DISLIKE_COUNT));
    }

    set dislikeCount(dislikes) {
        this.element.setAttribute(DATA_ITEM_DISLIKE_COUNT, dislikes);
        this.showVotes(this.dislikeCountTarget, dislikes);
    }

    get is_shared() {
        return Number.parseInt(this.element.getAttribute(DATA_ITEM_SHARED)) === 1;
    }

    set is_shared(is_shared) {
        this.element.setAttribute(DATA_ITEM_SHARED, is_shared ? '1' : '0');
        if (is_shared) {
            this.shareCount++;
        } else if (this.shareCount > 0) {
            this.shareCount--;
        }
    }

    get shareCount() {
        return Number.parseInt(this.element.getAttribute(DATA_ITEM_SHARE_COUNT));
    }

    get topicID() {
        return this.topicTarget.getAttribute(DATA_ITEM_ID);
    }

    set shareCount(shares) {
        this.element.setAttribute(DATA_ITEM_SHARE_COUNT, shares);
        this.showVotes(this.shareCountTarget, shares);
    }

    showVotes(element, votes) {
        if (votes > 0) {
            element.innerHTML = `${votes}`;
        } else {
            element.innerHTML = '';
        }
    }

    connect() {
        if (this.element.getAttribute(DATA_ITEM_CLASS) === POST_CLASS) {
            this.votable_type = POST_CLASS;
        } else {
            this.votable_type = TOPIC_CLASS;
        }
    }

    vote(vote_type) {
        const headers = new Headers();
        headers.set('Content-type', 'application/json');
        headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));

        const payload = {};
        payload['votable_id'] = this.item;
        payload['votable_type'] = this.votable_type;
        payload['vote_type'] = vote_type;


        fetch(URL, {
            method: 'POST',
            body: JSON.stringify(payload),
            headers: headers
        });
    }

    like() {
        let newVote = undefined;
        if (this.vote_type === NO_VOTE) {
            // NO_VOTE to LIKE
            this.likeCount++;
            newVote = LIKE;
        } else if (this.vote_type === LIKE) {
            // LIKE to NO_VOTE
            this.likeCount--;
            newVote = NO_VOTE;
        } else if (this.vote_type === DISLIKE) {
            // DISLIKE to LIKE
            this.dislikeCount--;
            this.likeCount++;
            newVote = LIKE;
        } else {
            // null to LIKE
            this.likeCount++;
            newVote = LIKE;
        }

        if (newVote !== undefined) {
            this.vote(newVote);
            this.vote_type = `${newVote}`;
            this.updateDisplay(newVote);
        }
    }

    updateDisplay(newVote) {
        switch (newVote) {
            case LIKE:
                this.likeTarget.classList.add(CHECKED_STATE_CLASS);
                this.dislikeTarget.classList.remove(CHECKED_STATE_CLASS);
                break;
            case DISLIKE:
                this.likeTarget.classList.remove(CHECKED_STATE_CLASS);
                this.dislikeTarget.classList.add(CHECKED_STATE_CLASS);
                break;
            case NO_VOTE:
                this.likeTarget.classList.remove(CHECKED_STATE_CLASS);
                this.dislikeTarget.classList.remove(CHECKED_STATE_CLASS);
                break;
        }
    }

    dislike() {
        let newVote = undefined;
        if (this.vote_type === NO_VOTE) {
            // NO_VOTE to DISLIKE
            this.dislikeCount++;
            newVote = DISLIKE;
        } else if (this.vote_type === DISLIKE) {
            // DISLIKE to NO_VOTE
            this.dislikeCount--;
            newVote = NO_VOTE;
        } else if (this.vote_type === LIKE) {
            // LIKE to DISLIKE
            this.likeCount--;
            this.dislikeCount++;
            newVote = DISLIKE;
        } else {
            // null to DISLIKE
            this.dislikeCount++;
            newVote = DISLIKE;
        }

        if (newVote !== undefined) {
            this.vote(newVote);
            this.vote_type = newVote;
            this.updateDisplay(newVote);
        }
    }

    share() {
        const newState = !this.is_shared;
        this.vote(newState ? SHARE : UNSHARE);
        this.is_shared = newState;
        if (this.is_shared) {
            this.shareTarget.classList.add(CHECKED_STATE_CLASS);
        } else {
            this.shareTarget.classList.remove(CHECKED_STATE_CLASS);
        }
    }

    quote() {
        if (this.votable_type === TOPIC_CLASS) {
            Turbolinks.visit(`${URL_POST}?topic=${this.item}&quote_topic=1`);
        } else {
            Turbolinks.visit(`${URL_POST}?topic=${this.element.getAttribute('data-topic-id')}&post=${this.item}`);
        }
    }

}