'use strict';

/**
 * @ngdoc function
 * @name simpleStepperWebuiApp.controller:inboundRules
 * @description
 * # MainCtrl
 * Controller of the simpleStepperWebuiApp
 */
angular.module('simpleStepperWebuiApp')
  .controller('InboundRulesCtrl', function ($scope, $http) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
    $scope.inboundRules = {};
    $http.get('/api/inboundRules')
      .success(function (data) {
        $scope.inboundRules = data;
      })
      .error(function (data) {
        $scope.inboundRules = data;
      });
  });
