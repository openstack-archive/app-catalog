(function () {
  "use strict";

  angular
    .module('glareassets')
    .controller('addAssetController', addAssetController);

  addAssetController.$inject = [
    '$scope',
    '$http',
    'AssetTypesFactory'
  ];

  function addAssetController($scope, $http, AssetTypesFactory) {
    $scope.assetTypes = {
      types: [],
      selected: null
    };
    $scope.asset = {};
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

    AssetTypesFactory.getTypes().then(function(types) {
      $scope.assetTypes.types = types;
      if ($scope.assetTypes.types.length !== 0) {
        $scope.assetTypes.selected = $scope.assetTypes.types[0];
      }
    });

    $scope.assetSubmit = function() {
      var data = angular.copy($scope.asset);
      var type = $scope.assetTypes.selected;
      var releases = [];

      angular.forEach($scope.releases, function(value, rel) {
        if (value) {
          releases.push(rel);
        }
      });

      if (releases.length === 0) {
        releases = ['Mitaka'];
      }
      data.release = releases;

      // TODO(kzaitsev): allow submitting files
      var uploadFile = function(data) {
        var f = document.getElementById('file').files[0];
        var reader = new FileReader();
        reader.onloadend = function(e) {
          data.object = e.target.result;
        };
        reader.readAsArrayBuffer(f);
      };

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
        console.log(result);
        alert('Artefact draft successfully created!');
      }).error(function(result) {
        console.log(result);
        alert('Artefact creation failed!');
      });
    };
  }
})();

