import anglar from 'angular';
import mod from 'app/core/module';
export const fullName = 'authView';

const TEMPLATE = require('./authForm.html');

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$state',
        '$rootScope',
        require('app/core/api/auth/authFactory').fullName,
        authView
    ]
});

function authView($state, $rootScope, AuthFactory) {
    const $ctrl = angular.extend(this, {
        $onInit
    });

    function $onInit() {
        AuthFactory.isAuth()
            .then(response => $rootScope.user = angular.copy(response.data))
            .catch(() => $state.go('root.login'));
    }
}
