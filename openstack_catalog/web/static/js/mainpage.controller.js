(function() {
  'use strict';
  angular
    .module('AppCatalog')
    .controller('MainPageController', MainPageController);
  MainPageController.$inject = ['$http', '$routeParams', 'UrlService'];
  function MainPageController($http, $routeParams, UrlService) {
    var vm = this;
    $http
      .get(UrlService.getApiUrl(['recent'], {}))
      .then(function(response) {
        vm.recent = response.data;
      });
  }
})();
