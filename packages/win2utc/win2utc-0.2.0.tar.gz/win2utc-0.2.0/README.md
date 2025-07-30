
## **How to Install/Use the CLI**

From your package root:

```sh
pip install --upgrade win2utc

win2utc "2025-11-01 10:00:00" "Pacific Standard Time"
win2utc "2025-11-01 17:00:00" "Pacific Standard Time" --from-utc
win2utc --range "2025-11-01 00:00:00" "2025-11-01 23:59:59" "Pacific Standard Time"
```

---


### Examples

**To UTC:**
```
win2utc "2025-07-03 15:00:00" "Eastern Standard Time"
```

**From UTC:**

```
win2utc "2025-07-03 19:00:00" "Eastern Standard Time" --from-utc
```

**Time Range to UTC:**

```sh
win2utc --range "2025-07-03 00:00:00" "2025-07-03 23:59:59" "Eastern Standard Time"
```
---
## **Next Steps**

- Add the above code to your project files.
- Test: `python -m tests.test_converter`
- Install: `pip install -e .`
- Try the CLI!

---
