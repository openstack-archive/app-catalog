(function () {
  "use strict";

  //NOTE(kzaitsev): required for old js code to work nicely with angular
  angular
    .module('glareassets')
    .config( ['$provide', function ($provide) {
      $provide.decorator('$browser', ['$delegate', function ($delegate) {
        $delegate.onUrlChange = function () {};
        $delegate.url = function () {
          return "";
        };
        return $delegate;
      }]);
    }])
    .config(function($locationProvider) {
      $locationProvider.html5Mode({
        enabled: false,
        requireBase: false,
        rewriteLinks: false
      });
    });
})();

