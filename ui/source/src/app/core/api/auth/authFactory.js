import mod from 'app/core/module';
export const fullName = 'authFactory';


mod.factory(fullName, ['$http', $http => {
    return {
        isAuth() {
            return $http.get('/api/users/is_auth');
        },

        login(credentials) {
            return $http.post('/api/users/login', credentials);
        },

        signUp(credentials) {
            return $http.post('/api/users/singup', credentials);
        },

        logout() {
            return $http.post('/api/users/logout');
        }
    };
}]);
