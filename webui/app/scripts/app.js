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
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
