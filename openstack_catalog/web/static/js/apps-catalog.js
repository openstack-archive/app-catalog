(function(){
  'use srict';
  var openstackReleases = ["Grizzly", "Havana", "Mitaka", "Newton"];
  var forms = {
    _common: [
      {name: "name", type: "string", required: true},
      {name: "description", type: "textarea", required: true},
      {name: "license", type: "string", required: true},
      {name: "license_url", type: "string"},
    ],
    glance_image: [
      {name: "disk_format", type: "select", options: ["qcow2", "iso"]}
    ],
    murano_package: [
      {name: "release", type: "multisel", options: openstackReleases},
    ],
    heat_template: [
      {name: "release", type: "multisel", options: openstackReleases},
    ],
    tosca_template: [
      {name: "release", type: "multisel", options: openstackReleases},
    ]
  };
  var glareUrl = "/api/v2/db";
  var glareUrlFull = window.location.protocol + "//" + window.location.host + glareUrl;
  angular
    .module("AppCatalog", ["ngRoute"])
    .filter("assetLink", function() {
      // Convert dependency into app catalog link
      return function(input) {
      var bits = input.split("/");
      return "#/assets/" + bits[2] + "/" + bits[3];
    }})
    .filter("blobLink", function() {
    // Generate link to blob
      return function(artifact, type, blobFieldName) {
        return glareUrlFull + "artifacts/" + type + "/" + artifact.id + "/" + blobFieldName;
      };
    })
    .config(function($routeProvider) {
      $routeProvider
      .when("/", {
        templateUrl: "static/html/index.html"
      })
      .when("/add", {
        templateUrl: "static/html/types.html",
        controller: "listTypesController"
      })
      .when("/add/:type", {
        templateUrl: "static/html/edit.html",
        controller: "editAssetController"
      })
      .when("/assets/:type/:id", {
        templateUrl: "static/html/asset.html",
        controller: "displayAssetController"
      })
      .when("/drafts/", {
        templateUrl: "static/html/types.html",
        controller: "listTypesController"
      })
      .when("/drafts/:type/", {
        templateUrl: "static/html/assets.html",
        controller: "listAssetsController"
      })
      .when("/edit/:type/:id", {
        templateUrl: "static/html/edit.html",
        controller: "editAssetController",
      })
      .when("/assets/:type/", {
        templateUrl: "static/html/assets.html",
        controller: "listAssetsController"
      });
    })
    .run(function($rootScope, $http) {
    // Highlight current tab
      $rootScope.$on("$locationChangeStart", function(event, next, current) {
      var nav = document.getElementById("navbar").children;
      for (var i = 0; i < nav.length; i++) {
        if (nav[i].firstChild.href == next) {
          nav[i].className = "active";
        } else {
          nav[i].className = "";
        }
      }});
    // Set proper headers for patch
    $http.defaults.headers.patch = {'Content-Type': 'application/json-patch+json'};
    })
    .controller("listTypesController", ['$scope', function($scope) {
      $scope.action = window.location.hash.search("/add") > 0 ? "add" : "drafts";
    }])
    .controller("listAssetsController", ['$scope', '$http', '$routeParams', '$location',
    function($scope, $http, $routeParams, $location) {
      $scope.type = $routeParams.type;
      var args = $location.search();
      var sort = args.sort || "name:asc";
      if (window.location.hash.search("/drafts") > 0) {
        var status = "neq:active";
        $scope.action = "edit";
      } else {
        var status = "eq:active";
        $scope.action = "assets";
      }
      var url = getApiUrl(["artifacts", $scope.type + '?status=' + status + '&sort=' + sort]);
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
    }])
    .controller("editAssetController", ["$scope", "$http", "$routeParams", "$location",
    function($scope, $http, $routeParams, $location) {
      $scope.type = $routeParams.type;
      $scope.formFields = forms._common.concat(forms[$scope.type]);
      if ($routeParams.id) {
        $http.get(getApiUrl(["artifacts", $scope.type, $routeParams.id]))
        .then(function(response){
          $scope.artifact = response.data;
        });
      } else {
        $scope.artifact = {};
        $scope.save = function(form) {
          //Create new
                };
      }
      $scope.save = function(form) {
        $scope.status = "Saving...";
        if (!$routeParams.id) {
          $http.post(getApiUrl(["artifacts", $scope.type]), $scope.artifact)
          .then(function(response){
            console.log(response);
            $scope.status = "Created";
            $scope.error = false;
          }, function(response) {
            $scope.error = response;
            $scope.status = "Error"
          });
        } else {
          var patch = [];
          angular.forEach($scope.artifact, function(value, key) {
            if (form[key] && form[key].$dirty) {
              patch.push({op: "replace", path: "/" + key, value: value});
            }
          });
          $http.patch(getApiUrl(["artifacts", $scope.type, $routeParams.id]), patch)
          .then(function(response){
            $scope.status = "Saved";
            console.log(response);
          }, function(response) {
            $scope.error = response;
         });
        }
      };
      $scope.status = false;
      $scope.error = false;
    }])
    .controller("displayAssetController", ['$scope', '$http', '$routeParams',
    function($scope, $http, $routeParams) {
      var url = getApiUrl(["artifacts", $routeParams.type, $routeParams.id]);
      $http.get(url).then(function(response) {
        $scope.item = response.data;
        $scope.type = $routeParams.type;
      });
    }]);

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
  function getApiUrl(bits) {
    var url = glareUrl;
    for (var i = 0; i < bits.length; i++) {
      url += "/" + bits[i];
    }
    return url;
  }
})();
