(function () {
  "use strict";

  //NOTE(kzaitsev): required for old js code to work nicely with angular
  angular
    .module('glareassets')
    .config(function($locationProvider) {
      $locationProvider.html5Mode(true);
    });
})();

