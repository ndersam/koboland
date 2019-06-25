import {Controller} from "stimulus";

const Utils = require('../utils');

const POST_URL = '/api/post/add/';
const TOPIC_URL = '/api/topic/add/';
const DATA_ITEM_CLASS = 'data-item-class';
const POST_CLASS = 'post';
const TOPIC_CLASS = 'topic';
const MAX_FILE_COUNT = 4;

export default class extends Controller {
    get fileElem() {
        return this.element.querySelector('input[type="file"]');
    }

    get preview() {
        return this.element.querySelector('input[type="file"] + div');
    }

    set preview(tag) {
        let preview = document.createElement(tag);
        this.fileElem.parentElement.appendChild(preview);
    }

    connect() {
        this.setUpURL();

        if (this.url != null) {
            this.files = [];
            this.setUpElement();
            this.setUpFileInput();
        }
    }

    get itemType() {
        return this.element.getAttribute(DATA_ITEM_CLASS);
    }

    setUpURL() {
        const itemType = this.itemType;
        this.url = null;
        if (itemType === POST_CLASS) {
            this.url = POST_URL;
        } else if (itemType === TOPIC_CLASS) {
            this.url = TOPIC_URL;
        }
    }

    setUpElement() {
        // Before post is sent
        this.element.addEventListener('submit', function (event) {
            event.preventDefault();

            const formData = new FormData(this.element);
            for (let i = 0; i < this.files.length; i++) {
                formData.set(`files[${i}]`, this.files[i]);
            }

            // AJAX request
            const headers = new Headers();
            let redirect = null;
            headers.set('X-CSRFToken', Utils.getCookie('csrftoken'));
            fetch(this.url, {
                method: 'POST',
                body: formData,
                headers: headers
            }).then(function (r) {
                redirect = r.url;
                return r.text();
            }.bind(this)).then(function (res) {
                this.reset();
                Turbolinks.controller.cache.put(redirect, Turbolinks.Snapshot.fromHTMLString(res));
                Turbolinks.visit(redirect, {action: 'restore'});
            }.bind(this));
        }.bind(this));

    }

    reset() {
        this.element.reset();
        this.fileElem.value = "";
        if (this.preview != null)
            this.preview.remove();
    }


    setUpFileInput() {
        // this.fileElem.style.opacity = 0;
        // this.fileElem.style.width = 0;
        // this.fileElem.style.height = 0;
        // this.fileElem.style.minWidth = 0;
        // this.fileElem.style.minHeight = 0;

        // Create Preview Tag
        if (this.element.querySelector('input[type="file"] + div') == null) {
            this.preview = 'div';
        }

        // Get fileTypes
        const acceptedTypes = this.fileElem.getAttribute('accept').split(',');
        this.fileTypes = acceptedTypes.map(type => type.trim());

        // Clear previous files
        this.fileElem.value = "";

        // Listen for events
        this.fileElem.addEventListener('change', this.updateFileDisplay.bind(this));
    }


    isValidFileType(file) {
        const fileTypes = this.fileTypes;
        for (let i = 0; i < fileTypes.length; i++) {
            if (file.type === fileTypes[i]) {
                return true;
            }
        }
        return false;
    }

    createImagePreview(file) {
        const listItem = document.createElement('li');
        const p = document.createElement('p');

        p.textContent = `File name ${file.name}, file size  ${Utils.getFileSize(file.size)}.`;
        let image = document.createElement('img');
        image.src = window.URL.createObjectURL(file);
        image.classList.add('img-fluid');

        listItem.appendChild(image);
        listItem.appendChild(p);
        return listItem;
    }

    createImageError(file) {
        const listItem = document.createElement('li');
        let p = document.createElement('p');
        p.textContent = `File name ${file.name}: Not a valid file type. Update your selection.`;
        listItem.appendChild(p);
        return listItem;
    }

    updateFileDisplay() {
        let preview = this.preview;
        let input = this.fileElem;

        // Clear previous `previews`
        while (preview.firstChild) {
            preview.removeChild(preview.firstChild);
        }

        let curFiles = input.files;
        let invalidFiles = [];

        if (curFiles.length === 0) {
            const p = document.createElement('p');
            p.textContent = 'No files currently selected for upload';
            preview.appendChild(p);
        } else {
            const list = document.createElement('ol');
            preview.appendChild(list);

            // Redraw previous `previews`
            for (let i = 0; i < this.files.length; i++) {
                list.appendChild(this.createImagePreview(this.files[i]));
            }

            // Preview newly added files
            let end = MAX_FILE_COUNT - this.files.length;
            for (let i = 0; i < end; i++) {
                if (this.isValidFileType(curFiles[i])) {
                    list.appendChild(this.createImagePreview(curFiles[i]));
                    this.files.push(curFiles[i]);
                } else {
                    invalidFiles.push(this.createImageError(curFiles[i]));
                }
            }

            // TODO
            for (let i = 0; i < invalidFiles.length; i++) {

            }
        }
    }
}