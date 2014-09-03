'use strict';

/**
 * @ngdoc function
 * @name simpleStepperWebuiApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the simpleStepperWebuiApp
 */
angular.module('simpleStepperWebuiApp')
  .controller('MainCtrl', ['$scope', '$http', 'apiEndpoint', function ($scope, $http, apiEndpoint) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
    $scope.postInboundRulesResult = [];
    $scope.appendYourIP = function () {
      $http.post(
           apiEndpoint + '/inboundRules'
        )
        .success(function (data) {
          $scope.postInboundRulesResult.push(data);
        })
        .error(function (data) {
          $scope.postInboundRulesResult.push(data);
        });
      };
  }]);
