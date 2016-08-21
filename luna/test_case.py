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
				argument_node = ast.Starred(value=ast.Name(id=name, ctx=ast.Load()), ctx=ast.Load()) #The expression refers to a name in the context.
				positional_arguments.append(argument_node)

			keyword_arguments = []
			for key, value in inserted_kwargs.items(): #Convert each key-word argument to an expression.
				name = "_kwarg" + key
				self._additional_context[name] = value #Store the actual argument in the context with a unique name.
				argument_node = ast.keyword(key, ast.Name(id=name, ctx=ast.Load())) #The expression refers to a name in the context.
				keyword_arguments.append(argument_node)

			self._additional_context[inserted_function.__name__] = inserted_function #Add to context so that we can call it.
			self._call_node = ast.Expr(value=ast.Call(func=ast.Name(id=inserted_function.__name__, ctx=ast.Load()), args=positional_arguments, keywords=keyword_arguments)) #Construct the actual node.

		def visit_ExceptHandler(self, node):
			"""
			Insert function calls inside an exception handler.

			:param node: The exception handler to insert function calls in.
			:return: A modified exception handler with function calls in its
				body.
			"""
			node.body = self._insert_calls(node.body)
			return node

		def visit_For(self, node):
			"""
			Inserts function calls inside a for node.

			:param node: The for node to insert function calls in.
			:return: A modified for node with function calls in its body.
			"""
			node.body = self._insert_calls(node.body)
			node.orelse = self._insert_calls(node.orelse)
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
			node.body = self._insert_calls(node.body)
			return node

		def visit_If(self, node):
			"""
			Inserts function calls inside an if node.

			:param node: The if node to insert function calls in.
			:return: A modified if node with function calls in its body.
			"""
			node.body = self._insert_calls(node.body)
			node.orelse = self._insert_calls(node.orelse)
			return node

		def visit_Try(self, node):
			"""
			Insert function calls inside a try node.

			:param node: The try node to insert function calls in.
			:return: A modified try node with function calls in its body.
			"""
			node.body = self._insert_calls(node.body)
			node.orelse = self._insert_calls(node.orelse)
			node.finalbody = self._insert_calls(node.finalbody)
			return node

		def visit_While(self, node):
			"""
			Insert function calls inside a while node.

			:param node: The while node to insert function calls in.
			:return: A modified while node with function calls in its body.
			"""
			node.body = self._insert_calls(node.body)
			node.orelse = self._insert_calls(node.orelse)
			return node

		def visit_With(self, node):
			"""
			Insert function calls inside a with node.

			:param node: The with node to insert function calls in.
			:return: A modified with node with function calls in its body.
			"""
			node.body = self._insert_calls(node.body)
			return node

		def _insert_calls(self, body):
			"""
			Insert function calls into a list of expressions.

			:param body: The list of expressions to insert the function calls
				in.
			:return: A new list of expressions, with function calls.
			"""
			new_body = [self._call_node]
			for child in body:
				new_body.append(child)
				new_body.append(self._call_node)
			return new_body

	call_inserter = FunctionInserter(inserted_function, inserted_function_args, inserted_function_kwargs)
	transformed_syntax = call_inserter.visit(syntax_tree) #Insert function calls everywhere.
	ast.fix_missing_locations(transformed_syntax)
	compiled = compile(transformed_syntax, filename="<call_inserter>", mode="exec")
	scope = call_inserter._additional_context
	exec(compiled, scope) #Execute the transformed code inside an empty scope.
	new_func = scope[call_inserter._outer_function_name] #The function definition inside the code is now the only name in this scope.

	return new_func