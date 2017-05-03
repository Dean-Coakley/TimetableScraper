var express = require('express');
var fs = require('fs');
var request = require('request');
var cheerio = require('cheerio');

var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var index = require('./routes/index');
var users = require('./routes/users');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(require('node-sass-middleware')({
  src: path.join(__dirname, 'public'),
  dest: path.join(__dirname, 'public'),
  indentedSyntax: true,
  sourceMap: true
}));
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', index);
app.use('/users', users);

app.get('/scrape', function(req, res) {
  var url = 'http://timetables.cit.ie:70/reporting/Individual;Student+Set;name;CO.DCOM2-B%0D%0A?weeks=23-32;35-37&days=1-5&periods=1-40&height=100&width=100';

  request(url, function (err, resp, html) {
    if (!err) {
      var $ = cheerio.load(html);

      var className, startTime, endTime, day;
      var json = {
        className: "", startTime: "", endTime: "", day: ""
      };

      $('table').filter(function () {
         var data = $('table').attr({'cellspacing': '0', 'border' : '1'}).children().text();

         data = data;
         fs.writeFile('Test', data, function (err) {
            if (err) {
                return console.log(err);
            }
            console.log('File saved');
         });
      });
    }
  });
});

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;
