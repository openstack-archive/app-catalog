(function() {
  'use strict';
  var knownTypes = ['images', 'tosca_templates', 'heat_templates', 'murano_packages'];
  angular
    .module('AppCatalog')
    .controller('DisplayAssetController', DisplayAssetController);
  DisplayAssetController.$inject = ['$http', '$routeParams', 'UrlService', '$location'];
  function DisplayAssetController($http, $routeParams, UrlService, $location) {
    var vm = this;
    var deps = [];
    var dependencies = [];
    if (knownTypes.indexOf($routeParams.type) < 0) {
      $location.url('404');
    }
    vm.Approve = Approve;
    vm.Deactivate = Deactivate;
    vm.dependencies = [];
    $http
      .get(UrlService.getApiUrl(['artifacts', $routeParams.type, $routeParams.id], {}))
      .then(function(response) {
        vm.item = response.data;
        vm.type = $routeParams.type;
        deps = response.data.dependencies.slice();
        loadDependencyNames();
      }, function(response){
        if (response.status === 404) {
          $location.url('404');
        }
      });
    function loadDependencyNames() {
      if (deps.length > 0) {
        var dep = deps.pop();
        var bits = dep.split('/').slice(1);
        var url = UrlService.getApiUrl(bits, {});
        $http.get(url).then(function(response){
          dependencies.push({name: response.data.name, type: bits[1], id: response.data.id});
        });
        loadDependencyNames();
      } else {
        vm.dependencies = dependencies;
      }
    }
    function Approve() {
      Patch([{
        op: 'replace',
        path: '/visibility',
        value: 'public'
      }]);
    }
    function Deactivate() {
      Patch([{
        op: 'replace',
        path: '/status',
        value: 'deactivated'
      }]);
    }
    function Patch(data) {
      $http.patch(UrlService.getApiUrl(['artifacts', vm.type, vm.item.id], {}), data)
      .then(function(response) {
        location.reload();
      }, function(response) {
        vm.error = response;
      });
    }
  }
})();
