(function() {
  'use strict';
  angular
    .module("AppCatalog")
    .controller("ListAssetsController", ListAssetsController);
  ListAssetsController.$inject = ['$http', '$routeParams', '$location', '$rootScope', 'Api'];
  function ListAssetsController($http, $routeParams, $location, $rootScope, Api) {
    var vm = this;
    vm.type = $routeParams.type;
    vm.visibility = $routeParams.visibility;
    vm.routeParams = $routeParams;
    var args = {visibility: $routeParams.visibility, status: 'eq:active'};
    if ($routeParams.visibility == "my") {
      vm.action = "edit";
      args.visibility = "private";
      delete args.status;
      args.owner = $rootScope.auth_info.nickname;
    } else {
      vm.action = "artifacts";
      if (vm.visibility == "private") {
        args.visibility = "private";
        args.status = "eq:active";
        vm.action = "private";
      } else {
        args.version = "latest";
      }
    }
    args.sort = $location.search().sort;
    if (!args.sort) {
      args.sort = "name:asc";
    }
    args.marker = $location.search().marker;
    if (args.marker) {
      vm.first = Api.getUrl('#', ["list", vm.visibility, $routeParams.type],
                            {sort: args.sort});
    } else {
      vm.first = false;
    }
    $http.get(Api.getApiUrl(["artifacts", vm.type], args)).then(function(response) {
      vm.data = response.data;
      if (response.data.next) {
        var marker = getUrlParams(response.data.next).marker;
        vm.next = Api.getUrl('#', ['list', vm.visibility, vm.type],
        {sort: args.sort, marker: marker});
      } else {
        vm.next = false;
      }
    });
  }
  function getUrlParams(url) {
    var params = {};
    var pairs = url.split("?")[1].split("&");
    for (var i = 0; i < pairs.length; i++) {
      var pair = pairs[i].split("=");
      params[pair[0]] = decodeURIComponent(pair[1]);
    }
    return params;
  }
})();
