(function() {
  'use strict';
  angular
    .module("AppCatalog")
    .controller("DisplayAssetController", DisplayAssetController);
  DisplayAssetController.$inject = ['$http', '$routeParams', 'UrlService'];
  function DisplayAssetController($http, $routeParams, UrlService) {
    var vm = this;
    vm.approve = approve;
    $http
      .get(UrlService.getApiUrl(["artifacts", $routeParams.type, $routeParams.id], {}))
      .then(function(response) {
        vm.item = response.data;
        vm.type = $routeParams.type;
      });
    function approve () {
      var patch = [{
        "op": "replace",
        "path": "/visibility",
        "value": "public"
      }];
      $http.patch(UrlService.getApiUrl(['artifacts', vm.type, vm.item.id], {}), patch)
      .then(function(response) {
        location.reload();
      }, function(response) {
        vm.error = response;
      });
    }
  }
})();
