const babel = require('@babel/core');
const vm = require('vm');
const fs = require('fs');

function decodeScript(filePath) {

  const scriptContent = fs.readFileSync(filePath, 'utf8')
  let jnFunctionCode = null;
  let jeFunctionCode = null;
  let initialArrayCode = null;
  let capturedArray = null;
  let jnOffset = null;
  let funcname2 = null;
  let vardecl = null;

  try {
    const findStringPlugin = function(babel) {
      const { types: t } = babel;
      return {
        visitor: {
          VariableDeclarator(path) {
            if (!t.isArrayExpression(path.node.init)) return;
            const elements = path.node.init.elements;
            let foundPattern = false;
            elements.forEach((element) => {
              if (t.isBinaryExpression(element) && element.operator === '+' && 
                  t.isStringLiteral(element.right) && element.right.value === 'L2') {
                foundPattern = true;
              }
            });
            if (foundPattern) {
              initialArrayCode = require('@babel/generator').default(path.node.init).code;
            }
          }
        }
      };
    };

    const functionNames = new Set();
    const extractPlugin = function(babel) {
      const { types: t } = babel;
      return {
        visitor: {
          VariableDeclarator(path) {
            if (!t.isArrayExpression(path.node.init)) return;
            path.node.init.elements.forEach((element) => {
              if (t.isBinaryExpression(element) && element.operator === '+' && 
                  t.isStringLiteral(element.right) && element.right.value === 'L2') {
                if (t.isCallExpression(element.left) && t.isIdentifier(element.left.callee)) {
                  functionNames.add(element.left.callee.name);
                }
              }
            });
          }
        }
      };
    };

    babel.transform(scriptContent, { plugins: [findStringPlugin, extractPlugin] });

    const assignedFunctions = new Map();
    functionNames.forEach(funcName => {
      const pattern = new RegExp(`\\b${funcName}\\s*=\\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\\s*;`, 'g');
      let match;
      while ((match = pattern.exec(scriptContent)) !== null) {
        if (!/^\d+$/.test(match[1])) {
          funcname2 = match[1];
          vardecl = `${funcName} = ${funcname2}`;
          assignedFunctions.set(funcName, match[1]);
        }
      }
    });
    
    const gefunc = vardecl ? vardecl.split(' =')[0] : null;
    const nestedFunctionCalls = new Set();
    if (assignedFunctions.size > 0) {
      const findFunctionPlugin = function(babel) {
        const { types: t } = babel;
        return {
          visitor: {
            FunctionDeclaration(path) {
              if (t.isIdentifier(path.node.id) && Array.from(assignedFunctions.values()).includes(path.node.id.name)) {
                const functionCode = require('@babel/generator').default(path.node).code;
                if (path.node.id.name === assignedFunctions.get(gefunc)) {
                  jnFunctionCode = functionCode;
                }
                const pattern = /\w+\[\w+\s*-=\s*(\d+)\]/g;
                const match = pattern.exec(functionCode);
                if (match && match[1]) {
                  jnOffset = match[1];
                }
                path.traverse({
                  CallExpression(innerPath) {
                    if (t.isIdentifier(innerPath.node.callee) && innerPath.node.arguments.length === 0) {
                      nestedFunctionCalls.add(innerPath.node.callee.name);
                    }
                  }
                });
              }
            },
            VariableDeclarator(path) {
              if (t.isIdentifier(path.node.id) && Array.from(assignedFunctions.values()).includes(path.node.id.name) && 
                  t.isFunctionExpression(path.node.init)) {
                const functionCode = require('@babel/generator').default(path.node).code;
                if (path.node.id.name === assignedFunctions.get(gefunc)) {
                  jnFunctionCode = `function ${path.node.id.name}${require('@babel/generator').default(path.node.init).code}`;
                }
                const pattern = /\w+\[\w+\s*-=\s*(\d+)\]/g;
                const match = pattern.exec(functionCode);
                if (match && match[1]) {
                  jnOffset = match[1];
                }
                path.traverse({
                  CallExpression(innerPath) {
                    if (t.isIdentifier(innerPath.node.callee) && innerPath.node.arguments.length === 0) {
                      nestedFunctionCalls.add(innerPath.node.callee.name);
                    }
                  }
                });
              }
            }
          }
        };
      };
      babel.transform(scriptContent, { plugins: [findFunctionPlugin] });
    }

    if (nestedFunctionCalls.size > 0) {
      const findNestedFunctionPlugin = function(babel) {
        const { types: t } = babel;
        return {
          visitor: {
            FunctionDeclaration(path) {
              if (t.isIdentifier(path.node.id) && nestedFunctionCalls.has(path.node.id.name)) {
                let foundArray = null;
                path.traverse({
                  VariableDeclarator(innerPath) {
                    if (t.isArrayExpression(innerPath.node.init)) {
                      foundArray = require('@babel/generator').default(innerPath.node.init).code;
                      jeArrayCode = foundArray;
                    }
                  }
                });
                if (foundArray) {
                  jeFunctionCode = require('@babel/generator').default(path.node).code;
                }
              }
            },
            VariableDeclarator(path) {
              if (t.isIdentifier(path.node.id) && nestedFunctionCalls.has(path.node.id.name) && 
                  t.isFunctionExpression(path.node.init)) {
                let foundArray = null;
                path.traverse({
                  VariableDeclarator(innerPath) {
                    if (t.isArrayExpression(innerPath.node.init)) {
                      foundArray = require('@babel/generator').default(innerPath.node.init).code;
                      jeArrayCode = foundArray;
                    }
                  }
                });
                if (foundArray) {
                  jeFunctionCode = `function ${path.node.id.name}${require('@babel/generator').default(path.node.init).code}`;
                }
              }
            }
          }
        };
      };
      babel.transform(scriptContent, { plugins: [findNestedFunctionPlugin] });
    }

    let iifeCode = null;
    if (nestedFunctionCalls) {
      const funcname_ = [...nestedFunctionCalls][0];
      const escapedFuncname = funcname_.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const iifePattern = new RegExp(`}\\s*\\(\\s*${escapedFuncname}\\s*\\);`, 'g');

      const matches = [...scriptContent.matchAll(iifePattern)];
      for (const match of matches) {
        const endIndex = match.index + match[0].length;
        let braceCount = 1;
        let startIndex = match.index - 1;
        while (startIndex >= 0 && braceCount > 0) {
          if (scriptContent[startIndex] === '}') braceCount++;
          else if (scriptContent[startIndex] === '{') braceCount--;
          startIndex--;
        }
        if (braceCount === 0) {
          while (startIndex >= 0 && /\s/.test(scriptContent[startIndex])) startIndex--;
          while (startIndex >= 0 && !/[\s(]/.test(scriptContent[startIndex])) startIndex--;
          if (scriptContent[startIndex] === '(') {
            startIndex--;
            if (scriptContent[startIndex] === '!') startIndex--;
          }
          startIndex++;
          iifeCode = scriptContent.slice(startIndex, endIndex);
          break;
        }
      }
      if (iifeCode) {
        const varAssignments = {};
        const forPattern = /for\s*\(\s*var\s+([^;]*);/;
        const forMatch = iifeCode.match(forPattern);
        if (forMatch && forMatch[1]) {
          forMatch[1].split(',').map(assignment => assignment.trim()).forEach(assignment => {
            const [varName, value] = assignment.split('=').map(s => s.trim());
            varAssignments[varName] = value;
          });
        }

        let modifiedIifeCode = iifeCode;
        if (forMatch && forMatch[1]) {
          const assignments = forMatch[1].split(',').map(assignment => assignment.trim());
          const nonNumberAssignments = assignments.filter(assignment => !/^\d+$/.test(assignment.split('=').map(s => s.trim())[1]));
          const newForDecl = nonNumberAssignments.length > 0 ? `var ${nonNumberAssignments.join(', ')};` : '';
          modifiedIifeCode = modifiedIifeCode.replace(`var ${forMatch[1]};`, newForDecl);
        }
        if (varAssignments['d'] === 't()') {
          modifiedIifeCode = modifiedIifeCode.replace(/\bd\s*=\s*t\s*\(\s*\)/g, `d = ${funcname_}()`);
        }
        Object.keys(varAssignments).forEach(varName => {
          if (/^\d+$/.test(varAssignments[varName])) {
            modifiedIifeCode = modifiedIifeCode.replace(new RegExp(`\\b${varName}\\b(?![\\w\\[\\]])`, 'g'), varAssignments[varName]);
          }
        });
        modifiedIifeCode = modifiedIifeCode.replace(/^\!\s*/, '').replace(new RegExp(`\\(\\s*${escapedFuncname}\\s*\\);$`, ''), '');
        modifiedIifeCode = `function e${modifiedIifeCode}`;

        const testtttContent = `${jeFunctionCode || `function ${funcname_}() { return []; }`}\n\n${jnFunctionCode || `function ${funcname2 || 'defaultFunc'}(t, e) { return null; }`}\n\n${modifiedIifeCode}`;
        const sandboxedEvalContent = `
${testtttContent}
e();
${vardecl || ''};
var array = ${initialArrayCode || '[]'};
console.log(array);
`;
        const sandbox = {
          console: { log: (...args) => { if (args.length === 1 && Array.isArray(args[0])) capturedArray = args[0]; } }
        };
        vm.runInNewContext(sandboxedEvalContent, sandbox);
      }
    }

    const middlePart = capturedArray
      ?.reduce((a, b) => b.length > a.length ? b : a, '')
      .split("'")
      .slice(1, 2)[0] || '';

    const brutekey = (encodedString) => {
      const results = [];
      for (let i = 0; i <= 999; i++) {
        const key = i.toString();
        const decoded = encodedString.split('').map((char, index) => {
          return String.fromCharCode(
            char.charCodeAt(0) ^ key.charCodeAt(index % key.length)
          );
        }).join('');
        const check = decoded.split('').every(char => {
          const code = char.charCodeAt(0);
          if (char === '@' || char === '|' || char === '~' || char === '`' || char === '<' || char === '>') {
            return false;
          }
          return true;
        });
        if (check) {
          results.push({
            key: i,
            decoded: decoded
          });
        }
      }
      return results;
    };

    console.log(JSON.stringify(brutekey(middlePart)))
  } catch (error) {
    return [];
  }
}

decodeScript(process.argv[2])