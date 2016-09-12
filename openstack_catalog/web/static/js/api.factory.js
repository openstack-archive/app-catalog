(function() {
  'use strict';
  var knownTypes = ['images', 'tosca_templates', 'heat_templates', 'murano_packages'];
  var getSchemasPromise = null;
  angular
    .module('AppCatalog')
    .factory('Api', Api);
  Api.$inject = ['$http'];
  function Api($http) {
    return {
      GetSchemas: GetSchemas,
      GetFieldType: GetFieldType,
      GetArtifact: GetArtifact,
      CreateArtifact: CreateArtifact,
      CreateBlob: CreateExternalBlob,
      getUrl: getUrl,
      getApiUrl: getApiUrl
    };
    function CreateExternalBlob(type, id, name, data) {
      return $http.request({
        method: "PUT",
        url: getApiUrl(["artifacts", type, id, name], {}),
        headers: {"content-type": "application/vnd+openstack.glare-custom-location+json"},
        data: data
      });
    }
    function GetArtifact(type, id) {
      return $http.get(getApiUrl(['artifacts', type, id], {}))
        .then(function (response) {
          return response.data;
        });
    }
    function CreateArtifact(type, artifact) {
      return $http.post('/api/v2/db/artifacts/' + type, artifact);
    }
    function GetSchemas() {
      if (getSchemasPromise === null) {
        getSchemasPromise = $http.get('/api/v2/db/schemas').then(function(response) {
          return response.data.schemas;
        });
      }
      return getSchemasPromise;
    }
    function GetFieldType(typeName, fieldName, schemas) {
      return getFieldType(schemas[typeName].properties[fieldName]);
    }
    function getFieldType(field) {
      var fieldType = {readOnly: field.readOnly === true};
      if (field.type.constructor === Array) {
        var type = field.type[0];
        fieldType.nullable = true;
      } else {
        var type = field.type;
        fieldType.nullable = false;
      }
      if (type === 'object') {
        var t = field.properties || null;
        if (t !== null && t.checksum && t.content_type && t.size) {
          fieldType.type = 'blob';
        } else {
          fieldType.type = 'dict';
          if ('properties' in field) {
            var _field = field.properties[Object.getOwnPropertyNames(field.properties)[0]];
            fieldType.elementType = getFieldType(_field);
          } else {
            fieldType.elementType = getFieldType(field.additionalProperties);
          }
        }
      } else {
        fieldType.type = type;
      }
      return fieldType;
    }
  }
  function getUrl(start, bits, args) {
    var url = start;
    for (var i = 0; i < bits.length; i++) {
      url += '/' + bits[i];
    }
    var query = [];
    for (var arg in args) {
      if ('undefined' !== typeof args[arg]) {
        query.push(arg + '=' + args[arg]);
      }
    }
    if (query) {
      url += '?' + query.join('&');
    }
    return url;
  }
  function getApiUrl(bits, args) {
    return getUrl(GLARE_URL, bits, args);
  }
})();
