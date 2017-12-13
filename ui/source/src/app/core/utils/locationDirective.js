import mod from 'app/core/main';

mod.directive('googleplace', () => {
    return {
        require: 'ngModel',
        link: (scope, element, attrs, model) => {
            let options = {
                types: [],
                componentRestrictions: {}
            };
            scope.gPlace = new google.maps.places.Autocomplete(element[0], options);

            google.maps.event.addListener(scope.gPlace, 'place_changed', () => {
                scope.$apply(() => model.$setViewValue(element.val()));
            });
        }
    }
});
