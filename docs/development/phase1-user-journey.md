# Phase 1 User Journey

Phase 1 turns Echel from a scaffold-first workflow into a product-first workflow.

## Flow

1. Define the product.

```bash
python3 tools/echel.py define \
  --problem "..." \
  --solution "..." \
  --direction "..." \
  --users "..." \
  --mvp "..." \
  --constraints "..." \
  --risks "..." \
  --stack "..." \
  --success "..."
```

2. Clarify missing intent.

```bash
python3 tools/echel.py clarify
python3 tools/echel.py clarify --field mvp --answer "- First useful slice"
```

3. Plan the MVP.

```bash
python3 tools/echel.py plan
```

4. Select next work.

```bash
python3 tools/echel.py next
```

5. Generate an agent work packet.

```bash
python3 tools/echel.py packet
```

6. Implement, verify, and update memory.

```bash
make wiki-health
python3 tools/echel.py doctor
```

## Principle

The user steers product direction. Echel turns that direction into product memory, planning, work items, and agent-ready execution context.
