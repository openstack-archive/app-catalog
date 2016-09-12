(function() {
  'use strict';
  angular
    .module('AppCatalog')
    .controller('MainPageController', MainPageController);
  MainPageController.$inject = ['$http', '$routeParams', 'Api'];
  function MainPageController($http, $routeParams, Api) {
    var vm = this;
    $http
      .get('/api/v2/db/recent').then(function(response) {
        vm.recent = response.data;
      });
  }
})();
