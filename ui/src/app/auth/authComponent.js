import anglar from 'angular';
import mod from 'app/core/module';
export const fullName = 'authView';

const TEMPLATE = require('./authForm.html');

mod.component(fullName, {
    template: TEMPLATE,
    bindings: {authUser: '<'}
});
