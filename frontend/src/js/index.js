const Turbolinks = require("turbolinks");
const Bootstrap = require('bootstrap');
import {Application} from "stimulus";
import {definitionsFromContext} from "stimulus/webpack-helpers";
import jQuery from "jquery";

Turbolinks.start();
const application = Application.start();
const context = require.context('./controllers', true, /\.js$/);
application.load(definitionsFromContext(context));

window.$ = window.$ || jQuery;

