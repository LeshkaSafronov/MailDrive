import mod from 'app/core/module';
export const fullName = 'logsFactory';

mod.factory(fullName, mailsFactory);
mailsFactory.$inject = ['$http'];

function mailsFactory($http) {
    return {
        getLogs() {
            return $http.get('/api/logs');
        }
    };
}
