import mod from 'app/core/module';
export const fullName = 'mailsFactory';

mod.factory(fullName, mailsFactory);
mailsFactory.$inject = ['$http'];

function mailsFactory($http) {
    return {
        createMail(mail) {
            return $http.post('/api/mails', mail);
        },

        getMails(userMail) {
            return $http.get(''.concat('/api/users/', userMail, '/mails'));
        },

        sendMail(mailId) {
            return $http.post(''.concat('/api/mails/', mailId, '/send'));
        },

        deleteMail(mailId) {
            return $http.delete(''.concat('/api/mails/', mailId));
        },

        getMailFiles(mailId) {
            return $http.get(''.concat('/api/mails/', mailId, '/files'));
        }
    };
}
