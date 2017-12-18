import mod from 'app/core/module';
export const fullName = 'usersFactory';

mod.factory(fullName, usersFactory);
usersFactory.$inject = ['$http'];

function usersFactory($http) {
    return {
        signUp(credentials) {
            return $http.post('/api/users/singup', credentials);
        },

        update(userMail, credentials) {
            return $http.put('/api/users/'.concat(userMail), credentials);
        },

        getUser(userId) {
            return $http.get('/api/users/'.concat(userId));
        }
    };
}
