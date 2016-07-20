var apiUrl = "/api/v2/db/artifacts/";
var app = angular.module("AppCatalog", ["ngRoute"]);

// Convert dependency into app catalog link
app.filter("assetLink", function() {
  return function(input) {
    var bits = input.split("/");
    return "#/assets/" + bits[2] + "/" + bits[3];
  };
});

// Generate link to blob
app.filter("blobLink", function() {
  return function(artifact, type, blob_field_name) {
    return window.location.protocol + "//" + window.location.host + "/api/v2/db/artifacts/" + type + "/" + artifact.id + "/" + blob_field_name;
  }
});

// Highlight current tab
app.run(function($rootScope) {
  $rootScope.$on("$locationChangeStart", function(event, next, current) {
    var nav = document.getElementById("navbar").children;
    for (var i = 0; i < nav.length; i++) {
      if (nav[i].firstChild.href == next) {
        nav[i].className = "active";
      } else {
        nav[i].className = "";
      }
    }
  });
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

// Parse URL params into dictionary
function getUrlParams(url) {
  var params = {};
  var pairs = url.split("?")[1].split("&");
  for (var i = 0; i < pairs.length; i++) {
    var pair = pairs[i].split("=");
    params[pair[0]] = decodeURIComponent(pair[1]);
  }
  return params;
}

app.controller("ListAssetsController", function($scope, $http, $routeParams, $location) {
  $scope.type = $routeParams.type;
  var args = $location.search();
  var sort = args.sort || "name:asc";
  var url = apiUrl + $scope.type + '?status=active&sort=' + sort;
  if (args.marker) {
    url += '&marker=' + args.marker;
    $scope.first = "#/assets/" + $scope.type + "/?sort=" + sort;
  } else {
    $scope.first = false;
  }
  $http.get(url).then(function(response) {
    $scope.data = response.data;
    if (response.data.next) {
      var marker = getUrlParams(response.data.next).marker;
      $scope.next = "#/assets/" + $scope.type + "/?sort=" + sort + "&marker=" + marker;
    } else {
      $scope.next = false;
    }
  });
});

app.controller("DisplayAssetController", function($scope, $http, $routeParams) {
  var url = "/api/v2/db/artifacts/" + $routeParams.type + "/" + $routeParams.id;
  $http.get(url).then(function(response) {
    $scope.item = response.data;
    $scope.type = $routeParams.type;
  });
});
