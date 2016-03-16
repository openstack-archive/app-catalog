(function () {
  'use strict';

  angular
    .module('glareassets')
    .directive('ngFileModel',FileModelDirective);

  function FileModelDirective() {
    return {
      scope: {
        ngFileModel: "="
      },
      link: link
    };

    function link(scope, element) {
      element.bind("change", function(changeEvent) {
        var reader = new FileReader();

        reader.onload = function(loadEvent) {
          scope.$apply(function() {
            scope.ngFileModel = {
              data: loadEvent.target.result,
              name: changeEvent.target.files[0].name,
              size: changeEvent.target.files[0].size
            };
          });
        };
        reader.readAsDataURL(changeEvent.target.files[0]);
      });
      console.log(scope);
    }
  }
})();
