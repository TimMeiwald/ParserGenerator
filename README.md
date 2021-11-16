# ParserGenerator
Takes a PEG Grammar File and generates a Parser from it 

An example of the PEG Grammar File is shown in src/Inputs/test.txt
The compiler output alongside intermediary outputs are shown in src/Outputs, with Parser.py being the Parser generated for the test.txt grammar

In order to use this you simply need to give "generate_parser()" in main.py a relative filepath to the grammar and it'll output in the relative target filepath. 
Note, It is safer to have a target filepath that consists of an empty folder to avoid the possibility of overwriting any code with the same name of some of the generated files. This may be fixed in the future

An example grammar is as follows, 

The following simply returns true and consumes a token if the inputs first character is equal to A. Else it returns false without consuming input
<Terminal> = "A"; 
 
The following return true and consumes two tokens if the inputs first two characters are AB. Else it returns false without consuming input
<Sequence> = "A", "B";
  
The following return true and consumes one tokens if the inputs first character is A or B. Else it returns false without consuming input. Note, in a PEG grammar the leftmost option is always to be evaluated first. Which is not relevant for this example but ensures the grammar has no ambiguity in more complex cases.
<Ordered_Choice> = "A"/"B";
  
The following always returns true but only consumes input if the expression matches. It is greedy and attempts to consume as many A's as possible. This means that <This_Rule> = "A"*, "A"; always fails as the 2nd sequence value of "A" never matches as the zero or more operator will have matched it.
<Zero_Or_More> = "A"*;
  
The following returns true if the expression matches at least once else it fails without consuming input. It is greedy and attempts to consume as many A's as possible. This means that <This_Rule> = "A"+, "A"; always fails as the 2nd sequence value of "A" never matches as the one or more operator will have matched it.
<One_Or_More> = "A"+;
The following always returns True but only consumes input if the expression matches. 
<Optional> = "A"?;
The following returns true if rule <Terminal> returns True and fails if <Terminal> fails. It consumes input if <Terminal> consumes input and doesn't if <Terminal> doesn't.
That is to say it behaves exactly like a functional call and can be used with all other operators to make *arbitrarily complex parsers.
* that Parsing Expression Grammars can describe
<Var_Reference> = <Terminal>;
The following returns true if what's inside the brackets return true etc etc. Behaves like scoping. Theoretically one could write an entire grammar in one rule with a lot of subexpressions. This exists for ease of use and reading where a subexpression isn't meaningful but explicitly showing order of operations is helpful. 
<Subexpression> = ("A");
