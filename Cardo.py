
'''
stack = []  # last value is the top of the stack

step:
    if stack is empty:
        stack = [ nextAction() ]

    # stack now has at least one element
    top = stack[-1]
    imminent(top)
    if stack and stack[-1] == top: # nothing else wants to precede us
        top.apply()
'''
