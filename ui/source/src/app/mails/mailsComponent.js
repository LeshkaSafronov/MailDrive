import angular from 'angular';
import mod from 'app/core/module';
import toastr from 'toastr';
import {TOASTR_CONF} from 'app/core/conf/toastrConf';
export const fullName = 'mailsView';

const TEMPLATE = require('./mailsForm.html');
const CHANGE_AVATAR_TEMPLATE = require('./dialogsTemplates/avatarDialogForm.html');
const CHANGE_SETTINGS_TEMPLATE = require('./dialogsTemplates/settingsDialogForm.html');
const MAIL_DIALOG_TEMPLATE = require('./dialogsTemplates/mailDialogForm.html');
const SEND_DIALOG_TEMPLATE = require('./dialogsTemplates/sendMailDialogForm.html');
const KEY_ESC = 27;
const MAIL_GROUP = ['Inbox', 'Sended', 'Draft'];

mod.component(fullName, {
    template: TEMPLATE,
    controller: [
        '$rootScope',
        '$state',
        '$uibModal',
        require('app/core/api/auth/authFactory').fullName,
        require('app/core/api/files/fileFactory').fullName,
        require('app/core/api/users/usersFactory').fullName,
        require('app/core/api/mails/mailsFactory').fullName,
        mailsView
    ]
});

function mailsView(
    $rootScope,
    $state,
    $uibModal,
    AuthFactory,
    FileFactory,
    UsersFactory,
    MailsFactory
) {
    const $ctrl = angular.extend(this, {
        createMail,
        delMail,
        sendMail,
        getMailGroup,
        observeMail,
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

        MailsFactory.getMails($ctrl.user.id)
            .then(response => {
                $ctrl.mails = angular.copy(response.data);

                // Get info about sender
                $ctrl.mails.map(mail => {
                    UsersFactory.getUser(mail.sender_id)
                        .then(response => {
                            mail.avatar = response.data.avatar_url || 'assets/avatar.png';
                            mail.country = response.data.country;
                            mail.email = response.data.email;
                            mail.name = response.data.name;
                        })
                        .catch(reject => toastr.error(reject.data));
                    return mail;
                });
            })
            .catch(reject => toastr.error(reject.data));
    }

    // Logout user
    function logout() {
        AuthFactory.logout()
            .then(() => {
                $state.go('root.login');
                window.location.reload();
            })
    }

    // Return mail group
    function getMailGroup(mailGroupId) {
        return MAIL_GROUP[mailGroupId - 1];
    }

    function delMail(mailId) {
        MailsFactory.deleteMail(mailId)
            .then(() => window.location.reload())
            .catch(reject => toastr.error(reject.data));
    }

    function sendMail(mailId) {
        MailsFactory.sendMail(mailId)
            .then(() => window.location.reload())
            .catch(reject => toastr.error(reject.data));
    }

    function createMail() {
        $uibModal.open({
            animation: true,
            backdrop: true,
            template: SEND_DIALOG_TEMPLATE,
            controller: ($scope, $uibModalInstance, $document) => {
                $scope.cancel = () => $uibModalInstance.dismiss('cancel');
                $scope.send = () => {
                    MailsFactory.createMail({
                        header: $scope.theme,
                        content: $scope.mail,
                        sender_id: $ctrl.user.id,
                        recipient_id: $scope.sendTo
                    })
                        .then(() => window.location.reload())
                        .catch(reject => toastr.error(reject.data));
                    $uibModalInstance.dismiss('cancel');
                };
            }
        }).result.then(() => true, () => false);
    }

    // Open mail in dialog
    function observeMail(mail) {
        $uibModal.open({
            animation: true,
            backdrop: true,
            template: MAIL_DIALOG_TEMPLATE,
            resolve: {
                mailObj: () => mail
            },
            controller: ($scope, $uibModalInstance, $document, mailObj) => {
                // Dismiss modal by keyup `ESC`
                $document.bind('keyup', $event => {
                    angular.equals($event.which, KEY_ESC) ? $scope.cancel() : null;
                });

                $scope.mailInfo = mailObj;
                $scope.cancel = () => $uibModalInstance.dismiss('cancel');
            }
        });
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
