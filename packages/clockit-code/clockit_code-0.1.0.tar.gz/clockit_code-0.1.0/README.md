![clockit](images/clockit.png)

# clockit

A super simple utility to time your python code.

## To-Do 

Deploy to PyPi

## usage

```python

with clockit() as ct:
    # do something expensive...
    my_slow_func()

print(ct)  # Time: 2.037 seconds
```

It prints nothing by default — just gives you structured access:

```python
ct.elapsed   # the float value
ct.readout   # the pretty string
```

We can print (or log, etc) inline, too.
```python
with clockit(printer=print) as ct:
    # your stuff
    another_func()
```
Would output:
```bash
Time: X.XX seconds
```

You can nest it too:

```python

with clockit() as ct_global:
    with clockit() as ct:
        time.sleep(1) # stuff that takes ~ 1 sec

    with clockit() as ct2:
        time.sleep(3) # stuff that takes ~ 3 seconds

print(ct)
print(ct2)
print(ct_global)
```

would output:

```bash
Time: 1.010 seconds
Time: 3.008 seconds
Time: 4.018 seconds
```

See more examples in ```examples.ipynb```