##JavaScript isolation

### Rewrite all function and variable names to prepend a sandbox_ prefix

We had to make changes in two places in lab6visitor.py:

First, add sandbox_ to every function and variable:

        def visit_Identifier(self, node):
        return 'sandbox_' + node.value
        
Second, modify the dotaccessor so that attributes wont get prefixed:

    def visit_DotAccessor(self, node):
        if getattr(node, '_parens', False):
            template = '(%s.%s)'
        else:
	    template = '%s[badword_check("%s")]'
        s = template % (self.visit(node.node), self.visit(node.identifier).
		replace('sandbox_', ''))

	    return s
        
We also needed on 'unsandbox' object properties:

    def visit_Assign(self, node):
        # Note: if node.op is ':' this "assignment" is actually a property in
        # an object literal, i.e. { foo: 1, "bar": 2 }. In that case, node.left
        # is either an ast.Identifier or an ast.String.
        if node.op == ':':
            template = '%s%s %s'
        else:
            template = '%s %s %s'
        if getattr(node, '_parens', False):
            template = '(%s)' % template
        if  node.op == ':':
		return template % (
            		self.visit(node.left).replace('sandbox_', ''), node.op, self.visit(node.right))
	return template % (
                        self.visit(node.left), node.op, self.visit(node.right))

### Prevent sandboxed code from accessing dangerous properties of objects
htmlfilter.py:

    function includes(k) {
      for(var i=0; i < this.length; i++){
        if( this[i] === k || ( this[i] !== this[i] && k !== k ) ){
          return true;
        }
      }
      return false;
    }

    var badwords = ["__proto__", "constructor", "__defineGetter__", "__defineSetter__"];
    badwords.includes = includes;

    function badword_check(s) {

	    if (badwords.includes(s)) {
		    return '__invalid__';		
	    }

	    return s;
    }

lab6visitor.py:

    def visit_DotAccessor(self, node):
        if getattr(node, '_parens', False):
            template = '(%s.%s)'
        else:
	    template = '%s[badword_check("%s")]'
        s = template % (self.visit(node.node), self.visit(node.identifier).
		replace('sandbox_', ''))

	    return s

### Ensure that dangerous attributes cannot be accessed using array-like brackets
htmlfilter.py:

    function includes(k) {
      for(var i=0; i < this.length; i++){
        if( this[i] === k || ( this[i] !== this[i] && k !== k ) ){
          return true;
        }
      }
      return false;
    }

    var badwords = ["__proto__", "constructor", "__defineGetter__", "__defineSetter__"];
    badwords.includes = includes;

    function badword_check(s) {

	    if (badwords.includes(s)) {
		    return '__invalid__';		
	    }

	    return s;
    }
    
lab6visitor.py:

        def visit_BracketAccessor(self, node):
        s = '%s[bracket_check(%s)]' % (self.visit(node.node), self.visit(node.expr))
        return s    

### Work around JavaScript's handling of the 'this' keyword

htmlfilter.py:

    function this_check(s) {
	if (s === window) return null;
        return s;
    }

lab6visitor.py:

    def visit_This(self, node):
	    return 'this_check(this)'