(function () {
  "use strict";

  angular
    .module('glareassets')
    .controller('addAssetController', addAssetController);

  addAssetController.$inject = [
    '$scope',
    '$rootScope',
    '$http',
    'AssetTypesFactory'
  ];

  function initEmptyAsset($scope) {
    $scope.fileData = {};
    $scope.asset = {};
    $scope.asset.version = "0.0.0";
    $scope.typeSpecific = {};
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

  function addAssetController($scope, $rootScope, $http, AssetTypesFactory) {

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

    initEmptyAsset($scope);

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

      $http({
        method: "POST",
        url: glareUrl,
        data: data,
        headers: {
          "Content-Type": "application/json"
        }
      }).success(function(result) {
        $rootScope.$broadcast('assetAdded');
        console.log(result);
        alert('Artefact draft successfully created!');
        initEmptyAsset($scope);
      }).error(function(result) {
        console.log(result);
        alert('Artefact creation failed!');
      });
    };
  }
})();

