import mod from 'app/core/main';
export const fullName = 'googleplace';

mod.directive(fullName, googleplace);

function googleplace() {
    return {
        require: 'ngModel',
        link: ($scope, $element, $attrs, model) => {
            $scope.gPlace = new google.maps.places.Autocomplete($element[0], {
                types: [],
                componentRestrictions: {}
            });

            google.maps.event.addListener($scope.gPlace, 'place_change', () => {
                $scope.$apply(() => model.$setViewValue(element.val()));
            });
        }
    };
}
