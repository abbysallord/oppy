const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const lightningcssDir = path.join(root, 'node_modules', 'lightningcss');
const bindingName = 'lightningcss.win32-x64-msvc.node';
const source = path.join(root, 'node_modules', 'lightningcss-win32-x64-msvc', bindingName);
const target = path.join(lightningcssDir, bindingName);

if (fs.existsSync(source) && !fs.existsSync(target)) {
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target);
  console.log(`Copied ${bindingName} to ${path.relative(root, target)}`);
} else if (!fs.existsSync(source)) {
  console.warn('lightningcss-win32-x64-msvc package is not installed');
} else {
  console.log(`${bindingName} already present`);
}
