import angular from 'angular';
import mod from 'app/core/module';
export const fullName = 'loginView';

const TEMPLATE = require('./loginForm.html');

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$state',
        require('app/core/api/auth/authFactory').fullName,
        loginView
    ]
})

function loginView($state, AuthFactory) {
    const $ctrl = angular.extend(this, {
        login,
        $onInit
    });

    function $onInit() {
        AuthFactory.isAuth().then(() => $state.go('auth'));
    }

    function login() {
        AuthFactory.login($ctrl.user).then(data => console.log(data));
    }
}
