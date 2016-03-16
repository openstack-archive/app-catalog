(function () {
  "use strict";

  angular
    .module('glareassets')
    .controller('addAssetController', addAssetController);

  addAssetController.$inject = ['$scope', '$http'];

  function addAssetController($scope, $http) {
    $scope.asset_submit = function() {
      var data = angular.copy($scope.asset);

      var rebuildRelease = function(data) {
        var release = [];
        for (var key in data.releases) {
          if (data.releases.hasOwnProperty(key)) {
            if (data.releases[key]) {
              release.push(key);
            }
          }
        }
        if (release.length === 0) {
          release = ['Kilo'];
        }
        data.release = release;
      };

      var rebuildAssetTypeData = function(data) {
        var neededAssetTypeData = data[data['type_name']];
        var assetTypes = [
          'glance_images',
          'heat_templates',
          'murano_packages',
          'tosca_templates',
          'bundles'
        ];
        for (var key in assetTypes) {
          delete data[assetTypes[key]];
        }
        for (var key in neededAssetTypeData) {
          data[key] = neededAssetTypeData[key];
        }
      };

      var uploadFile = function(data) {
        var f = document.getElementById('file').files[0];
        var reader = new FileReader();
        reader.onloadend = function(e) {
          var bin_data = e.target.result;
          data['object'] = bin_data;
        };
        reader.readAsArrayBuffer(f);
      };

      var rebuildData = function(data) {
        data['type_version'] = '0.0.0';
        rebuildRelease(data);
        rebuildAssetTypeData(data);
        uploadFile(data);
      };

      rebuildData(data);

      var build_glare_url = function(data, glare_endpoint) {
        // var url = glare_endpoint;
        // if (!glare_endpoint) {
        //     url = 'http://0.0.0.0:9494';
        // }
        url = 'api/v2/artifacts/' + data['type_name'] + '/v' + data['type_version'] + '/drafts';
        return url;
      };

      var config = {'Content-Type': 'application/json'};
      var url = build_glare_url(data);

      $http.post(url, data, config)
        .then(
            function(response) {
              //success
              alert('gotcha!');
            },
            function(response) {
              //failure
              alert('hopefully!');
            }
            );
      console.log(data);
    };
  }
})();

