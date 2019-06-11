const Turbolinks = require("turbolinks");
const Bootstrap = require('bootstrap');
import {Application} from "stimulus";
import {definitionsFromContext} from "stimulus/webpack-helpers";

Turbolinks.start();
const application = Application.start();
const context = require.context('../controllers', true, /\.js$/);
application.load(definitionsFromContext(context));

import jQuery from "jquery";
window.$ = window.$ || jQuery;

