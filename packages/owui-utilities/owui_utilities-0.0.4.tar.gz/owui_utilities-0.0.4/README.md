# OWUI Utilities
Package to add in reusable behavior for built-in OWUI tools

### Motivation
Develop utility functions to be reused across OWUI built-in tools. Some tools are more appropriately deployed as external tool servers (openapi/MCP), but some tools benefit from built-in events that can interact via the UI during execution. Utilities to make these tools better can be built once and reused across tools.

Currently just a single utility exists, if more utilities are added then specific readmes can be moved out to individual sections.

### Param Confirm: Background
Tool calls in OWUI can be great, but they are executed at the discretion of the LLM. The LLM will parse out the necessary arguments and decide whether to make the tool call. This has some potential downsides:
1)  This could be detrimental if the tool call is sending information to an external api that the user did not intend
2)  LLm could be performing an action the user may not have intended and these tool calls can have real effects, ie send emails, databases changes etc...
3) OWUI provides very little insight for users as to what tool is called and with what arguments 

We can mitigate this with reusable function decorators. The parameter_confirm decorator is used to alert the user to the current tool call and what arguments are being passed to the tool call. This could be expanded for argument collection when parsing by llm proves to not work, and we could be provide more info on what is returned by the tool call. There is room for lots of different utilities.


### Example
![image](images/param_confirm.png)
The above example shows a user asking to make a sentence from a few words. The description of the tool allows the LLM to decide that this is the proper tool to call, and the description of the arguments lets the LLM parse the user sentence to get what it needs. Rather than executing the tool call, OWUI asks if the user would like to execute the tool call and alerts the user as to which arguments are being used. If the user confirms then the tool executes, otherwise it does not. This is a trivial example but illustrates the usage.

### Usage
These are intended for "built-in tools", i.e. tools installed in OWUI the run client-side in the browser.  This approach relies on events which are only for local tools, not for external MCP/OpenAPI tool servers.

These function can be exposed in a few ways. 

1) Code can be packaged and published to pypi with something like twine. This is useful to make the local tools more concise. Then simply add as a requirement to the local tool with the proper module docstring section such as below. This is then installed on the backend when the tool is saved. Currently, the Gitlab CI/CD pipeline script publishes to the Gitlab package registry and CSDE Artifactory.


```bash
python -m build
python -m twine upload dist/*
```

tool header
```
requirements: pydantic, owui_tools
```

2) The other options is include the entirety of the decorator in the code of the local tool. 

Functions that wish use this simply need to import the function and decorate themselves with it.
```python
from owui_tools import parameter_confirm
...<some stuff>
class Tools:
    <init and valves and stuff>
    @parameter_confirm(filter_args=True)
    def <function_name>(
        self,
        <arg1>: <type>,
        <arg2>: <type>,
        <arg3>: <type>,
        __event_emitter__: Callable[[dict], Awaitable[None]],
        __event_call__: Callable[[dict], Awaitable[None]],
        __user__: dict = {},
    ) -> str:
    """
    Normal OWUI function and param descriptions
    """
    <Normal function defintion>
```

If the tool itself does not need to use the event functions they should still be included for the decorator to use. A full example can be seen in the test directory. 