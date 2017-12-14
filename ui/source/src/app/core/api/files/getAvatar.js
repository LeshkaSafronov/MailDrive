import mod from 'app/core/module';
export const fullName = 'avatarFactory';


mod.factory(fullName, ['$http', $http => {
    return {
        getAvatar(url) {
            return $http.get(url);
        }
    };
}]);
