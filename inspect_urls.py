from webull import webull
import inspect

wb = webull()
print("DIR(_urls):", dir(wb._urls))

# Iterate and find any that look like a login URL
for attr in dir(wb._urls):
    if not attr.startswith("__"):
        try:
            val = getattr(wb._urls, attr)()
            if "login" in val:
                print(f"{attr}: {val}")
        except:
            pass
