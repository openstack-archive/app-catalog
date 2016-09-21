(function() {
  'use strict';
  angular
    .module('AppCatalog', ['ngRoute'])
    .filter('blobSize', function() {
      return function(bytes) {
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) {
          return '-';
        }
        var units = ['bytes', 'K', 'M', 'G', 'T', 'P'];
        var number = Math.floor(Math.log(bytes) / Math.log(1024));
        return (bytes / Math.pow(1024, Math.floor(number))).toFixed(2) + units[number];
      };
    })
    .filter('assetLink', function() {
      return function(data) {
        return '#/artifacts/' + data.type + '/' + data.id;
      };
    })
    .filter('blobLink', function() {
      return function(artifact, type, blobFieldName) {
        return GLARE_URL + '/artifacts/' + type + '/' + artifact.id + '/' + blobFieldName;
      };
    })
    .filter('displayName', function() {
      return function(name) {
        name = name[0].toUpperCase() + name.substring(1);
        return name.replace('_', ' ');
      };
    })
    .config(function($routeProvider, $httpProvider) {
      $routeProvider
      .when('/', {
        templateUrl: 'static/html/index.html',
        controllerAs: 'vm',
        controller: 'MainPageController'
      })
      .when('/add/:type', {
        templateUrl: 'static/html/edit.html',
        controllerAs: 'vm',
        controller: 'EditAssetController'
      })
      .when('/artifacts/:type/:id', {
        templateUrl: 'static/html/asset.html',
        controllerAs: 'vm',
        controller: 'DisplayAssetController'
      })
      .when('/private/:type/:id', {
        templateUrl: 'static/html/asset.html',
        controllerAs: 'vm',
        controller: 'DisplayAssetController'
      })
      .when('/list/:visibility/:type/', {
        templateUrl: 'static/html/assets.html',
        controllerAs: 'vm',
        controller: 'ListAssetsController'
      })
      .when('/edit/:type/:id', {
        templateUrl: 'static/html/edit.html',
        controllerAs: 'vm',
        controller: 'EditAssetController'
      })
      .otherwise({
        template: '<h1>404</h1>'
      });
      $httpProvider.defaults.withCredentials = true;
    })
    .run(function($rootScope, $http) {
      $rootScope.$on('$locationChangeStart', function(event, next, current) {
        $rootScope.error = false;
        var nav = document.getElementById('navbar').children;
        var type = next.split('/');
        type = type[type.length - 2];
        for (var i = 0; i < nav.length; i++) {
          if (type.length > 5 && (nav[i].firstChild.href.indexOf(type) > 0)) {
            nav[i].className = 'active';
          } else {
            nav[i].className = '';
          }
        }
      });
      $http.get('/auth/info').then(function(response) {
        $rootScope.auth_info = response.data;
        if ('launchpad_teams' in response.data) {
          $rootScope.logged_in = true;
          $rootScope.is_admin = LAUNCHPAD_ADMIN_GROUPS.filter(function(group) {
            return response.data.launchpad_teams.indexOf(group) >= 0;
          }).length > 0;
        }
      });
      $http.defaults.headers.patch = {'Content-Type': 'application/json-patch+json'};
    });
})();
