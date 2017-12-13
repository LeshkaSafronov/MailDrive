import mod from 'app/core/module';
export const fullName = 'authFactory';


mod.factory(fullName, ['$http', $http => {
    return {
        isAuth() {
            return $http.get('api');
        },

        login(credentials) {
            return $http.post('/api/users/login', credentials);
        },

        signUp(credentials) {
            return $http.post('/api/users/singup', credentials);
        }
    };
}]);
