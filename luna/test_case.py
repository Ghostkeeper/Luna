#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a helper class for test cases.

Some of this logic is specific to Luna with its plug-in structure. The rest
could have been imported from a more sophisticated third-party unit testing
package. But as long as these features are small and few, we should not
introduce an external dependency.
"""

import ast #To get the AST of functions in order to insert other function calls in between.
import functools #For partial functions and wrapper functions.
import inspect #To get source code for inserting function in between.
import unittest #For unittest's test case, which we extend.

class _TestCaseMeta(type):
	"""
	Metaclass to capture all parametrised tests and duplicate them for each of
	their parameter sets.
	"""

	def __new__(mcs, name, bases, members):
		"""
		Defines a new TestCase class.

		This intercepts all tests that are parametrised and duplicates them for
		each of the sets of parameters they need to be called with.
		:param name: The name of the TestCase class.
		:param bases: The superclasses of the TestCase class.
		:param members: The members of the TestCase class, including functions.
		:return: A new TestCase class, modified for parametrised tests.
		"""
		members_copy = dict(members)
		for member in members_copy:
			if callable(members_copy[member]) and hasattr(members_copy[member], "parameters"): #It's a function that's marked with the @parametrise annotation.
				for test_name, parameters in members_copy[member].parameters.items(): #Copy the function for each set of parameters.
					new_function = functools.partialmethod(members_copy[member], **parameters) #Fill in only the parameters. The rest is filled in at calling (such as "self").
					members[member + "_" + test_name] = new_function #Store the filled-in function along with the test name to make it unique.
				del members[member] #Delete the original parametrised function.
		return type.__new__(mcs, name, bases, members)

class TestCase(unittest.TestCase, metaclass=_TestCaseMeta):
	"""
	Extension of ``unittest.TestCase`` that adds all features that Luna's test
	cases need.
	"""
	pass #All special logic is currently done by the metaclass.

def parametrise(parameters):
	"""
	Causes a test to run multiple times with different parameters.

	This only works for functions inside a `TestCase` class.

	:param parameters: A dictionary containing individual tests. The keys in the
		dictionary act as a name for the test, which is appended to the function
		name. The values of the dictionary are dictionaries themselves. These
		act as the parameters that are filled into the function.
	:return: A parametrised test case.
	"""
	def parametrise_decorator(original_function):
		"""
		Adds the parameters with which the test must be run to the function.

		:param original_function: The function to parametrise.
		:return: A function with the parameters attached.
		"""
		original_function.parameters = parameters
		return original_function
	return parametrise_decorator

def execute_in_between(function, inserted_function, *inserted_function_args, **inserted_function_kwargs):
	"""
	Modifies a function such that another function executes as often as possible
	in between.

	It creates a copy of the function which behaves exactly the same, except
	that it calls ``inserted_function`` between every expression, with the
	supplied parameters.

	This function is intended to be used for testing atomicity. You can insert a
	function that checks for the state of something modified by the function
	that is under scrutiny. This will test whether the state is modified
	atomically between expressions. Note that it is not an exhaustive test,
	since it can't test atomicity of single expressions. That means that it's
	pretty easy to circumvent by calling a single expression that is not atomic,
	such as a function. Still, it catches a lot of mistakes in concurrency.

	:param function: The function to insert functions in. Built-in functions are
		not allowed.
	:param inserted_function: The function to insert in the other function.
	:param inserted_function_args: The positional arguments to supply to the
		inserted function.
	:param inserted_function_kwargs: The key-word arguments to supply to the
		inserted function.
	:return: A modified function that calls ``inserted_function`` as often as
		possible during execution.
	"""
	source_lines, _ = inspect.getsourcelines(function)

	#Correct indentation so that AST can parse the code.
	indentation = len(source_lines[0]) - len(source_lines[0].lstrip())
	for index, line in enumerate(source_lines):
		source_lines[index] = line[indentation:]

	source_code = "".join(source_lines)
	syntax_tree = ast.parse(source_code)

	class FunctionInserter(ast.NodeTransformer):
		"""
		An AST ``NodeTransformer`` that inserts function calls everywhere.
		"""

		def __init__(self, inserted_function, *inserted_args, **inserted_kwargs):
			"""
			Create a new ``FunctionInserter`` instance.

			This prepares an AST node to insert in the outer function.

			:param inserted_function: The function to insert in the outer
				function.
			:param inserted_args: Positional arguments to call the inserted
				function with.
			:param inserted_kwargs: Key-word arguments to call the inserted
				function with.
			"""
			self._outer_function_name = None #The name of the outer function, stored when we encounter it in our walk.
			self._additional_context = {} #Extra variables added to the context to facilitate the call of the inserted method.

			positional_arguments = []
			for index, argument in enumerate(inserted_args): #Convert each positional argument to an expression.
				name = "_arg" + str(index)
				self._additional_context[name] = argument #Store the actual argument in the context with a unique name.
				args_node = ast.Starred(value=ast.Name(id=name, ctx=ast.Load()), ctx=ast.Load()) #The expression refers to a name in the context.
				positional_arguments.append(args_node)

			keyword_arguments = []
			for key, value in inserted_kwargs.items(): #Convert each key-word argument to an expression.
				name = "_kwarg" + key
				self._additional_context[name] = value #Store the actual argument in the context with a unique name.
				kwargs_node = ast.keyword(key, ast.Name(id=name, ctx=ast.Load())) #The expression refers to a name in the context.
				keyword_arguments.append(kwargs_node)

			self._additional_context[inserted_function.__name__] = inserted_function #Add to context so that we can call it.
			self._call_node = ast.Call(func=ast.Name(id=inserted_function.__name__, ctx=ast.Load()), args=positional_arguments, keywords=keyword_arguments) #Construct the actual nodes.
			self._expr_node = ast.Expr(value=self._call_node)

		def visit_BinOp(self, node):
			"""
			Insert function calls inside any binary operator.

			:param node: The binary operator to insert function calls in.
			:return: A modified binary operator with a function call around its
				expressions.
			"""
			self.visit(node.left)
			self.visit(node.right)
			return ast.BinOp(
				left=ast.IfExp(test=self._call_node, body=node.left, orelse=node.left),
				op=node.op,
				right=ast.IfExp(test=self._call_node, body=node.right, orelse=node.right)
			)

		def visit_BoolOp(self, node):
			"""
			Insert function calls inside any boolean operator.

			:param node: The boolean operator to insert function calls in.
			:return: A modified boolean operator with a function call around its
				expressions.
			"""
			node.values = self._add_calls_exprs(node.values)
			return node

		def visit_Call(self, node):
			"""
			Insert a function call around a function call.

			:param node: The call node to surround with a function call.
			:return: A modified call node that calls the inserted function
				before making the specified function call.
			"""
			return ast.Call(
				func=node.func,
				args=self._add_calls_exprs(node.args),
				keywords=self._add_calls_keywords(node.keywords)
			)

		def visit_Compare(self, node):
			"""
			Insert function calls inside any comparison operator.

			:param node: The comparison operator to insert function calls in.
			:return: A modified comparison operator with a function call around
				its expressions.
			"""
			self.visit(node.left)
			return ast.Compare(
				left=ast.IfExp(test=self._call_node, body=node.left, orelse=node.right),
				ops=node.ops,
				comparators=self._add_calls_exprs(node.comparators)
			)

		def visit_ExceptHandler(self, node):
			"""
			Insert function calls inside an exception handler.

			:param node: The exception handler to insert function calls in.
			:return: A modified exception handler with function calls in its
				body.
			"""
			node.body = self._add_calls_stmts(node.body)
			return node

		def visit_Expr(self, node):
			"""
			Insert function calls around an expression.

			:param node: The expression to insert function calls around.
			:return: A modified expression with function calls around it.
			"""
			self.visit(node.value)
			return ast.Expr(value=ast.IfExp(test=self._call_node, body=node, orelse=node)) #Turn the inserted call into the test of an if-expression, and return the original expression in both cases.

		def visit_For(self, node):
			"""
			Inserts function calls inside a for node.

			:param node: The for node to insert function calls in.
			:return: A modified for node with function calls in its body.
			"""
			node.body = self._add_calls_stmts(node.body)
			node.orelse = self._add_calls_stmts(node.orelse)
			return node

		def visit_FunctionDef(self, node):
			"""
			Insert function calls inside a function definition.

			:param node: The function definition to insert function calls in.
			:return: A modified function definition with function calls in its
				body.
			"""
			if not self._outer_function_name: #This is the first function declaration we're getting.
				self._outer_function_name = node.name
			node.body = self._add_calls_stmts(node.body)
			return node

		def visit_If(self, node):
			"""
			Inserts function calls inside an if node.

			:param node: The if node to insert function calls in.
			:return: A modified if node with function calls in its body.
			"""
			node.body = self._add_calls_stmts(node.body)
			node.orelse = self._add_calls_stmts(node.orelse)
			return node

		def visit_IfExp(self, node):
			"""
			Inserts function calls inside an if-expression node.

			:param node: The if-expression node to insert function calls in.
			:return: A modified if-expression node with function calls in its
				body.
			"""
			self.visit(node.test)
			self.visit(node.body)
			self.visit(node.orelse)
			return ast.IfExp(
				test=ast.IfExp(test=self._call_node, body=node.test, orelse=node.test),
				body=ast.IfExp(test=self._call_node, body=node.body, orelse=node.orelse),
				orelse=ast.IfExp(test=self._call_node, body=node.orelse, orelse=node.orelse)
			)

		def visit_Index(self, node):
			"""
			Insert function calls inside a subscript index.

			:param node: The subscript index to insert function calls in.
			:return: A modified subscript index with function calls around its
				value.
			"""
			self.visit(node.value)
			return ast.Index(value=ast.IfExp(test=self._call_node, body=node.value, orelse=node.value))

		def visit_List(self, node):
			"""
			Insert function calls inside a list node.

			:param node: The list node to insert function calls in.
			:return: A modified list node with function calls around all its
				elements.
			"""
			node.elts = self._add_calls_exprs(node.elts)
			return node

		def visit_Set(self, node):
			"""
			Insert function calls inside a set node.

			:param node: The set node to insert function calls in.
			:return: A modified set node with function calls around all its
				elements.
			"""
			node.elts = self._add_calls_exprs(node.elts)
			return node

		def visit_Slice(self, node):
			"""
			Insert function calls inside a subscript slice.

			:param node: The subscript slice to insert function calls in.
			:return: A modified subscript slice with function calls around its
				values.
			"""
			if node.lower:
				self.visit(node.lower)
				lower_node = ast.IfExp(test=self._call_node, body=node.lower, orelse=node.lower)
			else:
				lower_node = None
			if node.upper:
				self.visit(node.upper)
				upper_node = ast.IfExp(test=self._call_node, body=node.upper, orelse=node.upper)
			else:
				upper_node = None
			if node.step:
				self.visit(node.step)
				step_node = ast.IfExp(test=self._call_node, body=node.step, orelse=node.step)
			else:
				step_node = None
			return ast.Slice(
				lower=lower_node,
				upper=upper_node,
				step=step_node
			)

		def visit_Subscript(self, node):
			"""
			Insert function calls inside a subscript node.

			:param node: The subscript node to insert function calls in.
			:return: A modified subscript node with function calls around its
				value.
			"""
			self.visit(node.value)
			self.visit(node.slice)
			return ast.Subscript(
				value=ast.IfExp(test=self._call_node, body=node.upper, orelse=node.lower),
				slice=node.slice,
				ctx=node.ctx
			)

		def visit_Try(self, node):
			"""
			Insert function calls inside a try node.

			:param node: The try node to insert function calls in.
			:return: A modified try node with function calls in its body.
			"""
			node.body = self._add_calls_stmts(node.body)
			node.orelse = self._add_calls_stmts(node.orelse)
			node.finalbody = self._add_calls_stmts(node.finalbody)
			return node

		def visit_Tuple(self, node):
			"""
			Insert function calls inside a tuple node.

			:param node: The tuple node to insert function calls in.
			:return: A modified tuple node with function calls around all its
				elements.
			"""
			node.elts = self._add_calls_exprs(node.elts)
			return node

		def visit_UnaryOp(self, node):
			"""
			Insert function calls inside any unary operator.

			:param node: The unary operator to insert function calls in.
			:return: A modified unary operator with a function call around its
				expression.
			"""
			self.visit(node.operand)
			return ast.UnaryOp(op=node.op, operand=ast.IfExp(test=self._call_node, body=node.operand, orelse=node.operand))

		def visit_While(self, node):
			"""
			Insert function calls inside a while node.

			:param node: The while node to insert function calls in.
			:return: A modified while node with function calls in its body.
			"""
			node.body = self._add_calls_stmts(node.body)
			node.orelse = self._add_calls_stmts(node.orelse)
			return node

		def visit_With(self, node):
			"""
			Insert function calls inside a with node.

			:param node: The with node to insert function calls in.
			:return: A modified with node with function calls in its body.
			"""
			node.body = self._add_calls_stmts(node.body)
			return node

		def _add_calls_exprs(self, expressions):
			"""
			Surround each element in a list of expression with a function call.

			The expression will get replaced with an ``IfExp`` which calls the
			inserted function as the test, and returns the expression regardless
			of whether the test was ``True`` or ``False``.

			:param expressions: A list of expressions.
			:return: A new list of expressions, with function calls around every
				expression.
			"""
			result = []
			for expression in expressions:
				self.visit(expression)
				result.append(ast.IfExp(test=self._call_node, body=expression, orelse=expression))
			return result

		def _add_calls_keywords(self, keywords):
			"""
			Surround the value of each keyword with a function call.

			:param keywords: A list of keywords.
			:return: A new list of keywords, with function calls around every
				keyword.
			"""
			result = []
			for keyword in keywords:
				self.visit(keyword.value)
				result.append(ast.keyword(arg=keyword.arg, value=ast.IfExp(test=self._call_node, body=keyword.value, orelse=keyword.value)))
			return result

		def _add_calls_stmts(self, statements):
			"""
			Insert function calls into a list of statements.

			:param statements: The list of statements to insert the function
				calls in.
			:return: A new list of statements, with function calls in between.
			"""
			result = [self._expr_node]
			for statement in statements:
				self.visit(statement)
				result.append(statement)
				result.append(self._expr_node)
			return result

	call_inserter = FunctionInserter(inserted_function, inserted_function_args, inserted_function_kwargs)
	transformed_syntax = call_inserter.visit(syntax_tree) #Insert function calls everywhere.
	ast.fix_missing_locations(transformed_syntax) #Add lineno and col_offset markers to the new nodes.
	compiled = compile(transformed_syntax, filename="<call_inserter>", mode="exec")
	scope = call_inserter._additional_context
	exec(compiled, scope) #Execute the transformed code inside the pre-defined scope (which has all the arguments and the function definition).
	new_func = scope[call_inserter._outer_function_name] #The function definition inside the code is now the only name in this scope.

	return new_func