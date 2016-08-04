##JavaScript isolation

### Rewrite all function and variable names to prepend a sandbox_ prefix

### Prevent sandboxed code from accessing dangerous properties of objects

    function bracket_check(s) {
    
        if (s.toString == "__proto__" || s.toString == "constructor" || s.toString == "__defineGetter__" || s.toString == "__defineSetter__") {
            return __invalid__;
        }
        else {
            return s.toString();
            }

    }
    
### Ensure that dangerous attributes cannot be accessed using array-like brackets

### Work around JavaScript's handling of the 'this' keyword