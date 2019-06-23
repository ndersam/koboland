import {ReconnectingWebSocket} from '../reconnecting-websocket';
import {Controller} from 'stimulus';

const CHAT_URL = 'ws://' + window.location.host + '/chat/';

/*
Message Types
 */
const CHAT_REQUEST = 10;
const ACCEPT_REQUEST = 11;
const DISMISS_REQUEST = 12;

const JOIN_ROOM = 20;
const LEAVE_ROOM = 21;
const CREATE_ROOM = 22;
const DELETE_ROOM = 23;
const ADD_TO_ROOM = 24;
const REMOVE_FROM_ROOM = 25;

const MESSAGE = 30;
const READ = 31;

const BLOCK_USER = 40;

export default class extends Controller {

    connect() {
        this.setUpWebSocket();
    }

    get chatLog() {
        return document.querySelector('#chat-log');
    }

    setUpWebSocket() {
        // let ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
        let socket = new ReconnectingWebSocket(CHAT_URL);
        socket.onmessage(function (e) {
            // let data = JSON.parse(e.data);
            // let username = data['username'];
            // let message;
            //
            // if (data['type'] === "chat_join") {
            //     message = `${username} joined\n`;
            // } else if (data['type'] === "chat_leave") {
            //     message = `${username} left\n`;
            // } else {
            //     message = `${username}: ${data['message']}\n`;
            // }
        });


    }
}