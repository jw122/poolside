module.exports = {
    entry: [
        './src/index.jsx'
    ],
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: [
                  {
                    loader: 'babel-loader',
                    options: {
                      presets: ['@babel/preset-react']
                    }
                  }
                ]
            }
        ]
    },
    output: {
        path: __dirname + '/static',
        filename: 'bundle.js'
    }
};
