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

    AssetTypesFactory.getTypes().then(function(types) {
      $scope.assetTypes.types = types;
      if ($scope.assetTypes.types.length !== 0) {
        $scope.assetTypes.selected = $scope.assetTypes.types[0];
      }
    });

    $scope.assetSubmit = function() {
      console.log($scope);
      var data = angular.copy($scope.asset);
      var type = $scope.assetTypes.selected;

      var rebuildRelease = function(data) {
        var release = [];
        angular.forEach(data.releases, function(rel) {
          if (data.releases[rel]) {
            release.push(rel);
          }
        });
        if (release.length === 0) {
          release = ['Kilo'];
        }
        data.release = release;
      };

      var uploadFile = function(data) {
        var f = document.getElementById('file').files[0];
        var reader = new FileReader();
        reader.onloadend = function(e) {
          data.object = e.target.result;
        };
        reader.readAsArrayBuffer(f);
      };

      var rebuildData = function(data) {
        rebuildRelease(data);
        // uploadFile(data);
      };
      rebuildData(data);

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
      }).error(function(result) {
        console.log(result);
        alert('Artefact creation failed!');
      });
    };
  }
})();

