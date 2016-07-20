var app = angular.module("AppCatalog", ["ngRoute"]);

app.run(function($rootScope) {
    $rootScope.$on("$locationChangeStart", function(event, next, current) {

      var nav = document.getElementById("navbar").children;
      for(var i=0; i<nav.length; i++) {
          if (nav[i].firstChild.href == next) {
              nav[i].className = "active";
          } else {
              nav[i].className = "";
          }
      }

    })
});

app.config(function($routeProvider) {
    $routeProvider
    .when("/", {
      templateUrl: "static/html/index.html"
    })
    .when("/assets/:type/:id", {
      templateUrl: "static/html/asset.html",
      controller: "DisplayAssetController"
    })
    .when("/assets/:type/", {
      templateUrl: "static/html/assets.html",
      controller: "ListAssetsController"
    });
});

app.controller("ListAssetsController", function($scope, $http, $routeParams) {
  $scope.type = $routeParams.type;
  $http.get("/api/v2/db/artifacts/" + $scope.type + '?status=active')
    .then(function(response){
      $scope.data = response.data;
    });
});

app.controller("DisplayAssetController", function($scope, $http, $routeParams) {
  var url = "/api/v2/db/artifacts/" + $routeParams.type + "/" + $routeParams.id;
  $http.get(url).then(function(response){
    $scope.item = response.data;
  });
});
