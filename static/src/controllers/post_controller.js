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

export default class extends Controller {
    up_vote() {
        console.log("refresh!!!!!!!!!!", this.element.getAttribute('data-post'));

        const csrftoken = getCookie('csrftoken');
        const url = '/api-auth/post/vote/';
        const post = this.element.getAttribute('data-post');
        const headers = new Headers();
        headers.set('Content-type', 'application/json');
        headers.set('X-CSRFToken', csrftoken);

        const payload =  JSON.stringify({post_id: Number.parseInt(post)});
        console.log(payload);

        fetch(url, {
            method: "POST",
            body: payload,
            headers: headers
        }).then(r => {
            console.log(r.text());
        });

    }
}