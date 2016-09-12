(function() {
  'use strict';
  var openstackReleases = ["Icehouse", "Juno", "Kilo", "Liberty", "Mitaka", "Newton",
                           "Ocata", "Pike", "Queens"];
  var hiddenFields = ["status", "providedBy", "visibility"];
  var orderedFields = ["name", "description", "license", "license_url", "icon",
                       "metadata", "tags", "provided_by", "supported_by", "version",
                       "depends", "release", "image"];
  var externalBlobFields = {images: ["image"]};
  var customWidgets = {_all: {release: {widget: "multisel", options: openstackReleases}}};
  angular
    .module("AppCatalog")
    .controller("EditAssetController", EditAssetController);
  EditAssetController.$inject = ["$scope", "$http", "$routeParams", "$location", "Api"];
  function EditAssetController($scope, $http, $routeParams, $location, Api) {
    var vm = this;
    vm.Save = Save;
    vm.addItem = addItem;
    vm.addKey = addKey;
    vm.delKey = delKey;
    vm.newKey = {};
    vm.newBlobDictKey = {};
    vm.externalBlob = {};
    vm.externalBlobMd5 = {};
    vm.blobdict = {};
    vm.uploadErrors = [];
    vm.Activate = Activate;
    vm.type = $routeParams.type;
    vm.id = $routeParams.id;
    vm.uploading = [];
    if (vm.id) {
      Api.GetArtifact(vm.type, vm.id).then(function(artifact) {
        vm.artifact = artifact;
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
        var md5 = vm.externalBlobMd5[key];
        delete vm.externalBlob[key];
        delete vm.externalBlobMd5[key];
        Api.CreateExternalBlob(vm.type, vm.id, key, {url: url, md5: md5})
        .then(function(response) {
          createExternalBlobs();
        }, function(response) {
          vm.error = response;
        });
      } else {
        return;
      }
    }
    function _reload() {
      if (vm.uploadErrors.length == 0) {
        location.href = "#/edit/" + vm.type + "/" + vm.id;
        location.reload();
      }
    }
    function uploadBlobs(blobs) {
      if (blobs === false) {
        var collection = document.querySelectorAll('input[type=file]');
        var blobs = [];
        for (var i = 0; i < collection.length; i++) {
          if (collection[i].files.length > 0) {
            blobs.push(collection[i]);
          }
        }
        if (blobs.length == 0) {
          return _reload();
        }
      }
      if (blobs.length < 1) {
        vm.status = "Saved";
        createExternalBlobs();
        return _reload();
      }
      var blob = blobs.pop();
      var bits = blob.name.split(".");
      if (bits.length > 1) {
        var keyName = bits.slice(1).join(".");
        var url = Api.getApiUrl(["artifacts", vm.type, vm.id, bits[0], keyName], {});
      } else {
        var url = Api.getApiUrl(["artifacts", vm.type, vm.id, blob.name], {});
      }
      var uploading = {progress: 0.0, name: blob.name};
      if ($scope.$$phase) {
        vm.uploading.push(uploading);
      } else {
        $scope.$apply(function () {
          vm.uploading.push(uploading);
        });
      }
      var progressbar = document.getElementById("upload_progress");
      var progress = 0;
      vm.status = "Uploading " + blob.name;
      var client = new XMLHttpRequest();
      client.withCredentials = true;
      client.onloadend = function(evt) {
        $scope.$apply(function() {
          uploading.error = evt.target.statusText;
          if (evt.target.status != 200) {
            vm.uploadErrors.push({blob: blob.name, statusText: evt.target.statusText});
          }
        });
        uploadBlobs(blobs);
      };
      client.upload.onprogress = function(pe) {
        var newProgress = Math.ceil((pe.loaded / pe.total) * 100);
        if (newProgress != progress) {
          progress = newProgress;
          $scope.$apply(function() {
            uploading.progress = progress;
          });
        }
      };
      client.open("PUT", url, true);
      client.send(blob.files[0]);
      vm.status = "Upload complete.";
    }
    function Activate() {
      var url = Api.getApiUrl(["artifacts", vm.type, vm.id], {});
      var patch = [{op: "replace", path: "/status", value: "active"}];
      $http.patch(url, patch).then(function(response) {
        vm.status = "Activated";
      }, function(response) {
        vm.error = response;
      });
    }
    function GetFormFields() {
      Api.GetSchemas()
      .then(function (schemas) {
        vm.formFields = getFormFields(schemas);
      });
    }
    function getFormFields(schemas) {
      var formFields = [];
      for (var i = 0; i < orderedFields.length; i++) {
        var fieldName = orderedFields[i];
        if (fieldName in schemas[vm.type].properties) {
          var field = getFieldWidget(fieldName, schemas[vm.type].properties[fieldName]);
          field.description = schemas[vm.type].properties[fieldName].description;
          field.required = schemas[vm.type].required.indexOf(fieldName) >= 0;
          formFields.push(field);
        }
      }
      angular.forEach(schemas[vm.type].properties, function(val, key) {
        if (!val.readOnly && hiddenFields.indexOf(key) < 0 && orderedFields.indexOf(key) < 0) {
          var field = getFieldWidget(key, val);
          formFields.push(field);
        }
      });
      return formFields;
    }
    function getFieldWidget(name, field) {
      var fieldTypes = getFieldType(field);
      var fieldType = fieldTypes[0];
      var itemType = fieldTypes[1];
      var customWidget = customWidgets._all[name];
      var widget = {};
      if (customWidget !== undefined) {
        widget = customWidget;
      }
      switch (fieldType) {
        case 'string':
          if (field.hasOwnProperty('enum')) {
            widget = {widget: 'select', enum: field.enum};
          }
          if (field.maxLength > 255) {
            widget = {widget: 'textarea'};
          } else {
            widget = {widget: 'input', type: 'string'};
          }
          widget.maxlength = field.maxLength;
          console.log(field);
          console.log(widget);
          break;
        case 'integer':
          widget = {widget: 'input', type: 'number', min: field.minumum};
          break;
        case 'array':
          widget = {widget: 'array', type: itemType};
          break;
        case 'dict':
          var locked = field.additionalProperties === false;
          if (locked && vm.artifact.id === undefined && itemType !== 'file') {
            vm.artifact[name] = {};
            angular.forEach(field.properties, function(val, key) {
              vm.artifact[name][key] = "";
            });
          }
          widget = {widget: 'dict', locked: locked, itemType: itemType};
          break;
        case 'file':
          if (!vm.artifact.hasOwnProperty(name) || vm.artifact[name] === null) {
            if (externalBlobFields[vm.type] && externalBlobFields[vm.type].indexOf(name) >= 0) {
              widget = {widget: 'external_blob'};
            }
            widget = {widget: 'input', type: 'file'};
          } else {
            widget = {widget: 'uploaded_blob'};
          }
          break;
        default:
          widget = {unknown: field};
      }
      widget.name = name;
      return widget;
    }
    function getFieldType(field) {
      var type = (field.type.constructor === Array) ? field.type[0] : field.type;
      if (type == 'object') {
        var t = field.properties || null;
        if (t !== null && t.md5 && t.content_type && t.size) {
          return ['file', null];
        } else {
          var type;
          if ('properties' in field) {
            var _field = field.properties[Object.getOwnPropertyNames(field.properties)[0]];
            type = getFieldType(_field)[0];
          } else {
            type = getFieldType(field.additionalProperties)[0];
          }
          return ['dict', type];
        }
      }
      return [type, null];
    }
    function addItem(field) {
      if (!vm.artifact.hasOwnProperty(field)) {
        vm.artifact[field] = [];
      }
      vm.artifact[field].push("");
    }
    function addKey(field, vmKey, newDictName) {
      var newKey = vm[newDictName][field];
      if (!vm[vmKey].hasOwnProperty(field)) {
        if (newKey == "") {
          return;
        }
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
        $http.post(Api.getApiUrl(["artifacts", vm.type], {}), vm.artifact)
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
        $http.patch(Api.getApiUrl(["artifacts", vm.type, vm.id], {}), patch)
        .then(function(response) {
          uploadBlobs(false);
        }, function(response) {
          vm.error = response;
        });
      }
    }
  }
})();
