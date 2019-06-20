module.exports = {
    "plugins": [
        // require('postcss-import'),
        // require('tailwindcss')('./tailwind.config.js'),
        require('postcss-extend-rule')(),
        require('precss')({}),
        require('autoprefixer')(),
    ]
};

// module.exports = () => ({
//   plugins: {
//     // 'stylelint': {
//     //   "extends": "stylelint-config-standard",
//     //   "rules": {
//     //     "max-empty-lines": 2
//     //   }
//     // },
//     'precss': {},
//       'autoprefixer': {},
//     // 'postcss-cssnext': {},
//     // 'cssnano': {
//     //   'autoprefixer': false
//     // }
//   }
// });