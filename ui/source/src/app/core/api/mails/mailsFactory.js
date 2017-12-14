import mod from 'app/core/module';
export const fullName = 'mailsFactory';

mod.factory(fullName, mailsFactory);
mailsFactory.$inject = ['$http'];

function mailsFactory($http) {
    return {
        sendMail(header, content, sender, recipient) {
            return $http.post('/api/mails');
        }
    };
}
