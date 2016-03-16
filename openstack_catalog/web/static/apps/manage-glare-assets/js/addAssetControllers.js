"use strict";

var glareAssetsControllers = angular.module('glareAssetsControllers');

glareAssetsControllers.controller('assetController', ['$scope', '$http', function($scope, $http) {
  $scope.asset_submit = function() {
    var data = angular.copy($scope.asset);

    var rebuild_release = function(data) {
      var release = [];
      for (var key in data.releases) {
        if (data.releases.hasOwnProperty(key)) {
          if (data.releases[key]) {
            release.push(key);
          }
        }
      }
      if (release.length == 0) {
        release = ['Kilo'];
      }
      data['release'] = release;
    }

    var rebuild_asset_type_data = function(data) {
      var needed_asset_type_data = data[data['type_name']];
      var asset_types = ['glance_images', 'heat_templates', 'murano_packages', 'tosca_templates', 'bundles'];
      for (var key in asset_types) {
        delete data[asset_types[key]];
      }
      for (var key in needed_asset_type_data) {
        data[key] = needed_asset_type_data[key];
      }
    }

    var upload_file = function(data) {
      var f = document.getElementById('file').files[0];
      var reader = new FileReader();
      reader.onloadend = function(e) {
        var bin_data = e.target.result;
        data['object'] = bin_data;
      }
      reader.readAsArrayBuffer(f);
    }

    var rebuild_data = function(data) {
      data['type_version'] = '0.0.0';
      rebuild_release(data);
      rebuild_asset_type_data(data);
      upload_file(data);
    }

    rebuild_data(data);

    var build_glare_url = function(data, glare_endpoint) {
      // var url = glare_endpoint;
      // if (!glare_endpoint) {
      //     url = 'http://0.0.0.0:9494';
      // }
      url = 'api/v2/artifacts/' + data['type_name'] + '/v' + data['type_version'] + '/drafts';
      return url;
    }


    var config = {'Content-Type': 'application/json'};
    var url = build_glare_url(data);
    alert(url);

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
  }
}]);

glareAssetsControllers.controller('releaseCtrl', function($scope) {
  var releases_list = ['Austin', 'Bexar', 'Cactus', 'Diablo', 'Essex', 'Folsom', 'Grizzly', 'Havana', 'Icehouse', 'Juno', 'Kilo', 'Liberty', 'Mitaka', 'Newton', 'Ocata'];
  var releases = {};
  for (var key in releases_list) {releases[releases_list[key]] = false}
  $scope.releases = releases;
});

