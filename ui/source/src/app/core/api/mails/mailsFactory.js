import mod from 'app/core/module';
export const fullName = 'mailsFactory';

mod.factory(fullName, mailsFactory);
mailsFactory.$inject = ['$http'];

function mailsFactory($http) {
    return {
        getMails(userId) {
            return $http.get(''.concat('/api/users/', userId, '/mails'));
        }
    };
}
