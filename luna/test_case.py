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

	class YieldInserter(ast.NodeTransformer):
		"""
		An AST ``NodeTransformer`` that inserts yield statements everywhere.
		"""
		_yield_node = ast.Expr(value=ast.Yield())

		def __init__(self):
			"""
			Create a new YieldInserter instance.

			This prepares for storing the outer function name.
			"""
			self._outer_function_name = None

		def visit_ExceptHandler(self, node):
			"""
			Insert yield statements inside an exception handler.

			:param node: The exception handler to insert yield statements in.
			:return: A modified exception handler with yield statements in its
				body.
			"""
			node.body = self._insert_yields(node.body)
			return node

		def visit_For(self, node):
			"""
			Inserts yield statements inside a for node.

			:param node: The for node to insert yield statements in.
			:return: A modified for node with yield statements in its body.
			"""
			node.body = self._insert_yields(node.body)
			node.orelse = self._insert_yields(node.orelse)
			return node

		def visit_FunctionDef(self, node):
			"""
			Insert yield statements inside a function definition.

			:param node: The function definition to insert yield statements in.
			:return: A modified function definition with yield statements in its
				body.
			"""
			if not self._outer_function_name: #This is the first function declaration we're getting.
				self._outer_function_name = node.name
			node.body = self._insert_yields(node.body)
			return node

		def visit_If(self, node):
			"""
			Inserts yield statements inside an if node.

			:param node: The if node to insert yield statements in.
			:return: A modified if node with yield statements in its body.
			"""
			node.body = self._insert_yields(node.body)
			node.orelse = self._insert_yields(node.orelse)
			return node

		def visit_Try(self, node):
			"""
			Insert yield statements inside a try node.
			:param node: The try node to insert yield statements in.
			:return: A modified try node with yield statements in its body.
			"""
			node.body = self._insert_yields(node.body)
			node.orelse = self._insert_yields(node.orelse)
			node.finalbody = self._insert_yields(node.finalbody)
			return node

		def visit_While(self, node):
			"""
			Insert yield statements inside a while node.

			:param node: The while node to insert yield statements in.
			:return: A modified while node with yield statements in its body.
			"""
			node.body = self._insert_yields(node.body)
			node.orelse = self._insert_yields(node.orelse)
			return node

		def visit_With(self, node):
			"""
			Insert yield statements inside a with node.

			:param node: The with node to insert yield statements in.
			:return: A modified with node with yield statements in its body.
			"""
			node.body = self._insert_yields(node.body)
			return node

		def _insert_yields(self, body):
			"""
			Insert yield statements into a list of expressions.

			:param body: The list of expressions to insert the yield statements
				in.
			:return: A new list of expressions, with yield statements.
			"""
			new_body = [self._yield_node]
			for child in body:
				new_body.append(child)
				new_body.append(self._yield_node)
			return new_body

	yield_inserter = YieldInserter()
	transformed_syntax = yield_inserter.visit(syntax_tree) #Insert all yield statements.
	ast.fix_missing_locations(transformed_syntax)
	compiled = compile(transformed_syntax, filename="<yield_inserter>", mode="exec")
	scope = {}
	exec(compiled, scope) #Execute the transformed code inside an empty scope.
	new_func = scope[yield_inserter._outer_function_name] #The function definition inside the code is now the only name in this scope.

	functools.wraps(new_func)
	def func_wrapper(*args, **kwargs):
		"""
		Wrapper function to return, which calls the transformed function with
		any parameters it may have had.

		:param args: Positional arguments to call the transformed function with.
		:param kwargs: Key-word arguments to call the transformed function with.
		:return: TODO. Nothing yet.
		"""
		for yield_result in new_func(*args, **kwargs):
			if yield_result == None:
				inserted_function(*inserted_function_args, **inserted_function_kwargs)
	return func_wrapper