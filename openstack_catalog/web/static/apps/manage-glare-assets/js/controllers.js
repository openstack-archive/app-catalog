'use strict'

/* Controllers */

var glareAssetsControllers = angular.module('glareAssetsControllers', []);

glareAssetsControllers.controller('GlareAssetTypesListController', ['$scope', '$http',
    function ($scope, $http) {
        $scope.commonFields = ['name', 'description', 'version', 'license'];

        $http.get(GLARE_ENDPOINT + 'artifacts').success(function (data) {
            var assetsTypes = data.artifact_types;
            var flatAssetTypes = [];
            angular.forEach(assetsTypes, function (assertType) {
                var versions = assertType.versions;
                angular.forEach(versions, function (version) {
                    var newAsset = {
                        'name': assertType.displayed_name + ": " + version.id,
                        'link': version.link,
                        'drafts': []
                    };
                    $http.get(newAsset.link + '/drafts').success(function (data) {
                        newAsset.drafts = data.artifacts;
                        angular.forEach(newAsset.drafts, function (asset) {
                            asset.error = null;
                        });
                    });
                    flatAssetTypes.push(newAsset);

                });
            });
            $scope.assetsTypes = flatAssetTypes;
            $scope.assetTypeSelect = $scope.assetsTypes[0];
        });


        $scope.publish = function (draftId) {
            var url = $scope.assetTypeSelect.link + '/';
            url += draftId;
            url += '/publish';
            $http.post(url)
                .success(
                    function (data) {
                        angular.forEach($scope.assetTypeSelect.drafts, function (asset) {
                            if (asset.id == draftId) {
                                asset.published_at = data.published_at;
                            }
                        });
                    })
                .error(
                    function (errorResponse) {
                        var errorText = angular.element(errorResponse)[4].textContent || "unexpected error";

                        angular.forEach($scope.assetTypeSelect.drafts, function (asset) {
                            if (asset.id == draftId) {
                                asset.error = errorText;
                            }
                        });
                    });
        };

        $scope.details = function (draftId) {
            var url = $scope.assetTypeSelect.link + '/' + draftId;
            $http.get(url)
                .success(function (data) {
                    $scope.detailedDraft = data;
                });
        };

        $scope.hideDetails = function () {
            $scope.detailedDraft = undefined;
        }
    }
]);
