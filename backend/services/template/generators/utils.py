"""
LaTeX 格式化工具函数

用于将数学表达式格式化为 LaTeX 格式，确保前端 MathJax 渲染效果美观。

使用规范：
- 纯计算题：使用 `latex_calculation()` 将整个表达式包裹为 LaTeX
- 比较大小：使用 `latex_comparison()` 格式化比较表达式
- 单位换算：使用 `latex_number()` 仅包裹数字部分
- 分数：使用 `latex_fraction()` 格式化分数
"""


def latex_number(num: int | float) -> str:
    """
    格式化单个数字为 LaTeX 格式

    用于单位换算题目中仅包裹数字部分

    Args:
        num: 数字（整数或浮点数）

    Returns:
        LaTeX 格式的数字字符串

    Examples:
        >>> latex_number(5)
        '$5$'
        >>> latex_number(3.14)
        '$3.14$'
    """
    return f"${num}$"


def latex_calculation(parts: list | str) -> str:
    """
    格式化计算题表达式为 LaTeX 格式

    自动在运算符前后添加空格，确保 MathJax 渲染间距美观

    Args:
        parts: 表达式各部分（数字和运算符）的列表，或直接的表达式字符串

    Returns:
        LaTeX 格式的计算表达式

    Examples:
        >>> latex_calculation([5, '+', 3, '='])
        '$5 + 3 = （ ）$'
        >>> latex_calculation("5+3=")
        '$5 + 3 = （ ）$'
    """
    if isinstance(parts, str):
        # 如果是字符串，先按运算符分割再重组
        expr = parts
        # 确保运算符前后有空格
        for op in ['+', '-', '=', r'\times', r'\div']:
            expr = expr.replace(op, f' {op} ')
        # 清理多余空格
        expr = ' '.join(expr.split())
        return f"${expr} （ ）$"
    else:
        # 如果是列表，用空格连接
        expr = ' '.join(str(p) for p in parts)
        # 清理多余空格
        expr = ' '.join(expr.split())
        return f"${expr} （ ）$"


def latex_comparison(a, b) -> str:
    """
    格式化比较大小题目

    Args:
        a: 左侧数字或表达式
        b: 右侧数字或表达式

    Returns:
        LaTeX 格式的比较表达式

    Examples:
        >>> latex_comparison(5, 3)
        '$5 （ ） 3$'
        >>> latex_comparison('3+2', '4')
        '$3 + 2 （ ） 4$'
    """
    # 如果是字符串表达式，确保运算符有空格
    if isinstance(a, str):
        for op in ['+', '-', r'\times', r'\div']:
            a = a.replace(op, f' {op} ')
        a = ' '.join(a.split())

    if isinstance(b, str):
        for op in ['+', '-', r'\times', r'\div']:
            b = b.replace(op, f' {op} ')
        b = ' '.join(b.split())

    return f"${a} （ ） {b}$"


def latex_fraction(numerator: int, denominator: int) -> str:
    """
    格式化分数为 LaTeX 格式

    Args:
        numerator: 分子
        denominator: 分母

    Returns:
        LaTeX 格式的分数

    Examples:
        >>> latex_fraction(3, 4)
        '$\\\\frac{3}{4}$'
    """
    return f"$\\frac{{{numerator}}}{{{denominator}}}$"


def latex_fill_in_blank(value_before: str, value_after: str) -> str:
    """
    格式化填空题题干

    用于单位换算等题目，填空部分用全角括号表示

    Args:
        value_before: 填空前的内容（可包含 LaTeX 数字）
        value_after: 填空后的内容

    Returns:
        完整的填空题题干

    Examples:
        >>> latex_fill_in_blank("$5$", "元 = （ ）角")
        '$5$ 元 = （ ）角'
    """
    return f"{value_before} {value_after}"
