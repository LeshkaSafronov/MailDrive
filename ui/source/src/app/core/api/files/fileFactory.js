import angular from 'angular';
import mod from 'app/core/module';
export const fullName = 'filesFactory';

mod.factory(fullName, ['$http', $http => {
    return {
        putUpload(file, url) {
            let fd = new FormData();
            fd.append('file', file);
            return $http.put(url, fd, {
                transformRequest: angular.identity,
                headers: {'Content-Type': undefined}
            });
        }
    };
}])
