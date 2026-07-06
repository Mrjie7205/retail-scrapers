"""公共异常类型。"""


class ScraperError(RuntimeError):
    """所有可预期抓取错误的基类。"""


class ConfigurationError(ScraperError):
    """用户参数或渠道配置不合法。"""


class ExtractionError(ScraperError):
    """页面或接口无法提取有效数据。"""


class CompletenessError(ScraperError):
    """抓到了部分数据，但完整性检查未通过。"""
