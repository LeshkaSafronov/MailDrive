import angular from 'angular';
import mod from 'app/core/module';
import toastr from 'toastr';
import {TOASTR_CONF} from 'app/core/conf/toastrConf';
export const fullName = 'loginView';

const TEMPLATE = require('./loginForm.html');

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$scope',
        '$state',
        require('app/core/api/auth/authFactory').fullName,
        require('app/core/api/users/usersFactory').fullName,
        loginView
    ]
})

function loginView($scope, $state, AuthFactory, UserFactory) {
    const $ctrl = angular.extend(this, {
        signUp,
        login,
        $onInit
    });

    function $onInit() {
        // Toaster settings
        toastr.options = TOASTR_CONF;

        // Check auth
        AuthFactory.isAuth()
            .then(() => $state.go('root.auth.mails'))
            .catch(() => $state.go('root.login'));
    }

    // Login user
    function login() {
        AuthFactory.login($ctrl.user)
            .then(data => $state.go('root.auth.mails'))
            .catch(reject => toastr.error(reject.data));
    }
     // Sign up new user
    function signUp() {
        if (!angular.equals($ctrl.passwd.pass, $ctrl.passwd.repPass)) {
            toastr.error('Password now equal!');
            return null;
        }

        $ctrl.user.password = angular.copy($ctrl.passwd.pass);
        UserFactory.signUp($ctrl.user)
            .then(data => $state.go('root.auth.mails'))
            .catch(reject => toastr.error(reject.data));
    }
}
