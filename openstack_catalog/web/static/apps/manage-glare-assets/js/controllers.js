'use strict'

/* Controllers */

var glareAssetsControllers = angular.module('glareAssetsControllers', []);

glareAssetsControllers.controller('GlareAssetTypesListController', ['$scope', '$http', '$interpolate',
    function ($scope, $http, $interpolate) {
        $scope.commonFields = ['name', 'description', 'version', 'license'];
        $scope.assetTypes = {
            types: [],
            selected: null
        };
        var apiEntryPoint = '/api/v2';
        var assetTypesURL = apiEntryPoint + '/artifacts';
        var draftsLinkTemplate = $interpolate(apiEntryPoint + '/artifacts/{{type}}/{{id}}/drafts');
        var publishLinkTemplate = $interpolate(apiEntryPoint + '/artifacts/{{type}}/{{id}}/{{asset_id}}/publish');
        var assetLinkTemplate = $interpolate(apiEntryPoint + '/artifacts/{{type}}/{{id}}/{{asset_id}}');

        $http.get(assetTypesURL).success(function (data) {
            var assetTypes = data.artifact_types;
            angular.forEach(assetTypes, function (assetType) {
                var versions = assetType.versions;
                angular.forEach(versions, function (version) {
                    var typeAndId = new URL(version.link).pathname.split('/').slice(3);
                    var type = typeAndId[0];
                    var id = typeAndId[1];

                    $scope.assetTypes.types.push({
                        'name': assetType.displayed_name + ": " + id,
                        'type': type,
                        'id': id,
                        'drafts': []
                    });

                });
            });
            $scope.assetTypes.selected = $scope.assetTypes.types[0];
            $scope.retrieveAssets();
        });

        $scope.retrieveAssets = function () {
            $http.get(draftsLinkTemplate({type: $scope.assetTypes.selected.type, id: $scope.assetTypes.selected.id}))
                .success(function (data) {
                    for (var i = 0; i < $scope.assetTypes.types.length; ++i) {
                        if ($scope.assetTypes.types[i].name == $scope.assetTypes.selected.name) {
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
                            if (asset.id == draftId) {
                                asset.published_at = data.published_at;
                            }
                        });
                    })
                .error(
                    function (errorResponse) {
                        var errorText = angular.element(errorResponse)[4].textContent || "unexpected error";

                        angular.forEach($scope.assetTypes.selected.drafts, function (asset) {
                            if (asset.id == draftId) {
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
                .success(function (data) {
                    angular.forEach($scope.assetTypes.selected.drafts, function (asset) {
                        if (asset.id == draftId) {
                            asset.deleted = true;
                        }
                    });
                }).error(
                function (errorResponse) {
                    var errorText = angular.element(errorResponse)[4].textContent || "unexpected error";

                    angular.forEach($scope.assetTypes.selected.drafts, function (asset) {
                        if (asset.id == draftId) {
                            asset.error = errorText;
                        }
                    });
                });
        };

    }
]);
