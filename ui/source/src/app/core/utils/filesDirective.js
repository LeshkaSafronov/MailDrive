import mod from 'app/core/main';
export const fullName = 'fileModel';

mod.directive(fullName, fileModel);
fileModel.$inject = ['$parse'];

function fileModel($parse) {
    return {
        restrict: 'A',
        link: ($scope, $element, $attrs) => {
            $element.bind('change', () => {
                $scope.$apply(() => {
                    $parse($attrs.fileModel).assign($scope, $element[0].files[0]);
                });
            });
        }
    };
}
