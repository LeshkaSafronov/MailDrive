import angular from 'angular';
import mod from 'app/core/module';
export const fullName = 'rootController';

mod.controller(fullName, RootController);

RootController.$inject = [
    '$state',
    require('app/core/api/auth/authFactory').fullName
];

function RootController($state, AuthFactory) {
    angular.extend(this, {
        $onInit
    });

    function $onInit() {
        AuthFactory.isAuth()
        .then(() => console.log('auth'))
        .catch(() => $state.go('root.login'))
        .finally(() => console.debug('Root finally!'));
    }
}