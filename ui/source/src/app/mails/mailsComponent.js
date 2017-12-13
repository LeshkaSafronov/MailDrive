import angular from 'angular';
import mod from 'app/core/module';
export const fullName = 'mailsView';

const TEMPLATE = require('./mailsForm.html');

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$rootScope',
        '$state',
        require('app/core/api/auth/authFactory').fullName,
        mailsView
    ]
});

function mailsView($rootScope, $state, AuthFactory) {
    const $ctrl = angular.extend(this, {
        logout,
        $onInit
    });

    function $onInit() {
        $ctrl.user = angular.copy($rootScope.user);
    }

    function logout() {
        AuthFactory.logout().then(() => $state.go('root.login'));
    }
}
