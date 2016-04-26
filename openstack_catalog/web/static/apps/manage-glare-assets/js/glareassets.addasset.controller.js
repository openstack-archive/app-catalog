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
    'AssetTypesFactory'
  ];

  function addAssetController($scope, $rootScope, $http, $interpolate, $location, AssetTypesFactory) {

    $scope.asset = {};
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
    $scope.$on('$locationChangeStart', function () {
        var params = $location.search();
        if (!!params.id) {
          $scope.operation = "Edit asset";
          var t_name = {
            'MuranoPackageAsset': 'murano_packages',
            'GlanceImageAsset': 'glance_images',
            'BundleAsset': 'bundles',
            'TOSCATemplateAsset': 'tosca_templates',
            'MyArtifact': 'myartifact'
          }[params.t_name];
          var t_version = 'v' + params.t_ver;
          var assetLinkTemplate = $interpolate('/api/v2/db/artifacts/{{type}}/{{id}}/{{asset_id}}');
          $scope.assetUrl = assetLinkTemplate({
            type: t_name,
            id: t_version,
            asset_id: params.id
          });
          $http.get($scope.assetUrl)
          .success(function (data) {
            $scope.asset = data;
            $scope.loadedAsset = JSON.parse(JSON.stringify(data));
            for (var i=0; i < $scope.asset.release.length; ++i) {
              $scope.releases[$scope.asset.release[i]] = true;
            }

          });
        } else {
          $scope.asset = {};
          $scope.operation = "Add asset";
        }
      }
    );

    $scope.assetTypes = {
      types: [],
      selected: null
    };
    $scope.typeSpecific = {};


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

      if (!data.id){
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
        }).error(function(result) {
          console.log(result);
          alert('Artefact creation failed!');
        });
      } else {
        var patch_content = [];
        for(var fieldname in data) {
          if (data.hasOwnProperty(fieldname)) {
            if (!angular.equals(data[fieldname], $scope.loadedAsset[fieldname])) {
              patch_content.push({
                "op": "replace",
                "path": "/"+fieldname,
                "value": data[fieldname] || {}
              });
            }
          }
        }
        console.log(JSON.stringify(patch_content));
        $http({
          method: "PATCH",
          url: $scope.assetUrl,
          data: patch_content,
          headers: {
            "Content-Type": "application/json"
          }
        }).success(function(result) {
          $rootScope.$broadcast('assetAdded');
          console.log(result);
          alert('Artefact successfully edited!');
        }).error(function(result) {
          console.log(result);
          alert('Artefact update failed!');
        });
      }

    };
  }
})();

