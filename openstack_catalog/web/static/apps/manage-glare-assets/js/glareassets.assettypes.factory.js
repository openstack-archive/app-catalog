(function () {
  'use strict';

  angular
    .module('glareassets')
    .factory('AssetTypesFactory', AssetTypesFactory);

  AssetTypesFactory.$inject = ['$http'];

  function AssetTypesFactory($http) {

    // A factory that returns a list of artifact types

    return {
      getTypes: getTypes
    };

    function getTypes() {
      var assetTypesURL = '/api/v2/db/artifacts';
      var types = [];

      return $http.get(assetTypesURL).then(function (result) {
        var data = result.data;
        var assetTypes = data.artifact_types;
        angular.forEach(assetTypes, function (assetType) {
          var versions = assetType.versions;
          angular.forEach(versions, function (version) {
            var typeAndId = new URL(version.link).pathname.split('/').slice(3);
            var type = typeAndId[0];
            var id = typeAndId[1];

            types.push({
              'name': assetType.displayed_name + ": " + id,
              'type': type,
              'id': id,
              'drafts': []
            });

          });
        });
        return types;
      });
    }
  }
})();
