import angular from 'angular';
import mod from 'app/core/module';
import toastr from 'toastr';
import {TOASTR_CONF} from 'app/core/conf/toastrConf';
export const fullName = 'mailsView';

const TEMPLATE = require('./mailsForm.html');
const CHANGE_AVATAR_TEMPLATE = require('./dialogsTemplates/avatarDialogForm.html');
const CHANGE_SETTINGS_TEMPLATE = require('./dialogsTemplates/settingsDialogForm.html');
const MAIL_DIALOG_TEMPLATE = require('./dialogsTemplates/mailDialogForm.html');
const KEY_ESC = 27;

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$rootScope',
        '$state',
        '$uibModal',
        require('app/core/api/auth/authFactory').fullName,
        require('app/core/api/files/fileFactory').fullName,
        require('app/core/api/users/usersFactory').fullName,
        mailsView
    ]
});

function mailsView(
    $rootScope,
    $state,
    $uibModal,
    AuthFactory,
    FileFactory,
    UsersFactory
) {
    const $ctrl = angular.extend(this, {
        changeAvatar,
        changeSettings,
        logout,
        $onInit
    });

    function $onInit() {
        // Toaster settings
        toastr.options = TOASTR_CONF;

        $ctrl.user = angular.copy($rootScope.user);
        $ctrl.avatar = $ctrl.user.avatar_url || 'assets/avatar.png';
    }

    // Logout user
    function logout() {
        AuthFactory.logout()
            .then(() => {
                $state.go('root.login');
                window.location.reload();
            })
    }

    // Change user avatar
    function changeAvatar() {
        $uibModal.open({
            animation: true,
            backdrop: true,
            template: CHANGE_AVATAR_TEMPLATE,
            resolve: {
                user: () => $ctrl.user
            },
            controller: ($scope, $uibModalInstance, $document, user) => {
                // Dismiss modal by keyup `ESC`
                $document.bind('keyup', $event => {
                    angular.equals($event.which, KEY_ESC) ? $scope.cancel() : null;
                });

                $scope.cancel = () => $uibModalInstance.dismiss('cancel');
                $scope.apply = () => {
                    // Change avatar
                    FileFactory.changeAvatar(
                        $scope.imgFile, ''.concat('/api/users/', user.id, '/avatar'))
                        .then(() => window.location.reload())
                        .catch(reject => toastr.error(reject.data));
                    $uibModalInstance.dismiss('cancel');
                };
            }
        }).result.then(() => true, () => false);
    }

    // Change settings
    function changeSettings() {
        $uibModal.open({
            animation: true,
            backdrop: true,
            template: CHANGE_SETTINGS_TEMPLATE,
            resolve: {
                user: () => $ctrl.user
            },
            controller: ($scope, $uibModalInstance, $document, user) => {
                // Dismiss modal by keyup `ESC`
                $document.bind('keyup', $event => {
                    angular.equals($event.which, KEY_ESC) ? $scope.cancel() : null;
                });

                // Set user settings
                $scope.user = {
                    name: user.name,
                    subname: user.subname,
                    email: user.email,
                    age: user.age,
                    country: user.country,
                    telephone_number: user.telephone_number
                };

                $scope.cancel = () => $uibModalInstance.dismiss('cancel');
                $scope.apply = () => {
                    UsersFactory.update(user.id, $scope.user)
                        .then(() => window.location.reload())
                        .catch(reject => toastr.error(reject.data));
                };
            }
        }).result.then(() => true, () => false);
    }
}
