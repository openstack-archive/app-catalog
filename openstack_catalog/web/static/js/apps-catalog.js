(function() {
  'use srict';
  var openstackReleases = ["Grizzly", "Havana", "Mitaka", "Newton"];
  var forms = {
    _common: [
      {name: "name", widget: "input", type: "text", required: true},
      {name: "version", widget: "input", type: "text", required: true},
      {name: "description", widget: "textarea", required: true},
      {name: "license", widget: "input", type: "text", required: true},
      {name: "license_url", widget: "input", type: "text"}
    ],
    glance_image: [
      {name: "disk_format", widget: "select", options: ["raw", "vhd", "vmdk", "vdi", "aki", "ari",
                                                        "ami", "qcow2", "iso"]},
      {name: "container_format", widget: "select", options: ["bare", "ovf", "aki", "ari", "ami",
                                                             "ova", "docker"]},
      {name: "min_ram", widget: "input", type: "number"},
      {name: "min_disk", widget: "input", type: "number"},
      {name: "image", widget: "blob"}
    ],
    murano_package: [
      {name: "release", type: "multisel", options: openstackReleases},
      {name: "package_name", type: "text"}
    ],
    heat_template: [
      {name: "release", type: "multisel", options: openstackReleases}
    ],
    tosca_template: [
      {name: "release", type: "multisel", options: openstackReleases},
      {name: "template_format", widget: "input", type: "text", required: true},
      {name: "template", widget: "blob"}
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
    };})
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
      .when("/add/:type", {
        templateUrl: "static/html/edit.html",
        controller: "editAssetController"
      })
      .when("/artifacts/:type/:id", {
        templateUrl: "static/html/asset.html",
        controller: "displayAssetController"
      })
      .when("/list/:visibility/:type/", {
        templateUrl: "static/html/assets.html",
        controller: "listArtifactsController"
      })
      .when("/edit/:type/:id", {
        templateUrl: "static/html/edit.html",
        controller: "editAssetController"
      });
    })
    .run(function($rootScope, $http) {
      $rootScope.$on("$locationChangeStart", function(event, next, current) {
        var nav = document.getElementById("navbar").children;
        var type = next.split('/');
        type = type[type.length - 2];
        for (var i = 0; i < nav.length; i++) {
          if (type.length > 5 && (nav[i].firstChild.href.indexOf(type) > 0)) {
            nav[i].className = "active";
          } else {
            nav[i].className = "";
          }
        }
      });
      $http.get("/auth/info").then(function(response) {
        $rootScope.auth_info = response.data;
        if ('launchpad_teams' in response.data) {
          $rootScope.logged_in = true;
          $rootScope.is_admin = response.data.launchpad_teams.indexOf('mirantis') >= 0;
        }
      });
      $http.defaults.headers.patch = {'Content-Type': 'application/json-patch+json'};
    })
    .controller("listArtifactsController", ['$scope', '$http', '$routeParams',
    '$location', '$rootScope', function($scope, $http, $routeParams, $location, $rootScope) {
      $scope.type = $routeParams.type;
      $scope.visibility = $routeParams.visibility;
      $scope.routeParams = $routeParams;
      var args = {visibility: $routeParams.visibility};
      if ($routeParams.visibility == "my") {
        $scope.action = "edit";
        $scope.visibility = "private";
        args.owner = $rootScope.auth_info.launchpad_name;
      } else {
        $scope.action = "artifacts";
        if ($scope.visibility == "private") {
          args.visibility = "private";
          $scope.action = "private";
          args.status = "eq:active";
        }
      }
      args.sort = $location.search().sort;
      args.marker = $location.search().marker;
      if (args.marker) {
        $scope.first = getUrl('#', ["list", $scope.action, $routeParams.type], {sort: args.sort});
      } else {
        $scope.first = false;
      }
      $http.get(getUrl(glareUrl, ["artifacts", $scope.type], args)).then(function(response) {
        $scope.data = response.data;
        if (response.data.next) {
          var marker = getUrlParams(response.data.next).marker;
          $scope.next = getUrl('#', ['list', $scope.action, $scope.type],
          {sort: args.sort, marker: marker});
        } else {
          $scope.next = false;
        }
      });
    }])
    .controller("editAssetController", ["$scope", "$http", "$routeParams", "$location",
    function($scope, $http, $routeParams, $location) {
      $scope.type = $routeParams.type;
      $scope.id = $routeParams.id;
      $scope.formFields = forms._common.concat(forms[$scope.type]);
      if ($scope.id) {
        $http.get(getUrl(glareUrl, ["artifacts", $scope.type, $scope.id], {}))
        .then(function(response) {
          $scope.artifact = response.data;
        });
      } else {
        $scope.artifact = {metadata: {}};
      }
      $scope.addMetadataEntry = function() {
        $scope.artifact.metadata[$scope.md_new_key] = "";
        $scope.md_new_key = "";
      }
      $scope.delMetadataEntry = function(key) {
        delete $scope.artifact.metadata[key];
      };
      $scope.save = function(form) {
        $scope.status = "Creating...";
        if (!$scope.id) {
          $http.post(getUrl(glareUrl, ["artifacts", $scope.type], {}), $scope.artifact)
          .then(function(response) {
            $scope.id = response.data.id;
            uploadBlobs($http, $scope, false);
          }, function(response) {
            $scope.error = response;
            $scope.status = "Error"
          });
        } else {
          var patch = [];
          angular.forEach($scope.artifact, function(value, key) {
            var _metadata_clean = true;
            if (form[key] && form[key].$dirty) {
              patch.push({op: "replace", path: "/" + key, value: value});
            } else if ((key.search("metadata-") == 0) && form[key].$dirty) {
              _metadata_clean = false;
            }
          });
          patch.push({op: "replace", path: "/metadata", value: $scope.artifact.metadata});
          $http.patch(getUrl(glareUrl, ["artifacts", $scope.type, $scope.id], {}), patch)
          .then(function(response){
            uploadBlobs($http, $scope, false);
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
      var url = getUrl(glareUrl, ["artifacts", $routeParams.type, $routeParams.id], {});
      $http.get(url).then(function(response) {
        $scope.item = response.data;
        $scope.type = $routeParams.type;
      });
      $scope.approve = function () {
        var patch = [{
          "op": "replace",
          "path": "/visibility",
          "value": "public"
        }];
        $http.patch(getUrl(glareUrl, ['artifacts', $scope.type, $scope.item.id], {}), patch)
        .then(function(response) {
          location.reload();
        }, function(response) {
          $scope.error = response;
        });
      };
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

  function getUrl(start, bits, args) {
    var url = start;
    for (var i = 0; i < bits.length; i++) {
      url += "/" + bits[i];
    }
    var query = []
    for (var arg in args) {
      if ('undefined' !== typeof args[arg]) {
        query.push(arg + "=" + args[arg]);
      }
    }
    if (query) {
      url += "?" + query.join("&");
    }
    return url;
  }

  function uploadBlobs($http, $scope, blobs) {
    if (blobs === false) {
      var collection = document.querySelectorAll('input[type=file]');
      var blobs = [];
      for(var i = 0; i < collection.length; i++) blobs.push(collection[i]);
    }
    if (blobs.length < 1) {
      $scope.status = "Saved";
      location.href = "#/edit/" + $scope.type + "/" + $scope.id;
      return;
    }
    var blob = blobs.pop();
    if (blob.files.length > 0) {
      var url = getUrl(glareUrl, ["artifacts", $scope.type, $scope.id, blob.name], {});
      $http.put(url, blob.files[0])
      .then(function(response) {
        uploadBlobs($http, $scope, blobs);
      }, function(response) {
        $scope.error = response;
      });
    } else {
      uploadBlobs($http, $scope, blobs);
    }
  }

})();
