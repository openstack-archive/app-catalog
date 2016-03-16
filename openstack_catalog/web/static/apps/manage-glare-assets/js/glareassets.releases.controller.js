(function () {
  "use strict";
  angular
     .module('glareassets')
     .controller('releasesController', releasesController);
  releasesController.$inject = ['$scope'];

  function releasesController($scope) {
    var releasesList = [
      'Austin',
      'Bexar',
      'Cactus',
      'Diablo',
      'Essex',
      'Folsom',
      'Grizzly',
      'Havana',
      'Icehouse',
      'Juno',
      'Kilo',
      'Liberty',
      'Mitaka',
      'Newton',
      'Ocata'];
    var releases = {};
    for (var key in releasesList) {
      releases[releasesList[key]] = false;
    }
    $scope.releases = releases;
  }
})();

