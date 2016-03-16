(function () {
  'use strict';

  angular
    .module('glareassets')
    .controller('TypesListController', TypesListController);

  TypesListController.$inject = [
    '$scope',
    '$http',
    '$interpolate',
    'AssetTypesFactory'
  ];

  function TypesListController($scope, $http, $interpolate, AssetTypesFactory) {
    $scope.commonFields = ['name', 'description', 'version', 'license'];
    $scope.assetTypes = {
      types: [],
      selected: null
    };
    var apiEntryPoint = '/api/v2/db';
    var draftsLinkTemplate = $interpolate(apiEntryPoint + '/artifacts/{{type}}/{{id}}/drafts');
    var publishLinkTemplate = $interpolate(apiEntryPoint + '/artifacts/{{type}}/{{id}}/{{asset_id}}/publish');
    var assetLinkTemplate = $interpolate(apiEntryPoint + '/artifacts/{{type}}/{{id}}/{{asset_id}}');

    // Get artifact types
    AssetTypesFactory.getTypes().then(function(types) {
      $scope.assetTypes.types = types;
      if ($scope.assetTypes.types.length !== 0) {
        $scope.assetTypes.selected = $scope.assetTypes.types[0];
        $scope.retrieveAssets();
      }
    });

    $scope.retrieveAssets = function () {
      $http.get(draftsLinkTemplate({type: $scope.assetTypes.selected.type, id: $scope.assetTypes.selected.id}))
        .success(function (data) {
          for (var i = 0; i < $scope.assetTypes.types.length; ++i) {
            if ($scope.assetTypes.types[i].name === $scope.assetTypes.selected.name) {
              $scope.assetTypes.types[i].drafts = data.artifacts;
              angular.forEach($scope.assetTypes.types[i].drafts, function (asset) {
                asset.error = null;
              });
              return;
            }
          }
        });
    };

    $scope.publish = function (draftId) {
      var url = publishLinkTemplate({
        type: $scope.assetTypes.selected.type,
        id: $scope.assetTypes.selected.id,
        asset_id: draftId
      });
      $http.post(url)
        .success(
            function (data) {
              angular.forEach($scope.assetTypes.selected.drafts, function (asset) {
                if (asset.id === draftId) {
                  asset.published_at = data.published_at;
                }
              });
            })
      .error(
          function (errorResponse) {
            var errorText = angular.element(errorResponse)[4].textContent || "unexpected error";

            angular.forEach($scope.assetTypes.selected.drafts, function (asset) {
              if (asset.id === draftId) {
                asset.error = errorText;
              }
            });
          });
    };

    $scope.details = function (draftId) {
      var url = assetLinkTemplate({
        type: $scope.assetTypes.selected.type,
        id: $scope.assetTypes.selected.id,
        asset_id: draftId
      });

      $http.get(url)
        .success(function (data) {
          $scope.detailedDraft = data;
        });
    };

    $scope.hideDetails = function () {
      $scope.detailedDraft = undefined;
    };

    $scope.delete = function (draftId) {
      var url = assetLinkTemplate({
        type: $scope.assetTypes.selected.type,
        id: $scope.assetTypes.selected.id,
        asset_id: draftId
      });
      $http.delete(url)
        .success(function () {
          angular.forEach($scope.assetTypes.selected.drafts, function (asset) {
            if (asset.id === draftId) {
              asset.deleted = true;
            }
          });
        }).error(
          function (errorResponse) {
            var errorText = angular.element(errorResponse)[4].textContent || "unexpected error";

            angular.forEach($scope.assetTypes.selected.drafts, function (asset) {
              if (asset.id === draftId) {
                asset.error = errorText;
              }
            });
          });
    };

  }
})();
