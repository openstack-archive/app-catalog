(function() {
  'use strict';
  var openstackReleases = ["Grizzly", "Havana", "Mitaka", "Newton"];
  var forms = {
    _common: [
      {name: "name", widget: "input", type: "text", required: true},
      {name: "version", widget: "input", type: "text", required: true},
      {name: "description", widget: "textarea", required: true},
      {name: "license", widget: "input", type: "text", required: true},
      {name: "license_url", widget: "input", type: "text"}
    ],
    glance_image: [
      {name: "disk_format", widget: "select", options: ["raw", "vhd", "vmdk", "vdi", "aki", "ari",
                                                        "ami", "qcow2", "iso"]},
      {name: "container_format", widget: "select", options: ["bare", "ovf", "aki", "ari", "ami",
                                                             "ova", "docker"]},
      {name: "min_ram", widget: "input", type: "number"},
      {name: "min_disk", widget: "input", type: "number"},
      {name: "image", widget: "blob"}
    ],
    murano_package: [
      {name: "release", type: "multisel", options: openstackReleases},
      {name: "package_name", type: "text"}
    ],
    heat_template: [
      {name: "release", type: "multisel", options: openstackReleases}
    ],
    tosca_template: [
      {name: "release", type: "multisel", options: openstackReleases},
      {name: "template_format", widget: "input", type: "text", required: true},
      {name: "template", widget: "blob"}
    ]
  };
  angular
    .module("AppCatalog")
    .controller("EditAssetController", EditAssetController);
  EditAssetController.$inject = ["$http", "$routeParams", "$location", "UrlService"];
  function EditAssetController($http, $routeParams, $location, UrlService) {
    var vm = this;
    vm.AddMetadataEntry = AddMetadataEntry;
    vm.DelMetadataEntry = DelMetadataEntry;
    vm.Save = Save;
    vm.Activate = Activate;
    vm.type = $routeParams.type;
    vm.id = $routeParams.id;
    vm.formFields = forms._common.concat(forms[vm.type]);
    if (vm.id) {
      $http.get(UrlService.getApiUrl(["artifacts", vm.type, vm.id], {}))
      .then(function(response) {
        vm.artifact = response.data;
      });
    } else {
      vm.artifact = {metadata: {}};
    }
    vm.status = false;
    vm.error = false;

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
        location.href = "#/edit/" + vm.type + "/" + vm.id;
        return;
      }
      var blob = blobs.pop();
      if (blob.files.length > 0) {
        var url = UrlService.getApiUrl(["artifacts", vm.type, vm.id, blob.name], {});
        var progressbar = document.getElementById("upload_progress");
        var progress = 0;
        vm.status = "Uploading " + blob.name;

        var client = new XMLHttpRequest();
        client.onloadend = function(evt) {
            vm.status = "Upload complete.";
        };
        client.upload.onprogress = function(pe) {
            var new_progress = Math.ceil((pe.loaded / pe.total) * 100);
            if (new_progress != progress) {
                progress = new_progress;
                vm.status = "Uploaded " + progress + "%";
                progressbar.textContent = "Uploaded " + progress + "%";
            }
        };
        client.open("PUT", url, true);
        client.send(blob.files[0]);

      } else {
        uploadBlobs(blobs);
      }
    }
    function AddMetadataEntry() {
      vm.artifact.metadata[vm.md_new_key] = "";
      vm.md_new_key = "";
    }
    function DelMetadataEntry(key) {
      delete vm.artifact.metadata[key];
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
    function Save(form) {
      vm.status = "Creating...";
      if (!vm.id) {
        $http.post(UrlService.getApiUrl(["artifacts", vm.type], {}), vm.artifact)
        .then(function(response) {
          vm.id = response.data.id;
          uploadBlobs(false);
        }, function(response) {
          vm.error = response;
          vm.status = "Error";
        });
      } else {
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
