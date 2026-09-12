"""Conservative representation equivalence, not general formula simplification.

Only the known simple sheet names Detail and Summary are accepted. Strings,
external references, structured references and other quoted names stay verbatim.
"""
import re

# Whole lexical atoms: never substitute inside Excel string literals, quoted
# names, or bracketed references. Doubled quote escaping remains untouched.
ATOMS = re.compile(r'"(?:[^"]|"")*"|\[(?:[^\[\]]|\[[^\]]*\])*\]|\'(?:[^\']|\'\')*\'|.', re.DOTALL)
OPTIONAL_QUOTED_SHEETS = {"'Detail'": 'Detail', "'Summary'": 'Summary'}


def canonical_formula(value):
    """Remove optional quotes only from standalone known sheet qualifiers.

    Fail closed for malformed/incomplete formulas and unfamiliar syntax. This
    function does not change case, spaces, operators, constants or cell addresses.
    """
    if not isinstance(value, str) or not value.startswith('='):
        return value
    result = []
    for match in ATOMS.finditer(value):
        token = match.group()
        start, end = match.span()
        if token in {'"', "'", '[', ']'}:
            return value  # Unclosed/unsupported lexical atom: no normalization.
        # Qualifier must follow a formula delimiter, not a name, external book
        # reference, or 3D range colon. Do not rewrite a partial identifier.
        boundary = start > 0 and value[start-1] in '=+-*/^&(),;<>% '
        if token in OPTIONAL_QUOTED_SHEETS and boundary and value[end:end+1] == '!':
            token = OPTIONAL_QUOTED_SHEETS[token]
        result.append(token)
    return ''.join(result)


def equivalent_formulas(left, right):
    if left == right:
        return True
    if not (isinstance(left, str) and isinstance(right, str)
            and left.startswith('=') and right.startswith('=')):
        return False
    return canonical_formula(left) == canonical_formula(right)
