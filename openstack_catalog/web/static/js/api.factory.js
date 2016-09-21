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
      GetArtifacts: GetArtifacts,
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
      }).error(handleApiError);
    }
    function GetArtifacts(type, args) {
      return callApi('get', ['artifacts', type], args, null);
    }
    function GetArtifact(type, id) {
      return callApi('get', ['artifacts', type, id], {}, null)
        .then(function (response) {
          return response.data;
        });
    }
    function CreateArtifact(type, artifact) {
      return callApi('post', ['artifacts', type], {}, artifact);
    }
    function GetSchemas() {
      if (getSchemasPromise === null) {
        getSchemasPromise = callApi('get', ['schemas'], {}, null).then(function(response) {
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
    function callApi(method, bits, args, data) {
      return $http({method: method, url: getApiUrl(bits, args), data: data}).error(handleApiError);
    }
    function handleApiError(data) {
      var explanation;
      if (data === null) {
        explanation = "HTTP Request Error";
      } else {
        explanation = data.explanation || data;
      }
      alert(explanation);
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
