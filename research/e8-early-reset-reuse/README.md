# Earlier clean resets on PR433

Conditional kappa = 0.001128250848293019, approximately 0.659% above PR433. Eleven helpers removed, R758 to R747. The exact bit saving is 0.001129525236098815991751; the unchanged complex saving is 0.001183986549206329.

Run `python -B research/e8-early-reset-reuse/verify.py /absolute/new/output` with Python 3.11 or 3.14. Standard library only. The wrapper freshly verifies the pinned parent with all phases before reconstructing and checking the changed bit program.

At draft submission the changed emitted bit, independent bank audit, two rational moments and exact finite assembly passed locally against the previously fully replayed parent. The new uninterrupted wrapper and GitHub CI are pending. Local receipts distinguish that scope.
