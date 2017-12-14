import mod from 'app/core/main';

mod.directive('fileModel', ['$parse', $parse => {
    return {
        restrict: 'A',
        link: ($scope, $elem, $attrs) => {
            let model = $parse($attrs.fileModel);
            let modelSetter = model.assign;

            $elem.bind('change', () => {
                $scope.$apply(() => {
                    modelSetter($scope, $elem[0].files[0]);
                });
            });
        }
    };
}]);
