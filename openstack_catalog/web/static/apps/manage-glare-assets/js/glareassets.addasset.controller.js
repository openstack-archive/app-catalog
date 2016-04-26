(function () {
  //"use strict";

  angular
    .module('glareassets')
    .controller('addAssetController', addAssetController);

  addAssetController.$inject = [
    '$scope',
    '$rootScope',
    '$http',
    '$interpolate',
    '$location',
    '$cookies',
    'AssetTypesFactory'
  ];

  function initEmptyAsset($scope) {
    $scope.fileData = {};
    $scope.asset = {};
    $scope.asset.version = "0.0.0";
    $scope.typeSpecific = {};
    $scope.loadedAsset = {};
    $scope.operation = "Add asset";
    $scope.releases = {
      'Austin': false,
      'Bexar': false,
      'Cactus': false,
      'Diablo': false,
      'Essex': false,
      'Folsom': false,
      'Grizzly': false,
      'Havana': false,
      'Icehouse':false,
      'Juno':false,
      'Kilo': false,
      'Liberty': false,
      'Mitaka': false,
      'Newton': false,
      'Ocata': false
    };
  }

  function addAssetController($scope, $rootScope, $http, $interpolate, $location, $cookies, AssetTypesFactory) {
    $scope.$on('$locationChangeStart', function () {
        initEmptyAsset($scope);
        var asset_id = $cookies.asset_id;
        if (!!asset_id) {
          var asset_version = $cookies.asset_version;
          var asset_name = $cookies.asset_name;
          $scope.operation = "Edit asset";
          var t_name = {
            'MuranoPackageAsset': 'murano_packages',
            'GlanceImageAsset': 'glance_images',
            'BundleAsset': 'bundles',
            'TOSCATemplateAsset': 'tosca_templates',
            'MyArtifact': 'myartifact'
          }[asset_name];
          var t_version = 'v' + asset_version;
          var assetLinkTemplate = $interpolate('/api/v2/db/artifacts/{{type}}/{{id}}/{{asset_id}}');
          $scope.assetUrl = assetLinkTemplate({
            type: t_name,
            id: t_version,
            asset_id: asset_id
          });
          $http.get($scope.assetUrl)
          .success(function (data) {
            $scope.asset = data;
            $scope.loadedAsset = JSON.parse(JSON.stringify(data));
            for (var i=0; i < $scope.asset.release.length; ++i) {
              $scope.releases[$scope.asset.release[i]] = true;
            }
            delete $scope.asset['id'];
            delete $scope.asset['type_name'];
            delete $scope.asset['deleted_at'];
            delete $scope.asset['created_at'];
            delete $scope.asset['published_at'];
            delete $scope.asset['depends'];
            delete $scope.asset['type_version'];
            delete $scope.asset['updated_at'];
            $cookies.asset_id = '';

          });
        } else {
          $scope.operation = "Add asset";
        }
      }
    );

    $scope.assetTypes = {
      types: [],
      selected: null
    };

    AssetTypesFactory.getTypes().then(function(types) {
      $scope.assetTypes.types = types;
      if ($scope.assetTypes.types.length !== 0) {
        $scope.assetTypes.selected = $scope.assetTypes.types[0];
      }
    });
    
    $scope.$watch('asset', function () {
      $scope.assetTypes.selected = $scope.assetTypes.types.filter(function (item) {
        return item.name == $scope.asset.type_name + ": v" + $scope.asset.type_version;
      })[0];
    });




    $scope.assetSubmit = function() {
      var data = angular.copy($scope.asset);
      var type = $scope.assetTypes.selected;
      var releases = [];

      if (!$scope.separateSupportedBy) {
        data.supported_by = data.provided_by;
      }

      angular.forEach($scope.releases, function(value, rel) {
        if (value) {
          releases.push(rel);
        }
      });

      if (releases.length === 0) {
        releases = ['Mitaka'];
      }
      data.release = releases;

      // Add type-specific data to asset info
      angular.forEach($scope.typeSpecific[type.type], function(value, key) {
        data[key] = value;
      });

      var glareUrl = '/api/v2/db/artifacts/' + type.type + '/' + type.id + '/drafts';
      var dataToSend = JSON.stringify(data);

      console.log(dataToSend);
      console.log($scope.fileData);
      $http({
          method: "POST",
          url: glareUrl,
          data: data,
          headers: {
            "Content-Type": "application/json"
          }
        })
        .success(function(result) {
          $rootScope.$broadcast('assetAdded');
          console.log(result);
          var glareBlobUrl = '/api/v2/db/artifacts/' + type.type + '/' + type.id + '/' + result.id + '/stored_object';
          console.log(glareBlobUrl);
          var blobMessage = '';

          // also upload the binary if it's there
          if (data.stored) {
            $http({
              method: "PUT",
              url: glareBlobUrl,
              data: $scope.fileData.assetFile.data,
              headers: {
                "Content-Type": "application/octet-stream"
              }
            }).success(function(blobResult) {
              console.log(blobResult);
              blobMessage = 'Binary has been uploaded successfully.';
            }).error(function(blobResult) {
              console.log(blobResult);
              blobMessage = 'There was an error uploading the binary.';
            });
        }
          alert('Artefact draft successfully created. ' + blobMessage);
          initEmptyAsset($scope);
        }).error(function(result) {
          console.log(result);
          alert('Artefact creation failed.');
        });
    }
  }
})();

