const path = require('path');

module.exports = {
  entry: './src/panel.ts',
  output: {
    filename: 'med-expert-panel.js',
    path: path.resolve(__dirname, '../custom_components/med_expert/www'),
    clean: true
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
  resolve: {
    extensions: ['.ts', '.js']
  },
  devtool: 'source-map'
};
