"""V4 implementation of the preserved V3 specification. Rates are fractions."""
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

D = lambda value: Decimal(str(value))
ZERO = D(0)
STEP = D('0.0001')


def pct(value):
    return D(value).quantize(STEP, rounding=ROUND_HALF_UP)


def salary(value):
    return int((D(value) / 100).quantize(D(1), rounding=ROUND_HALF_UP) * 100)


def weight(ratio):
    for threshold, result in [('.70', 4), ('.80', 2), ('.90', 1), ('1', '.5')]:
        if ratio < D(threshold):
            return D(result)
    return ZERO


def prepare(employee, market, parameters):
    e = dict(employee)
    base = D(e['June_Base_Salary'])
    if base <= 0 or e['Currency'] != 'ARS':
        raise ValueError('Positive ARS salary required: ' + e['Employee_ID'])
    promotion = e['Current_Rank'] != e['New_Rank']
    progression = not promotion and e['New_Grade'] > e['Current_Grade']
    flags = []
    if not promotion and e['New_Grade'] < e['Current_Grade']:
        flags.append('MOVEMENT_REVIEW_REQUIRED')
    rating = e['Performance_Rating']
    if rating not in range(1, 6):
        raise ValueError('Invalid rating: ' + e['Employee_ID'])
    e['General_Increase_Pct'] = pct(parameters['General_Increase'])
    e['Promotion_Increase_Pct'] = pct(parameters['Promotion_Increase']) if promotion else ZERO
    e['Progression_Increase_Pct'] = pct(parameters['Progression_Increase']) if progression else ZERO
    e['Protected_Increase_Pct'] = sum(e[k] for k in ['General_Increase_Pct', 'Promotion_Increase_Pct', 'Progression_Increase_Pct'])
    e['Protected_Salary'] = base * (1 + e['Protected_Increase_Pct'])
    e['Merit_Weight'] = ZERO if promotion or progression else D([0, '.5', 1, 2, 4][rating - 1])
    reference = market.get(e['Market_Job_Code'])
    if reference is not None and D(reference) <= 0:
        raise ValueError('Nonpositive market reference')
    e['WTW_Reference_Salary'] = D(reference) if reference is not None else None
    e['Initial_Compa_Ratio'] = base / D(reference) if reference is not None else None
    e['Preliminary_Compa_Ratio'] = e['Protected_Salary'] / D(reference) if reference is not None else None
    if reference is None:
        flags.append('MARKET_DATA_MISSING')
    e['Flag'] = ';'.join(flags)
    return e


def at_x(employee, x, rounded=True):
    e = dict(employee)
    base = D(e['June_Base_Salary'])
    merit = e['Merit_Weight'] * x
    if rounded:
        merit = pct(merit)
    before = base * (1 + e['Protected_Increase_Pct'] + merit)
    ref = e['WTW_Reference_Salary']
    mw = weight(before / ref) if ref else ZERO
    gap = max(ZERO, (ref - before) / base) if ref else ZERO
    market = min(mw * x, gap)
    if rounded:
        market = min(pct(market), gap.quantize(STEP, rounding=ROUND_FLOOR))
    raw_salary = base * (1 + e['Protected_Increase_Pct'] + merit + market)
    final_salary = salary(raw_salary) if rounded else raw_salary
    e.update(X=x, Merit_Increase_Pct=merit, Market_Weight=mw,
             Market_Increase_Pct=market, New_Salary=final_salary,
             Total_Increase_Pct=pct(D(final_salary) / base - 1),
             Final_Compa_Ratio=D(final_salary) / ref if ref else None)
    if rounded and market > 0 and ref and final_salary > ref and before <= ref:
        e['Flag'] = ';'.join(filter(None, [e['Flag'], 'MARKET_SALARY_ROUNDING_REVIEW_REQUIRED']))
    return e


def calculate_group(employees, budget):
    """Search each market-band interval: payroll has downward discontinuities.

    Within each interval it is monotone; global binary search is not valid.
    The final quantization follows the V3 round-X-then-decrement rule.
    """
    payroll = sum(D(e['June_Base_Salary']) for e in employees)
    maximum = payroll * (1 + D(budget))
    protected = sum(e['Protected_Salary'] for e in employees)
    if protected > maximum:
        result = [at_x(e, ZERO) for e in employees]
        for e in result:
            e['Flag'] = ';'.join(filter(None, [e['Flag'], 'BUDGET_INSUFICIENTE']))
        return result
    slope = sum(D(e['June_Base_Salary']) * e['Merit_Weight'] for e in employees)
    if not slope:
        # No finite maximum X once all market caps are exhausted. Do not invent X.
        raise ValueError('X_UNBOUNDED: business decision required for zero-merit group')
    upper = (maximum - protected) / slope
    breaks = {ZERO, upper}
    for e in employees:
        if e['WTW_Reference_Salary'] and e['Merit_Weight']:
            for band in map(D, ['.7', '.8', '.9', '1']):
                point = (band * e['WTW_Reference_Salary'] / D(e['June_Base_Salary']) - 1 - e['Protected_Increase_Pct']) / e['Merit_Weight']
                if ZERO < point < upper:
                    breaks.add(point)
    def cost(x):
        return sum(at_x(e, x, False)['New_Salary'] for e in employees)
    best = ZERO
    points = sorted(breaks)
    for left, right in zip(points, points[1:]):
        if cost(left) > maximum:
            continue
        lo, hi = left, right
        for _ in range(100):
            mid = (lo + hi) / 2
            if cost(mid) <= maximum:
                lo = mid
            else:
                hi = mid
        best = max(best, lo)
    if cost(upper) <= maximum:
        best = upper
    x = pct(best)
    while True:
        result = [at_x(e, x) for e in employees]
        if sum(e['New_Salary'] for e in result) <= maximum or x == 0:
            return result
        x = max(ZERO, x - STEP)


def human_result(e, adjustment, minimum, maximum):
    if isinstance(adjustment, bool) or not isinstance(adjustment, (int, float, Decimal)):
        raise ValueError('ADJUSTMENT_NOT_NUMERIC')
    adjustment = D(adjustment)
    if not adjustment.is_finite():
        raise ValueError('ADJUSTMENT_NOT_FINITE')
    if adjustment != pct(adjustment):
        raise ValueError('ADJUSTMENT_PRECISION')
    if not D(minimum) <= adjustment <= D(maximum):
        raise ValueError('ADJUSTMENT_OUT_OF_PARAMETERS')
    increase = pct(e['Total_Increase_Pct'] + adjustment)
    final = salary(D(e['June_Base_Salary']) * (1 + increase))
    if increase < e['Protected_Increase_Pct'] or final < salary(e['Protected_Salary']):
        raise ValueError('PROTECTED_FLOOR_VIOLATION')
    return dict(Discretionary_Adjustment_Pct=adjustment, Final_Increase_Pct=increase,
                Final_Salary=final, Final_Compa_Ratio=D(final) / e['WTW_Reference_Salary'] if e['WTW_Reference_Salary'] else None,
                Human_Modified=adjustment != 0)
