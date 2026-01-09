"""
Simple Python usage example of the `jsz3` module when running inside Pyodide.

This file is for documentation only; it is executed inside the browser by `src/main.js`.
"""
import jsz3
import asyncio

async def main():
	jsz3.init()
	jsz3.declare_int('a')
	jsz3.declare_int('b')
	jsz3.add_eq_sum(['a', 'b'], 7)
	jsz3.add_gt('a', 2)
	sat = await jsz3.check()
	print('sat =', sat)
	model = await jsz3.model()
	print('model =', model)

asyncio.run(main())
