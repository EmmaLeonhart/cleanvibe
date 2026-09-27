"""Test package setup.

Point cleanvibe's Claude Code config path at a throwaway file, so no test can
ever write the real ~/.claude.json (cleanvibe.trust pre-trusts new project
folders there).
"""

import os
import tempfile

os.environ["CLEANVIBE_CLAUDE_CONFIG"] = os.path.join(
    tempfile.mkdtemp(prefix="cleanvibe-tests-"), ".claude.json"
)
