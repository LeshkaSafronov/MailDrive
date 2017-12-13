import angular from 'angular';
import mod from 'app/core/module';
export const fullName = 'mailsView';

const TEMPLATE = require('./mailsForm.html');
const KEY_ESC = 27;

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$rootScope',
        '$state',
        '$uibModal',
        require('app/core/api/auth/authFactory').fullName,
        mailsView
    ]
});

function mailsView($rootScope, $state, $uibModal, AuthFactory) {
    const $ctrl = angular.extend(this, {
        changeSettings,
        logout,
        $onInit
    });

    function $onInit() {
        $ctrl.user = angular.copy($rootScope.user);
    }

    function logout() {
        AuthFactory.logout().then(() => $state.go('root.login'));
    }

    function changeSettings() {
        let modalInstance = $uibModal.open({
            animation: true,
            backdrop: true,
            template: require('./settingsDialogFrom.html'),
            resolve: {
                user: () => $ctrl.user
            },
            controller: ($scope, $uibModalInstance, $document, user) => {
                // Dismiss modal by keyup `ESC`
                $document.bind('keyup', $event => {
                    $event.which === KEY_ESC ? $scope.cancel() : null;
                });

                // New user settings
                $scope.user = {};
                $scope.user.name = angular.copy(user.name);
                $scope.user.subname = angular.copy(user.subname);
                $scope.user.email = angular.copy(user.email);
                $scope.user.age = angular.copy(user.age);
                $scope.user.telephone_number = angular.copy(user.telephone_number);

                $scope.cancel = () => $uibModalInstance.dismiss('cancel');
                $scope.apply = () => AuthFactory.update(user.id, $scope.user)
                    .then(() => window.location.reload());
            }
        });
        return modalInstance.result.then(() => true, () => false);
    }
}
