import './main.sass';
import './vendor.css';

import angular from 'angular';
import 'angular-sanitize';
import 'angular-ui-bootstrap';
import 'angular-ui-router';
import 'angular-bootstrap-datetimepicker';
import 'angular-bootstrap-datetimepicker-template';
import 'angular-cookies';

// Create application
const mainModule = angular.module('mail.drive', [
    'ngCookies',
    'ui.bootstrap',
    'ui.router',
    'ui.bootstrap.datetimepicker',
    'ngSanitize'
]);

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
mainModule.config(['$stateProvider', $stateProvider => {
    console.log($stateProvider);
}]);

angular.element(document).ready(() => {
    angular.bootstrap(document, [mainModule.name]);
});
