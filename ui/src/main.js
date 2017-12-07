import './main.sass';
import './vendor.css';

import angular from 'angular';
import 'angular-sanitize';
import 'angular-ui-bootstrap';
import 'angular-ui-router';
import 'angular-bootstrap-datetimepicker';
import 'angular-bootstrap-datetimepicker-template';
import 'angular-cookies';

// Import components controller
import * as RootController from 'app/core/root/rootController';

// Create application
const mainModule = angular.module('mail.drive', [
    require('app/core/main').default.name
])
.config(configFn)
.config(routerFn);

// Configurate app
configFn.$inject = [
    '$uibTooltipProvider',
    '$httpProvider',
    '$uibModalProvider'
];

function configFn($uibTooltipProvider, $httpProvider, $uibModalProvider) {
    $uibModalProvider.options = false;
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.withCredentials = true;
    $uibTooltipProvider.options({
        popupDelay: 500
    });
}

// Configurate router
routerFn.$inject = [
    '$stateProvider',
    '$urlRouterProvider'
];

function routerFn($stateProvider, $urlRouterProvider) {
    // Converts component name to html tags
    const componentNameToHtml = fullName => {
        let tagName = fullName.replace(/[A-Z]/g, (letter, pos) => {
            return (pos ? '-' : '') + letter.toLowerCase();
        });
        return `<${tagName}></${tagName}>`
    };

    // Add state to provider
    const createState = (name, params={}) => {
        let views = params.views || {'': params};
        Object.keys(views).forEach(key => {
            let view = views[key];
            if (!view.template && view.component) {
                if (!view.component.fullName) {
                    throw new Error('Ups! no fullName for: ', name);
                }
                view.template = componentNameToHtml(view.component.fullName);
            }
        });
        $stateProvider.state(name, params);
    };
}

angular.element(document).ready(() => {
    angular.bootstrap(document, [mainModule.name]);
});

