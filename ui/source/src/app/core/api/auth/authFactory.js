import mod from 'app/core/module';
export const fullName = 'authFactory';


mod.factory(fullName, authFactory);
authFactory.$inject = ['$http'];

function authFactory($http) {
    return {
        isAuth() {
            return $http.get('/api/users/is_auth');
        },

        login(credentials) {
            return $http.post('/api/users/login', credentials);
        },

        logout() {
            return $http.post('/api/users/logout');
        }
    };
}
