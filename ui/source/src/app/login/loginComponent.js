import angular from 'angular';
import mod from 'app/core/module';
import toastr from 'toastr';
export const fullName = 'loginView';

const TEMPLATE = require('./loginForm.html');

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$scope',
        '$state',
        require('app/core/api/auth/authFactory').fullName,
        loginView
    ]
})

function loginView($scope, $state, AuthFactory) {
    const $ctrl = angular.extend(this, {
        signUp,
        login,
        $onInit
    });

    function $onInit() {
        AuthFactory.isAuth().then(() => $state.go('auth'));

        // Toaster settings
        toastr.options = {
            closeButton: true,
            newestOnTop: false,
            progressBar: true,
            positionClass: 'toast-bottom-right',
            preventDuplicates: false,
            showDuration: 300,
            hideDuration: 1000,
            timeOut: 5000,
            extendedTimeOut: 1000,
            showEasing: "swing",
            hideEasing: "linear",
            showMethod: "fadeIn",
            hideMethod: "fadeOut"
        };
    }

    function login() {
        AuthFactory.login($ctrl.user)
            .then(data => console.log(data))
            .catch(reject => toastr.error(reject.data));
    }

    function signUp() {
        if (!angular.equals($ctrl.passwd.pass, $ctrl.passwd.repPass)) {
            toastr.error('Password now equal!');
            return null;
        }

        $ctrl.user.password = angular.copy($ctrl.passwd.pass);
        AuthFactory.signUp($ctrl.user)
            .then(data => console.log(data))
            .catch(reject => toastr.error(reject.data));
    }
}
