**Title:** [Bug] "Defaults" button in Additional Inputs does not restore defaults (it restores the last saved values) and prints the whole dict to the console

## Summary
After changing values in Additional Inputs and pressing Save, the Defaults button no longer resets the tab to its original values. It re-applies the last saved ones.

## Steps to reproduce
1. Basic Inputs: span 20 m, carriageway 4.25 m, Optimized. Open Additional Inputs.
2. Typical Section Details: change Deck Thickness from 250 to 275. Press Save ("Inputs saved successfully").
3. Re-open Additional Inputs, press **Defaults** on that tab.
4. Expected: Deck Thickness returns to 250. Actual: it stays 275.
5. Watch the terminal: every click on Defaults also prints the full working dictionary.

(Only File > Save Input, see #71, then resets everything to defaults, as a side effect of a different bug.)

## Root cause
`src/osdagbridge/desktop/ui/dialogs/additional_input/additional_inputs.py`
- `reset_active_tab_defaults()` (about line 446) restores widgets from `self.default_input_dict`.
- `set_input_dictionary()` (about line 223) makes `self.default_input_dict` the **same object** as the main window's `input_dict`.
- `_save_inputs()` (about line 519) runs `self.default_input_dict.update(self.working_input_dict)`.

So after the first Save, the "defaults" are the user's own values. The real factory defaults live only in `core/bridge_types/plate_girder/defaults.py`.

Also, lines 158-161 connect a leftover debug call to the same button:
```python
from pprint import pprint
self.defaults_button.clicked.connect(lambda: pprint(self.working_input_dict))
```

## Suggested fix
1. Keep an untouched copy of the factory defaults, taken before the user can edit anything, and reset from that:
```python
# in __init__ or the first set_input_dictionary()
import copy
self._factory_defaults = copy.deepcopy(input_dict)   # once

# in reset_active_tab_defaults()
value = self._factory_defaults.get(name)
```
2. Do not `update()` the factory copy in `_save_inputs()`.
3. Delete the `pprint` connection (lines ~160-161).

## Impact
The button looks like it works but does nothing useful once any value was saved, so users cannot undo custom values from the dialog.

## Evidence to attach
Screenshots: deck thickness 275 before and after pressing Defaults; terminal output showing the printed dict.
