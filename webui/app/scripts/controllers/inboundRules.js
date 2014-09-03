'use strict';

/**
 * @ngdoc function
 * @name simpleStepperWebuiApp.controller:inboundRules
 * @description
 * # MainCtrl
 * Controller of the simpleStepperWebuiApp
 */
angular.module('simpleStepperWebuiApp')
  .controller('InboundRulesCtrl', ['$scope', '$http', 'apiEndpoint', function ($scope, $http, apiEndpoint) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
    $scope.inboundRules = {};
    $http.get(
        apiEndpoint + '/inboundRules'
      )
      .success(function (data) {
        $scope.inboundRules = data;
      })
      .error(function (data) {
        $scope.inboundRules = data;
      });
  }]);
