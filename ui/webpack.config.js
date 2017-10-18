'use strict';

const webpack = require('webpack');
const path = require('path');
const conf = require('./webpack.conf/webpack.settings');

const libsConfig = require('./webpack.conf/webpack.libs');

const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CirclDepPlugin = require('circular-dependency-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
