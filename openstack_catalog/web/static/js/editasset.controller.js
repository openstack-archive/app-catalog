(function() {
  'use strict';
  var openstackReleases = ["Icehouse", "Juno", "Kilo", "Liberty", "Mitaka", "Newton", "Ocata", "Pike", "Queens"];
  var hiddenFields = ["status", "providedBy", "visibility"];
  var orderedFields = ["name", "description", "license", "license_url", "icon",
                       "metadata", "tags", "provided_by", "supported_by", "version",
                       "depends", "release", "image"];
  var externalBlobFields = {images: ["image"]};
  angular
    .module("AppCatalog")
    .controller("EditAssetController", EditAssetController);
  EditAssetController.$inject = ["$scope", "$http", "$routeParams", "$location", "UrlService"];
  function EditAssetController($scope, $http, $routeParams, $location, UrlService) {
    var vm = this;
    vm.Save = Save;
    vm.addItem = addItem;
    vm.addKey = addKey;
    vm.delKey = delKey;
    vm.newKey = {};
    vm.newBlobDictKey = {};
    vm.externalBlob = {};
    vm.externalBlobChecksum = {};
    vm.blobdict = {};
    vm.Activate = Activate;
    vm.type = $routeParams.type;
    vm.id = $routeParams.id;
    vm.uploading = [];
    if (vm.id) {
      $http.get(UrlService.getApiUrl(["artifacts", vm.type, vm.id], {}))
      .then(function(response) {
        vm.artifact = response.data;
        GetFormFields();
      });
    } else {
      vm.artifact = {};
      GetFormFields();
    }
    vm.status = false;
    vm.error = false;
    function createExternalBlobs() {
      var key = Object.keys(vm.externalBlob)[0];
      if (key) {
        var url = vm.externalBlob[key];
        var checksum = vm.externalBlobChecksum[key];
        delete vm.externalBlob[key];
        delete vm.externalBlobChecksum[key];
        var request = {
          method: "PUT",
          url: UrlService.getApiUrl(["artifacts", vm.type, vm.id, key], {}),
          headers: {"content-type": "application/vnd+openstack.glare-custom-location+json"},
          data: {url: url, checksum: checksum}
        };
        $http(request).then(function(response) {
          createExternalBlobs();
        }, function(response) {
          vm.error = response;
        });
      } else {
        return;
      }
    }
    function uploadBlobs(blobs) {
      if (blobs === false) {
        var collection = document.querySelectorAll('input[type=file]');
        var blobs = [];
        for (var i = 0; i < collection.length; i++) {
          blobs.push(collection[i]);
        }
      }
      if (blobs.length < 1) {
        vm.status = "Saved";
        createExternalBlobs();
        location.href = "#/edit/" + vm.type + "/" + vm.id;
        location.reload();
        return;
      }
      var blob = blobs.pop();
      if (blob.files.length > 0) {
        var blobdict_key = blob.attributes['ng-blobdict-key'];
        var bits = blob.name.split(".");
        if (bits.length > 1) {
          var keyName = bits.slice(1).join(".");
          var url = UrlService.getApiUrl(["artifacts", vm.type, vm.id, bits[0], keyName], {});
        } else {
          var url = UrlService.getApiUrl(["artifacts", vm.type, vm.id, blob.name], {});
        }
        var uploading = {progress: 0.0, name: blob.name};
        if($scope.$$phase) {
          vm.uploading.push(uploading);
        } else {
          $scope.$apply(function (){
            vm.uploading.push(uploading);
          });
        }
        var progressbar = document.getElementById("upload_progress");
        var progress = 0;
        vm.status = "Uploading " + blob.name;
        var client = new XMLHttpRequest();
        client.onloadend = function(evt) {
          $scope.$apply(function() {
            uploading.error = evt.target.statusText;
          });
          uploadBlobs(blobs);
        };
        client.upload.onprogress = function(pe) {
          var new_progress = Math.ceil((pe.loaded / pe.total) * 100);
          if (new_progress != progress) {
              progress = new_progress;
              $scope.$apply(function() {
                uploading.progress = progress;
              });
          }
        };
        client.open("PUT", url, true);
        client.send(blob.files[0]);

      } else {
        uploadBlobs(blobs);
      }
      vm.status = "Upload complete.";
    }
    function Activate() {
      var url = UrlService.getApiUrl(["artifacts", vm.type, vm.id], {});
      var patch = [{op: "replace", path: "/status", value: "active"}];
      $http.patch(url, patch).then(function(response){
        vm.status = "Activated";
      }, function(response) {
        vm.error = response;
      });
    }
    function GetFormFields() {
      $http.get(UrlService.getApiUrl(["schemas"], {}))
      .then(function (response){
        setFormFields(response.data.schemas);
      });
    }
    function setFormFields(schemas) {
      var formFields = [];
      for (var i=0; i<orderedFields.length; i++) {
        var field_name = orderedFields[i];
        if (field_name in schemas[vm.type].properties) {
          var field = getFieldWidget(field_name, schemas[vm.type].properties[field_name]);
          field.name = field_name;
          field.description = schemas[vm.type].properties[field_name].description;
          formFields.push(field);
        }
      }
      angular.forEach(schemas[vm.type].properties, function(val, key) {
        if (!val.readOnly && hiddenFields.indexOf(key) < 0 && orderedFields.indexOf(key) < 0) {
          var field = getFieldWidget(key, val);
          field.name = key;
          formFields.push(field);
        }
      });
      vm.formFields = formFields;
    }
    function getFieldWidget(name, field) {
      var fieldTypes = getFieldType(field);
      var fieldType = fieldTypes[0];
      var itemType = fieldTypes[1];
      switch (fieldType) {
        case 'string':
          if (field.hasOwnProperty('enum')) {
            return {widget: 'select', enum: field.enum};
          }
          if (field.maxLength > 255) {
            return {widget: 'textarea'}
          } else {
            return {widget: 'input', type: 'string'};
          }
        case 'integer':
          return {widget: 'input', type: 'number'};
        case 'array':
          return {widget: 'array', type: itemType};
        case 'dict':
          var locked = field.additionalProperties === false;
          if (locked && vm.artifact.id == null && itemType !== 'file') {
            vm.artifact[name] = {};
            angular.forEach(field.properties, function(val, key) {
              vm.artifact[name][key] = "";
            });
          }
          return {widget: 'dict', locked: locked, itemType: itemType};
        case 'file':
          if (!vm.artifact.hasOwnProperty(name) || vm.artifact[name] === null) {
            if (externalBlobFields[vm.type] && externalBlobFields[vm.type].indexOf(name) >= 0) {
              return {widget: 'external_blob'};
            }
            return {widget: 'input', type: 'file'};
          } else {
            return {widget: 'uploaded_blob'};
          }
        default:
          return {unknown: field}
      }
    }
    function getFieldType(field) {
      var type = (field.type.constructor === Array) ? field.type[0] : field.type;
      if (type == 'object') {
        var t = field.properties;
        if (t != null && t.checksum && t.content_type && t.size) {
          return ['file', null];
        } else {
          var type;
          if ('properties' in field) {
            type = getFieldType(field.properties[Object.getOwnPropertyNames(field.properties)[0]])[0];
          } else {
            type = getFieldType(field.additionalProperties)[0];
          }
          return ['dict', type];
        }
      }
      return [type, null];
    }
    function addItem(field) {
      if (vm.artifact[field] == null) {
        vm.artifact[field] = [];
      }
      vm.artifact[field].push("");
    }
    function addKey(field, vmKey, newDictName) {
      var newKey = vm[newDictName][field];
      if (newKey == null || newKey == "") {
        return;
      }
      if (vm[vmKey][field] == null) {
        vm[vmKey][field] = {};
      }
      if (vm[vmKey][field].hasOwnProperty(newKey)) {
        vm[newDictName][field] = "";
        return;
      }
      vm[vmKey][field][vm[newDictName][field]] = "";
      vm[newDictName][field] = "";
    }
    function delKey(field, key, vmKey) {
      delete vm[vmKey][field][key];
    }
    function Save(form) {
      if (!vm.id) {
        vm.status = "Creating...";
        $http.post(UrlService.getApiUrl(["artifacts", vm.type], {}), vm.artifact)
        .then(function(response) {
          vm.id = response.data.id;
          uploadBlobs(false);
        }, function(response) {
          vm.error = response;
          vm.status = "Error";
        });
      } else {
        vm.status = "Saving...";
        var patch = [];
        angular.forEach(vm.artifact, function(value, key) {
          if (form[key] && form[key].$dirty) {
            patch.push({op: "replace", path: "/" + key, value: value});
          }
        });
        patch.push({op: "replace", path: "/metadata", value: vm.artifact.metadata});
        $http.patch(UrlService.getApiUrl(["artifacts", vm.type, vm.id], {}), patch)
        .then(function(response) {
          uploadBlobs(false);
        }, function(response) {
          vm.error = response;
        });
      }
    }
  }
})();
