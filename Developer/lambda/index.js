'use strict';

var AWS = require('aws-sdk');
var async = require('async');
var v1 = 5;
var v2 = 10;


function createfun_add(next) {
  var c1 = v1 + v2;
  next(null, c1);
}

function createfun_substract(c1, next) {
  var c2 = c1 - 1
  next(null, c2)
}

function createfun_divide(c2, next) {
  var result = c2/2
  next(null, result);
}

exports.handler = function(event, context, callback){
  async.waterfall([createfun_add, createfun_substract, createfun_divide],
    function (err, result) {
      if (err) {
        callback(err);
      } else {
        console.log(result);
        callback(null, result);
      }
  });
};
