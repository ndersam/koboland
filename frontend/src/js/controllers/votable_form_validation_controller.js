import {Controller} from "stimulus";

const DATA_VALIDATE_CLASS = 'data-validate';
const DATA_ITEM_CLASS = 'data-item-class';
const TOPIC = 'topic';
const POST = 'post';


export default class extends Controller {

    get btnSubmit() {
        return this.element.querySelector('button');
    }

    shouldEnableSubmit() {
        const title = this.element.querySelector('input[name="title"]');
        if (title !== null && title.value.length === 0) {
            return false;
        }

        const board = this.element.querySelector('select[name="board"]');
        if (board !== null && board.options[board.selectedIndex].value.length === 0) {
            return false;
        }

        const content = this.element.querySelector('textarea[name="content"]');
        const files = this.element.querySelector('input[name="files"]');
        if (content.value.length === 0 && files.files.length === 0) {
            return false;
        }

        return true;
    }

    connect() {
        this.addBlurListener();
        this.addFormChangesListeners();
        this.setSubmitButtonState();
    }

    isTargetElement(event) {
        let form = event.target.form;
        return form !== undefined && form.hasAttribute(DATA_VALIDATE_CLASS);
    }

    addBlurListener() {
        document.addEventListener('blur', function (event) {

            if (!this.isTargetElement(event)) {
                return;
            }

            // Validate the field
            let error = event.target.validity;
            console.log(error);

        }.bind(this), true);
    }

    addFormChangesListeners() {
        document.addEventListener('keyup', function (event) {
            if (!this.isTargetElement(event)) {
                return;
            }
            this.setSubmitButtonState();
        }.bind(this), true);

        document.addEventListener('change', function (event) {
            if (!this.isTargetElement(event)) {
                return;
            }
            if (event.target.getAttribute('type') === 'file' || event.target.getAttribute('name') === 'board') {
                this.setSubmitButtonState();
            }
        }.bind(this), true);
    }

    setSubmitButtonState() {
        this.btnSubmit.disabled = !this.shouldEnableSubmit();
    }
}