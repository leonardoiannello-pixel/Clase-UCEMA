"""Run the unchanged 20 historical workflow tests against V4.1 in this process.

Only test wiring changes: point ROOT to original fixtures and import workflow
under the same module name used by historical mocks. No historical files edited.
"""
import importlib.util
from pathlib import Path
import sys
import unittest

PACKAGE=Path(__file__).resolve().parents[2]
HISTORICAL=PACKAGE.parent/'Entrega-2/v4'
sys.path.insert(0,str(HISTORICAL))
sys.path.insert(0,str(PACKAGE/'agente/v41'))
spec=importlib.util.spec_from_file_location('workflow',PACKAGE/'agente/v41/workflow_v41.py')
workflow=importlib.util.module_from_spec(spec)
sys.modules['workflow']=workflow
spec.loader.exec_module(workflow)
workflow.ROOT=HISTORICAL  # Fixture/renderer paths only; comparator stays V4.1.
suite=unittest.defaultTestLoader.discover(str(HISTORICAL/'tests'),pattern='test_workflow.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(not result.wasSuccessful())
