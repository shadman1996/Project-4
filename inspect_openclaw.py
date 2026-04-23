import openclaw
import inspect

print("OpenClaw version:", getattr(openclaw, '__version__', 'unknown'))
print("\nDir:")
print(dir(openclaw))

print("\nClasses:")
for name, obj in inspect.getmembers(openclaw):
    if inspect.isclass(obj):
        print(f"- {name}: {obj.__module__}")
        try:
            print("  Doc:", obj.__doc__)
            print("  Init sig:", inspect.signature(obj.__init__))
        except Exception as e:
            pass
