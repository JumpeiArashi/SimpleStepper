'use strict';

/**
 * @ngdoc overview
 * @name simpleStepperWebuiApp
 * @description
 * # simpleStepperWebuiApp
 *
 * Main module of the application.
 */
angular
  .module('simpleStepperWebuiApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/inboundRules', {
        templateUrl: 'views/inboundRules.html',
        controller: 'InboundRulesCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
