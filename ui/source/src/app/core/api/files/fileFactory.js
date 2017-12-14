import angular from 'angular';
import mod from 'app/core/module';
export const fullName = 'filesFactory';


mod.factory(fullName, filesFactory);
filesFactory.$inject = ['$http'];

function filesFactory($http) {
    return {
        changeAvatar(image, url) {
            let formData = new FormData();
            formData.append('image', image);

            return $http.put(url, formData, {
                transformRequest: angular.identity,
                headers: {
                    'Content-Type': undefined
                }
            });
        }
    };
}
