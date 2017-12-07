const webpack = require('webpack');
const path = require('path');

const ExtractTextPlugin = require('extract-text-webpack-plugin');
let CircularDependencyPlugin = require('circular-dependency-plugin')
const HtmlWebpackPlugin = require('html-webpack-plugin');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');

const uiDir = process.cwd();
const srcDir = path.join(uiDir, 'src');
const nodeModulesDir = path.join(uiDir, 'node_modules');
const sourceMapDir = 'srcs:///';
const buildDir = path.join(uiDir, 'build');


// Resolve path for libs files
const shirmModules = {
    'jquery': {
        path: path.join(nodeModulesDir, 'jquery/dist/jquery.min'),
        devPath: path.join(nodeModulesDir, 'jquery/dist/jquery')
    },

    'angular': {
        path: path.join(nodeModulesDir, 'angular/index'),
        loader: {
            test: '/angular/',
            loader: 'imports?$=jquery!exports?angular'
        }
    },

    'bootstrap': {
        path: path.join(nodeModulesDir, 'bootstrap/dist/js/bootstrap.min.js')
    },

    'moment': {
        path: path.join(nodeModulesDir, 'moment/moment')
    },

    'angular-sanitize': {
        path: path.join(nodeModulesDir, 'angular-sanitize/angular-sanitize.min'),
        devPath: path.join(nodeModulesDir, 'angular-sanitize/angular-sanitize')
    },

    'angular-ui-bootstrap': {
        path: path.join(nodeModulesDir, 'angular-ui-bootstrap/dist/ui-bootstrap-tpls')
    },

    'angular-ui-router': {
        path: path.join(nodeModulesDir, 'angular-ui-router/release/angular-ui-router.min'),
        devPath: path.join(nodeModulesDir, 'angular-ui-router/release/angular-ui-router')
    },

    'angular-cookies': {
        path: path.join(nodeModulesDir, 'angular-cookies/angular-cookies.min'),
        devPath: path.join(nodeModulesDir, 'angular-cookies/angular-cookies'),
        loader: {
            test: '/angular-cookies/',
            loader: 'import?angular'
        }
    },

    'angular-bootstrap-datetimepicker': {
        path: path.join(nodeModulesDir, 'angular-bootstrap-datetimepicker/src/js/datetimepicker')
    },

    'angular-bootstrap-datetimepicker-template': {
        path: path.join(nodeModulesDir, 'angular-bootstrap-datetimepicker/src/js/datetimepicker.templates')
    },

    'toastr': {
        path: path.join(nodeModulesDir, 'toastr/toastr')
    }
};


// Resolver libs files
function webpackLibsResolver() {
    const out = {
        resolve: {alias: {}},
        module: {rules: []}
    };

    Object.keys(shirmModules).forEach(alias => {
        let libPath;
        const libConfig = shirmModules[alias];

        if (typeof libConfig === 'string') {
            libPath = libConfig;

        } else {
            libPath = libConfig.path || alias;

        }

        out.resolve.alias[alias] = libPath;
        libConfig.rule ? out.module.rules.push(libConfig.rule) : null;
    });

    return out;
}


// Webpack configs
const webpackConfigs = {
    debug: false,
    context: srcDir,
    resolve: {
        root: srcDir,
        modules: [srcDir, nodeModulesDir],
        alias: webpackLibsResolver().resolve.alias,
        modulesDirectories: ['/node_modules/']
    },
    entry: 'main.js',
    output: {
        path: buildDir,
        filename: '[name].[chunkhash].js',
        devtoolsModuleFilenameTemplate: info => {
            return sourceMapDir + path.normalize(info.recourcePath);
        }
    },
    debtool: 'cheap-module-source-map',
    module: {
        loaders: [
            // json loader
            {
                test: /\.json$/,
                loader: 'json'
            },

            // template loader
            {
                test: /\.html$/,
                loader: 'html-loader',
                exclude: [/index*\.html$/]
            },

            // assets
            {
                test: /(node_modules).+\.(png|jpe?g|gif|woff|woff2|ttf|eot|ico|svg|swf)$/,
                loader: 'file-loader?name=assets/[name].[hash].[ext]',
                options: {
                    context: nodeModulesDir
                }
            },
            {
                test: /\.woff(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=application/font-woff"
            },
            {
                test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=application/font-woff"
            },
            {
                test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=application/octet-stream"
            },
            {
                test: /\.eot(\?v=\d+\.\d+\.\d+)?$/,
                loader: "file"
            },
            {
                test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
                loader: "url?limit=10000&mimetype=image/svg+xml"
            },
            {
                test: /\.(png|jpe?g|gif|svg|woff|woff2|ttf|eot|ico)$/,
                loader: 'file-loader?name=[path][name].[ext]',
                options: {
                    context: srcDir
                }
            },

            // style loader
            {
                test: /\.css$/,
                loader: ExtractTextPlugin.extract('style-loader', 'css-loader?sourceMap')
            },
            {
                test: /\.sass$/,
                loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader?sourceMap')
            },

            // js loaders
            {
                test: /\.js$/,
                loader: 'babel',
                exclude: /node_modules/,
                query: {
                    presets: ['es2015', 'es2016', 'es2017']
                }
            }
        ]
    },
    plugins: [
        new ExtractTextPlugin('main.[contenthash].css'),
        new HtmlWebpackPlugin({
            template: 'index.html'
        }),
        new CircularDependencyPlugin({failOnError: false}),
        new OptimizeCssAssetsPlugin(),
        new webpack.NoErrorsPlugin(),
        new webpack.ProvidePlugin({
            'window.jQuery': 'jquery',
            'window.$': 'jquery',
            jQuery: 'jquery'
        })
    ]
};

module.exports = webpackConfigs;
