(function() {
  'use strict';
  angular
    .module("AppCatalog")
    .controller("ListAssetsController", ListAssetsController);
  ListAssetsController.$inject = ['$http', '$routeParams', '$location', '$rootScope', 'UrlService'];
  function ListAssetsController($http, $routeParams, $location, $rootScope, UrlService) {
    var vm = this;
    vm.type = $routeParams.type;
    vm.visibility = $routeParams.visibility;
    vm.routeParams = $routeParams;
    var args = {visibility: $routeParams.visibility};
    if ($routeParams.visibility == "my") {
      vm.action = "edit";
      args.visibility = "private";
      args.owner = $rootScope.auth_info.launchpad_name;
    } else {
      vm.action = "artifacts";
      if (vm.visibility == "private") {
        args.visibility = "private";
        vm.action = "private";
        args.status = "eq:active";
      }
    }
    args.sort = $location.search().sort;
    if (!args.sort) {
        args.sort = "name:asc";
    }
    args.marker = $location.search().marker;
    if (args.marker) {
      vm.first = UrlService.getUrl('#', ["list", vm.visibility, $routeParams.type], {sort: args.sort});
    } else {
      vm.first = false;
    }
    $http.get(UrlService.getApiUrl(["artifacts", vm.type], args)).then(function(response) {
      vm.data = response.data;
      if (response.data.next) {
        var marker = getUrlParams(response.data.next).marker;
        vm.next = UrlService.getUrl('#', ['list', vm.visibility, vm.type],
        {sort: args.sort, marker: marker});
      } else {
        vm.next = false;
      }
    });
  }
  function getUrlParams(url) {
    // Parse URL params into dictionary
    var params = {};
    var pairs = url.split("?")[1].split("&");
    for (var i = 0; i < pairs.length; i++) {
      var pair = pairs[i].split("=");
      params[pair[0]] = decodeURIComponent(pair[1]);
    }
    return params;
  }
})();
