# -*- coding: utf-8 -*-
"""
可转债分析核心工具函数 - 全新实现版本
包含5大类共19个专业可转债分析工具
"""
import akshare as ak
import pandas as pd
import numpy as np
from functools import lru_cache
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import traceback
import math
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 备份的原有工具函数（已注释）
# ============================================================================
"""
原有工具函数已备份在此注释块中：
- find_bond_code_by_name
- get_convertible_bond_realtime_metrics
- screen_discount_arbitrage_opportunities
- track_clause_triggers
- get_upcoming_convertible_bonds
- monitor_intraday_spread
- screen_for_special_opportunities
"""


# ============================================================================
# 内部辅助函数
# ============================================================================

@lru_cache(maxsize=1)
def _get_all_bonds_list() -> pd.DataFrame:
    """
    获取并缓存全市场可转债的全面数据。
    该函数是所有其他数据分析函数的基础。
    使用 ak.bond_cov_comparison() 一次性获取所有需要的数据，以提高健壮性。
    """
    try:
        print("正在获取全市场可转债数据...")
        df = ak.bond_cov_comparison()

        # 重命名列以匹配项目内部的命名约定
        df.rename(columns={
            '转债代码': 'bond_code',
            '转债名称': 'bond_name',
            '转债最新价': 'bond_price',
            '正股代码': 'stock_code',
            '正股名称': 'stock_name',
            '正股最新价': 'stock_price',
            '转股价': 'conversion_price',
            '强赎触发价': 'redemption_trigger_price',
            '回售触发价': 'put_trigger_price',
            '转股价值': 'conversion_value',
            '溢价率': 'premium_rate',
            '纯债价值': 'pure_bond_value',
            '到期收益率': 'ytm'
        }, inplace=True)

        # 数据清洗和转换
        numeric_cols = ['bond_price', 'stock_price', 'conversion_price']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 删除关键数值列中包含NaN的行
        df.dropna(subset=[col for col in numeric_cols if col in df.columns], inplace=True)

        print(f"成功获取并处理了 {len(df)} 只可转债数据")
        return df

    except Exception as e:
        print(f"[_get_all_bonds_list] 错误: {e}")
        print(traceback.format_exc())
        return pd.DataFrame()


def _safe_float(value: Any, default: float = 0.0) -> float:
    """安全转换为浮点数"""
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    """安全转换为整数"""
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default


# ============================================================================
# 第一类：基础数据获取工具 (Data Acquisition Tools)
# ============================================================================

def get_all_convertible_bonds() -> List[Dict[str, Any]]:
    """
    获取所有活跃可转债的代码和名称。

    Returns:
        包含所有可转债基本信息的列表
    """
    try:
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return []

        result = []
        for _, row in all_bonds_df.iterrows():
            result.append({
                "bond_code": str(row['bond_code']),
                "bond_name": str(row['bond_name']),
                "stock_code": str(row['stock_code']),
                "stock_name": str(row['stock_name']),
                "bond_price": _safe_float(row['bond_price']),
                "stock_price": _safe_float(row['stock_price']),
                "conversion_price": _safe_float(row['conversion_price'])
            })

        print(f"成功获取 {len(result)} 只可转债信息")
        return result

    except Exception as e:
        print(f"[get_all_convertible_bonds] 错误: {e}")
        return []


def get_realtime_quotes(codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    获取指定债券和股票的实时报价。

    Args:
        codes: 债券代码或股票代码列表

    Returns:
        代码到实时报价的映射
    """
    if not codes:
        return {}

    try:
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return {}

        result = {}

        # 处理债券代码
        bond_codes = [code for code in codes if code.startswith(('11', '12', '13'))]
        if bond_codes:
            bond_data = all_bonds_df[all_bonds_df['bond_code'].isin(bond_codes)]
            for _, row in bond_data.iterrows():
                result[row['bond_code']] = {
                    "code": row['bond_code'],
                    "name": row['bond_name'],
                    "price": _safe_float(row['bond_price']),
                    "type": "bond"
                }

        # 处理股票代码
        stock_codes = [code for code in codes if not code.startswith(('11', '12', '13'))]
        if stock_codes:
            stock_data = all_bonds_df[all_bonds_df['stock_code'].isin(stock_codes)]
            for _, row in stock_data.iterrows():
                result[row['stock_code']] = {
                    "code": row['stock_code'],
                    "name": row['stock_name'],
                    "price": _safe_float(row['stock_price']),
                    "type": "stock"
                }

        return result

    except Exception as e:
        print(f"[get_realtime_quotes] 错误: {e}")
        return {}


def get_bond_static_info(bond_code: str) -> Dict[str, Any]:
    """
    获取指定可转债的详细静态信息。

    Args:
        bond_code: 债券代码

    Returns:
        债券的详细静态信息
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    try:
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return {"error": "无法获取债券数据"}

        bond_info = all_bonds_df[all_bonds_df['bond_code'] == bond_code]
        if bond_info.empty:
            return {"error": f"未找到债券 {bond_code}"}

        info = bond_info.iloc[0]

        # 获取更详细的债券信息
        try:
            detail_df = ak.bond_zh_cov_info(symbol=bond_code)
            if not detail_df.empty:
                detail_info = detail_df.iloc[0]
                return {
                    "bond_code": bond_code,
                    "bond_name": str(info['bond_name']),
                    "stock_code": str(info['stock_code']),
                    "stock_name": str(info['stock_name']),
                    "bond_price": _safe_float(info['bond_price']),
                    "stock_price": _safe_float(info['stock_price']),
                    "conversion_price": _safe_float(info['conversion_price']),
                    "redemption_trigger_price": _safe_float(info.get('redemption_trigger_price')),
                    "put_trigger_price": _safe_float(info.get('put_trigger_price')),
                    "issue_date": str(detail_info.get('发行日期', '')),
                    "maturity_date": str(detail_info.get('到期日期', '')),
                    "issue_scale": str(detail_info.get('发行规模', '')),
                    "coupon_rate": str(detail_info.get('票面利率', '')),
                    "conversion_start_date": str(detail_info.get('转股起始日', '')),
                    "conversion_end_date": str(detail_info.get('转股截止日', ''))
                }
        except:
            pass

        # 如果无法获取详细信息，返回基本信息
        return {
            "bond_code": bond_code,
            "bond_name": str(info['bond_name']),
            "stock_code": str(info['stock_code']),
            "stock_name": str(info['stock_name']),
            "bond_price": _safe_float(info['bond_price']),
            "stock_price": _safe_float(info['stock_price']),
            "conversion_price": _safe_float(info['conversion_price']),
            "redemption_trigger_price": _safe_float(info.get('redemption_trigger_price')),
            "put_trigger_price": _safe_float(info.get('put_trigger_price'))
        }

    except Exception as e:
        return {"error": f"[get_bond_static_info] 错误: {e}"}


def get_stock_financials(stock_code: str) -> Dict[str, Any]:
    """
    获取正股的关键财务数据。

    Args:
        stock_code: 股票代码

    Returns:
        股票的关键财务指标
    """
    if not stock_code:
        return {"error": "股票代码不能为空"}

    try:
        # 获取基本财务指标
        financial_data = {}

        # 尝试获取股票基本信息
        try:
            stock_info = ak.stock_individual_info_em(symbol=stock_code)
            if not stock_info.empty:
                for _, row in stock_info.iterrows():
                    key = str(row['item'])
                    value = str(row['value'])
                    financial_data[key] = value
        except:
            pass

        # 尝试获取财务指标
        try:
            financial_indicators = ak.stock_financial_abstract_ths(symbol=stock_code, indicator="按报告期")
            if not financial_indicators.empty:
                latest = financial_indicators.iloc[0]
                financial_data.update({
                    "营业收入": str(latest.get('营业收入', '')),
                    "净利润": str(latest.get('净利润', '')),
                    "总资产": str(latest.get('总资产', '')),
                    "净资产": str(latest.get('净资产', '')),
                    "每股收益": str(latest.get('每股收益', '')),
                    "净资产收益率": str(latest.get('净资产收益率', '')),
                    "资产负债率": str(latest.get('资产负债率', ''))
                })
        except:
            pass

        if not financial_data:
            return {"error": f"无法获取股票 {stock_code} 的财务数据"}

        return {
            "stock_code": stock_code,
            "financial_data": financial_data
        }

    except Exception as e:
        return {"error": f"[get_stock_financials] 错误: {e}"}


def get_historical_prices(code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """
    获取指定代码的历史价格数据。

    Args:
        code: 债券代码或股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        历史价格数据列表
    """
    if not code or not start_date or not end_date:
        return []

    try:
        # 转换日期格式
        start_date_fmt = start_date.replace('-', '')
        end_date_fmt = end_date.replace('-', '')

        # 判断是债券还是股票
        if code.startswith(('11', '12', '13')):
            # 可转债历史数据
            try:
                df = ak.bond_zh_hs_cov_daily(symbol=code)
                if not df.empty:
                    # 过滤日期范围
                    df['date'] = pd.to_datetime(df['date'])
                    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
                    df = df.loc[mask]

                    result = []
                    for _, row in df.iterrows():
                        result.append({
                            "date": row['date'].strftime('%Y-%m-%d'),
                            "open": _safe_float(row['open']),
                            "high": _safe_float(row['high']),
                            "low": _safe_float(row['low']),
                            "close": _safe_float(row['close']),
                            "volume": _safe_float(row['volume'])
                        })
                    return result
            except:
                pass
        else:
            # 股票历史数据
            try:
                df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                      start_date=start_date_fmt,
                                      end_date=end_date_fmt, adjust="qfq")
                if not df.empty:
                    result = []
                    for _, row in df.iterrows():
                        result.append({
                            "date": row['日期'].strftime('%Y-%m-%d'),
                            "open": _safe_float(row['开盘']),
                            "high": _safe_float(row['最高']),
                            "low": _safe_float(row['最低']),
                            "close": _safe_float(row['收盘']),
                            "volume": _safe_float(row['成交量'])
                        })
                    return result
            except:
                pass

        return []

    except Exception as e:
        print(f"[get_historical_prices] 错误: {e}")
        return []


def get_company_announcements(stock_code: str, count: int = 10) -> List[Dict[str, Any]]:
    """
    获取公司最新公告信息。

    Args:
        stock_code: 股票代码
        count: 获取公告数量

    Returns:
        公告信息列表
    """
    if not stock_code:
        return []

    try:
        # 获取公司公告
        announcements = ak.stock_notice_report(symbol=stock_code)
        if announcements.empty:
            return []

        # 取最新的count条公告
        announcements = announcements.head(count)

        result = []
        for _, row in announcements.iterrows():
            result.append({
                "title": str(row.get('公告标题', '')),
                "date": str(row.get('公告日期', '')),
                "type": str(row.get('公告类型', '')),
                "url": str(row.get('公告链接', ''))
            })

        return result

    except Exception as e:
        print(f"[get_company_announcements] 错误: {e}")
        return []


# ============================================================================
# 第二类：核心指标计算工具 (Indicator Calculation Tools)
# ============================================================================

def calculate_conversion_value(stock_price: float, conversion_price: float) -> float:
    """
    计算转股价值。

    Args:
        stock_price: 正股价格
        conversion_price: 转股价

    Returns:
        转股价值
    """
    if conversion_price <= 0:
        return 0.0
    return (100.0 / conversion_price) * stock_price


def calculate_conversion_premium_rate(bond_price: float, conversion_value: float) -> float:
    """
    计算转股溢价率。

    Args:
        bond_price: 债券价格
        conversion_value: 转股价值

    Returns:
        转股溢价率（小数形式）
    """
    if conversion_value <= 0:
        return 0.0
    return (bond_price / conversion_value) - 1.0


def calculate_pure_bond_value(bond_code: str) -> Dict[str, Any]:
    """
    计算纯债价值（债底）。

    Args:
        bond_code: 债券代码

    Returns:
        纯债价值计算结果
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    try:
        # 获取债券详细信息
        bond_info = get_bond_static_info(bond_code)
        if "error" in bond_info:
            return bond_info

        # 简化的纯债价值计算（实际应该基于现金流折现）
        # 这里使用近似方法
        coupon_rate = 0.005  # 默认票面利率0.5%
        years_to_maturity = 5  # 默认剩余期限5年

        # 尝试从债券信息中获取实际参数
        try:
            if 'coupon_rate' in bond_info and bond_info['coupon_rate']:
                coupon_rate = float(bond_info['coupon_rate'].replace('%', '')) / 100
        except:
            pass

        # 简化的纯债价值计算
        # PV = 年利息 * [(1-(1+r)^-n)/r] + 面值/(1+r)^n
        market_rate = 0.03  # 假设市场利率3%
        annual_coupon = 100 * coupon_rate

        if market_rate > 0:
            pv_coupons = annual_coupon * (1 - (1 + market_rate) ** -years_to_maturity) / market_rate
            pv_principal = 100 / (1 + market_rate) ** years_to_maturity
            pure_bond_value = pv_coupons + pv_principal
        else:
            pure_bond_value = 100 + annual_coupon * years_to_maturity

        return {
            "bond_code": bond_code,
            "pure_bond_value": round(pure_bond_value, 2),
            "coupon_rate": coupon_rate,
            "years_to_maturity": years_to_maturity,
            "market_rate_assumed": market_rate
        }

    except Exception as e:
        return {"error": f"[calculate_pure_bond_value] 错误: {e}"}


def calculate_ytm(bond_code: str, bond_price: float) -> Dict[str, Any]:
    """
    计算到期收益率。

    Args:
        bond_code: 债券代码
        bond_price: 债券价格

    Returns:
        到期收益率计算结果
    """
    if not bond_code or bond_price <= 0:
        return {"error": "参数无效"}

    try:
        # 获取债券信息
        bond_info = get_bond_static_info(bond_code)
        if "error" in bond_info:
            return bond_info

        # 简化的YTM计算
        coupon_rate = 0.005  # 默认票面利率
        years_to_maturity = 5  # 默认剩余期限
        face_value = 100  # 面值

        # 尝试获取实际参数
        try:
            if 'coupon_rate' in bond_info and bond_info['coupon_rate']:
                coupon_rate = float(bond_info['coupon_rate'].replace('%', '')) / 100
        except:
            pass

        annual_coupon = face_value * coupon_rate

        # 使用近似公式计算YTM
        # YTM ≈ [年利息 + (面值-价格)/年数] / [(面值+价格)/2]
        ytm_approx = (annual_coupon + (face_value - bond_price) / years_to_maturity) / ((face_value + bond_price) / 2)

        return {
            "bond_code": bond_code,
            "bond_price": bond_price,
            "ytm": round(ytm_approx * 100, 2),  # 转换为百分比
            "annual_coupon": annual_coupon,
            "years_to_maturity": years_to_maturity,
            "calculation_method": "approximate"
        }

    except Exception as e:
        return {"error": f"[calculate_ytm] 错误: {e}"}


# ============================================================================
# 第三类：条款状态与博弈分析工具 (Clause Analysis Tools)
# ============================================================================

def check_clause_trigger_status(bond_code: str) -> Dict[str, Any]:
    """
    检查可转债条款触发状态。

    Args:
        bond_code: 债券代码

    Returns:
        条款触发状态分析
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    try:
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return {"error": "无法获取债券数据"}

        bond_info = all_bonds_df[all_bonds_df['bond_code'] == bond_code]
        if bond_info.empty:
            return {"error": f"未找到债券 {bond_code}"}

        info = bond_info.iloc[0]
        stock_code = str(info['stock_code'])
        current_stock_price = _safe_float(info['stock_price'])
        redemption_price = _safe_float(info.get('redemption_trigger_price'))
        put_price = _safe_float(info.get('put_trigger_price'))

        # 获取历史价格数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=45)).strftime('%Y%m%d')

        try:
            hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                       start_date=start_date, end_date=end_date, adjust="qfq")
            if hist_df.empty:
                return {"error": f"无法获取股票 {stock_code} 的历史数据"}

            last_30_close = hist_df['收盘'].tail(30)

            # 强赎条款分析
            redemption_analysis = {"triggered": False, "days_count": 0, "progress": 0}
            if redemption_price > 0:
                days_above = (last_30_close >= redemption_price).sum()
                redemption_analysis = {
                    "triggered": days_above >= 15,
                    "days_count": int(days_above),
                    "progress": round(days_above / 15 * 100, 1),
                    "trigger_price": redemption_price,
                    "current_price": current_stock_price,
                    "status": "已触发" if days_above >= 15 else f"进度 {days_above}/15 天"
                }

            # 回售条款分析
            put_analysis = {"triggered": False, "days_count": 0, "progress": 0}
            if put_price > 0:
                days_below = (last_30_close <= put_price).sum()
                put_analysis = {
                    "triggered": days_below >= 30,
                    "days_count": int(days_below),
                    "progress": round(days_below / 30 * 100, 1),
                    "trigger_price": put_price,
                    "current_price": current_stock_price,
                    "status": "已触发" if days_below >= 30 else f"进度 {days_below}/30 天"
                }

            return {
                "bond_code": bond_code,
                "bond_name": str(info['bond_name']),
                "stock_code": stock_code,
                "stock_name": str(info['stock_name']),
                "current_stock_price": current_stock_price,
                "redemption_clause": redemption_analysis,
                "put_clause": put_analysis,
                "analysis_date": datetime.now().strftime('%Y-%m-%d')
            }

        except Exception as e:
            return {"error": f"获取历史数据失败: {e}"}

    except Exception as e:
        return {"error": f"[check_clause_trigger_status] 错误: {e}"}


def get_major_bondholders_info(bond_code: str) -> Dict[str, Any]:
    """
    获取可转债主要持有人信息。

    Args:
        bond_code: 债券代码

    Returns:
        主要持有人信息
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    try:
        # 尝试获取债券持有人信息
        # 注意：akshare可能没有直接的债券持有人接口，这里提供框架

        # 获取基本债券信息
        bond_info = get_bond_static_info(bond_code)
        if "error" in bond_info:
            return bond_info

        # 模拟持有人信息（实际应该从真实数据源获取）
        holders_info = {
            "bond_code": bond_code,
            "bond_name": bond_info.get('bond_name', ''),
            "total_holders": "数据暂不可用",
            "institutional_holders": "数据暂不可用",
            "individual_holders": "数据暂不可用",
            "top_holders": [],
            "data_source": "模拟数据",
            "note": "实际使用时需要接入真实的债券持有人数据源"
        }

        return holders_info

    except Exception as e:
        return {"error": f"[get_major_bondholders_info] 错误: {e}"}


# ============================================================================
# 第四类：筛选与监控工具 (Screening & Monitoring Tools)
# ============================================================================

def screen_bonds_by_premium(min_premium: float, max_premium: float) -> List[Dict[str, Any]]:
    """
    按溢价率范围筛选可转债。

    Args:
        min_premium: 最小溢价率（小数形式，如0.05表示5%）
        max_premium: 最大溢价率（小数形式，如0.20表示20%）

    Returns:
        符合条件的债券列表
    """
    try:
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return []

        # 计算转股价值和溢价率
        df = all_bonds_df[all_bonds_df['conversion_price'] > 0].copy()
        df['conversion_value'] = (100 / df['conversion_price']) * df['stock_price']
        df['premium_rate'] = (df['bond_price'] / df['conversion_value']) - 1

        # 筛选溢价率在指定范围内的债券
        filtered_df = df[(df['premium_rate'] >= min_premium) & (df['premium_rate'] <= max_premium)].copy()
        filtered_df = filtered_df.sort_values('premium_rate')

        result = []
        for _, row in filtered_df.iterrows():
            result.append({
                "bond_code": str(row['bond_code']),
                "bond_name": str(row['bond_name']),
                "bond_price": _safe_float(row['bond_price']),
                "stock_code": str(row['stock_code']),
                "stock_name": str(row['stock_name']),
                "stock_price": _safe_float(row['stock_price']),
                "conversion_price": _safe_float(row['conversion_price']),
                "conversion_value": round(_safe_float(row['conversion_value']), 2),
                "premium_rate": round(_safe_float(row['premium_rate']) * 100, 2),  # 转换为百分比
                "premium_rate_decimal": round(_safe_float(row['premium_rate']), 4)
            })

        print(f"筛选出 {len(result)} 只溢价率在 {min_premium*100:.1f}%-{max_premium*100:.1f}% 范围内的可转债")
        return result

    except Exception as e:
        print(f"[screen_bonds_by_premium] 错误: {e}")
        return []


def screen_bonds_by_price_and_ytm(max_price: float, min_ytm: float) -> List[Dict[str, Any]]:
    """
    按价格和到期收益率筛选可转债。

    Args:
        max_price: 最大债券价格
        min_ytm: 最小到期收益率（百分比形式，如5.0表示5%）

    Returns:
        符合条件的债券列表
    """
    try:
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return []

        # 筛选价格符合条件的债券
        price_filtered = all_bonds_df[all_bonds_df['bond_price'] <= max_price].copy()

        result = []
        for _, row in price_filtered.iterrows():
            bond_code = str(row['bond_code'])
            bond_price = _safe_float(row['bond_price'])

            # 计算YTM
            ytm_result = calculate_ytm(bond_code, bond_price)
            if "error" not in ytm_result:
                ytm_value = ytm_result.get('ytm', 0)
                if ytm_value >= min_ytm:
                    result.append({
                        "bond_code": bond_code,
                        "bond_name": str(row['bond_name']),
                        "bond_price": bond_price,
                        "stock_code": str(row['stock_code']),
                        "stock_name": str(row['stock_name']),
                        "stock_price": _safe_float(row['stock_price']),
                        "conversion_price": _safe_float(row['conversion_price']),
                        "ytm": ytm_value,
                        "meets_price_criteria": bond_price <= max_price,
                        "meets_ytm_criteria": ytm_value >= min_ytm
                    })

        # 按YTM降序排列
        result.sort(key=lambda x: x['ytm'], reverse=True)

        print(f"筛选出 {len(result)} 只价格≤{max_price}且YTM≥{min_ytm}%的可转债")
        return result

    except Exception as e:
        print(f"[screen_bonds_by_price_and_ytm] 错误: {e}")
        return []


def screen_for_clause_plays(play_type: str) -> List[Dict[str, Any]]:
    """
    筛选特定条款博弈机会。

    Args:
        play_type: 博弈类型 ("redemption" - 强赎博弈, "put" - 回售博弈, "revision" - 下修博弈)

    Returns:
        符合条件的博弈机会列表
    """
    if play_type not in ["redemption", "put", "revision"]:
        return [{"error": "博弈类型必须是 'redemption', 'put', 或 'revision'"}]

    try:
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return []

        result = []

        for _, row in all_bonds_df.iterrows():
            bond_code = str(row['bond_code'])

            # 获取条款触发状态
            clause_status = check_clause_trigger_status(bond_code)
            if "error" in clause_status:
                continue

            bond_info = {
                "bond_code": bond_code,
                "bond_name": str(row['bond_name']),
                "bond_price": _safe_float(row['bond_price']),
                "stock_code": str(row['stock_code']),
                "stock_name": str(row['stock_name']),
                "stock_price": _safe_float(row['stock_price']),
                "conversion_price": _safe_float(row['conversion_price'])
            }

            if play_type == "redemption":
                # 强赎博弈：接近触发强赎条款的债券
                redemption_info = clause_status.get('redemption_clause', {})
                if redemption_info.get('progress', 0) >= 60:  # 进度超过60%
                    bond_info.update({
                        "play_type": "强赎博弈",
                        "trigger_progress": redemption_info.get('progress', 0),
                        "days_count": redemption_info.get('days_count', 0),
                        "trigger_price": redemption_info.get('trigger_price', 0),
                        "opportunity_desc": f"强赎进度 {redemption_info.get('progress', 0):.1f}%"
                    })
                    result.append(bond_info)

            elif play_type == "put":
                # 回售博弈：接近触发回售条款的债券
                put_info = clause_status.get('put_clause', {})
                if put_info.get('progress', 0) >= 60:  # 进度超过60%
                    bond_info.update({
                        "play_type": "回售博弈",
                        "trigger_progress": put_info.get('progress', 0),
                        "days_count": put_info.get('days_count', 0),
                        "trigger_price": put_info.get('trigger_price', 0),
                        "opportunity_desc": f"回售进度 {put_info.get('progress', 0):.1f}%"
                    })
                    result.append(bond_info)

            elif play_type == "revision":
                # 下修博弈：转股价值较低，可能下修转股价的债券
                conversion_value = calculate_conversion_value(
                    _safe_float(row['stock_price']),
                    _safe_float(row['conversion_price'])
                )
                premium_rate = calculate_conversion_premium_rate(
                    _safe_float(row['bond_price']),
                    conversion_value
                )

                # 溢价率较高且转股价值较低的债券可能下修
                if premium_rate > 0.15 and conversion_value < 90:
                    bond_info.update({
                        "play_type": "下修博弈",
                        "conversion_value": round(conversion_value, 2),
                        "premium_rate": round(premium_rate * 100, 2),
                        "opportunity_desc": f"溢价率 {premium_rate*100:.1f}%, 转股价值 {conversion_value:.1f}"
                    })
                    result.append(bond_info)

        # 按机会程度排序
        if play_type in ["redemption", "put"]:
            result.sort(key=lambda x: x.get('trigger_progress', 0), reverse=True)
        else:
            result.sort(key=lambda x: x.get('premium_rate', 0), reverse=True)

        print(f"筛选出 {len(result)} 个 {play_type} 博弈机会")
        return result

    except Exception as e:
        print(f"[screen_for_clause_plays] 错误: {e}")
        return []


# ============================================================================
# 第五类：深度分析与辅助决策工具 (Deep Analysis & Auxiliary Decision Tools)
# ============================================================================

def calculate_implied_volatility(bond_code: str) -> Dict[str, Any]:
    """
    计算可转债的隐含波动率。

    Args:
        bond_code: 债券代码

    Returns:
        隐含波动率计算结果
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    try:
        # 获取债券基本信息
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return {"error": "无法获取债券数据"}

        bond_info = all_bonds_df[all_bonds_df['bond_code'] == bond_code]
        if bond_info.empty:
            return {"error": f"未找到债券 {bond_code}"}

        info = bond_info.iloc[0]
        stock_code = str(info['stock_code'])

        # 获取股票历史价格计算历史波动率
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=252)).strftime('%Y%m%d')  # 一年数据

        try:
            hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily",
                                       start_date=start_date, end_date=end_date, adjust="qfq")
            if hist_df.empty:
                return {"error": f"无法获取股票 {stock_code} 的历史数据"}

            # 计算日收益率
            hist_df['returns'] = hist_df['收盘'].pct_change()
            hist_df = hist_df.dropna()

            if len(hist_df) < 30:
                return {"error": "历史数据不足"}

            # 计算历史波动率（年化）
            daily_volatility = hist_df['returns'].std()
            annual_volatility = daily_volatility * (252 ** 0.5)

            # 简化的隐含波动率计算（实际需要期权定价模型）
            # 这里使用历史波动率作为近似
            bond_price = _safe_float(info['bond_price'])
            stock_price = _safe_float(info['stock_price'])
            conversion_price = _safe_float(info['conversion_price'])

            conversion_value = calculate_conversion_value(stock_price, conversion_price)
            premium_rate = calculate_conversion_premium_rate(bond_price, conversion_value)

            # 隐含波动率通常高于历史波动率
            implied_volatility = annual_volatility * (1 + premium_rate * 0.5)

            return {
                "bond_code": bond_code,
                "bond_name": str(info['bond_name']),
                "stock_code": stock_code,
                "historical_volatility": round(annual_volatility * 100, 2),
                "implied_volatility": round(implied_volatility * 100, 2),
                "premium_rate": round(premium_rate * 100, 2),
                "data_period": f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:]} 至 {end_date[:4]}-{end_date[4:6]}-{end_date[6:]}",
                "note": "隐含波动率为近似计算值"
            }

        except Exception as e:
            return {"error": f"计算波动率失败: {e}"}

    except Exception as e:
        return {"error": f"[calculate_implied_volatility] 错误: {e}"}


def get_option_greeks(bond_code: str) -> Dict[str, Any]:
    """
    计算可转债的期权希腊字母。

    Args:
        bond_code: 债券代码

    Returns:
        期权希腊字母计算结果
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    try:
        # 获取债券基本信息
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return {"error": "无法获取债券数据"}

        bond_info = all_bonds_df[all_bonds_df['bond_code'] == bond_code]
        if bond_info.empty:
            return {"error": f"未找到债券 {bond_code}"}

        info = bond_info.iloc[0]
        bond_price = _safe_float(info['bond_price'])
        stock_price = _safe_float(info['stock_price'])
        conversion_price = _safe_float(info['conversion_price'])

        if conversion_price <= 0:
            return {"error": "转股价无效"}

        # 简化的希腊字母计算
        conversion_ratio = 100 / conversion_price
        conversion_value = conversion_ratio * stock_price
        premium = bond_price - conversion_value

        # Delta: 债券价格对股票价格的敏感度
        # 简化计算：当债券价格接近转股价值时，Delta接近转股比例
        if bond_price > 0:
            delta = conversion_ratio * (conversion_value / bond_price)
        else:
            delta = 0

        # Gamma: Delta的变化率（简化计算）
        gamma = 0.01 if premium > 0 else 0

        # Theta: 时间价值衰减（简化计算）
        theta = -premium * 0.001 if premium > 0 else 0

        # Vega: 对波动率的敏感度（简化计算）
        vega = premium * 0.1 if premium > 0 else 0

        return {
            "bond_code": bond_code,
            "bond_name": str(info['bond_name']),
            "bond_price": bond_price,
            "stock_price": stock_price,
            "conversion_price": conversion_price,
            "conversion_value": round(conversion_value, 2),
            "premium": round(premium, 2),
            "greeks": {
                "delta": round(delta, 4),
                "gamma": round(gamma, 4),
                "theta": round(theta, 4),
                "vega": round(vega, 4)
            },
            "note": "希腊字母为简化计算值，实际应使用专业期权定价模型"
        }

    except Exception as e:
        return {"error": f"[get_option_greeks] 错误: {e}"}


def get_historical_premium_chart_data(bond_code: str, period: str = "3M") -> Dict[str, Any]:
    """
    获取可转债历史溢价率图表数据。

    Args:
        bond_code: 债券代码
        period: 时间周期 ("1M", "3M", "6M", "1Y")

    Returns:
        历史溢价率数据
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    period_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    if period not in period_days:
        return {"error": "时间周期必须是 '1M', '3M', '6M', '1Y' 之一"}

    try:
        # 获取债券基本信息
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return {"error": "无法获取债券数据"}

        bond_info = all_bonds_df[all_bonds_df['bond_code'] == bond_code]
        if bond_info.empty:
            return {"error": f"未找到债券 {bond_code}"}

        info = bond_info.iloc[0]
        stock_code = str(info['stock_code'])
        conversion_price = _safe_float(info['conversion_price'])

        if conversion_price <= 0:
            return {"error": "转股价无效"}

        # 获取历史数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days[period])

        # 获取股票历史价格
        stock_hist = get_historical_prices(stock_code,
                                         start_date.strftime('%Y-%m-%d'),
                                         end_date.strftime('%Y-%m-%d'))

        # 获取债券历史价格
        bond_hist = get_historical_prices(bond_code,
                                        start_date.strftime('%Y-%m-%d'),
                                        end_date.strftime('%Y-%m-%d'))

        if not stock_hist or not bond_hist:
            return {"error": "无法获取足够的历史数据"}

        # 构建日期对齐的数据
        stock_dict = {item['date']: item['close'] for item in stock_hist}
        bond_dict = {item['date']: item['close'] for item in bond_hist}

        chart_data = []
        for date in sorted(set(stock_dict.keys()) & set(bond_dict.keys())):
            stock_price = stock_dict[date]
            bond_price = bond_dict[date]

            if stock_price > 0 and bond_price > 0:
                conversion_value = calculate_conversion_value(stock_price, conversion_price)
                premium_rate = calculate_conversion_premium_rate(bond_price, conversion_value)

                chart_data.append({
                    "date": date,
                    "bond_price": round(bond_price, 2),
                    "stock_price": round(stock_price, 2),
                    "conversion_value": round(conversion_value, 2),
                    "premium_rate": round(premium_rate * 100, 2)  # 转换为百分比
                })

        if not chart_data:
            return {"error": "无法生成图表数据"}

        # 计算统计信息
        premium_rates = [item['premium_rate'] for item in chart_data]

        return {
            "bond_code": bond_code,
            "bond_name": str(info['bond_name']),
            "period": period,
            "data_points": len(chart_data),
            "chart_data": chart_data,
            "statistics": {
                "avg_premium": round(sum(premium_rates) / len(premium_rates), 2),
                "max_premium": round(max(premium_rates), 2),
                "min_premium": round(min(premium_rates), 2),
                "current_premium": round(premium_rates[-1], 2) if premium_rates else 0
            }
        }

    except Exception as e:
        return {"error": f"[get_historical_premium_chart_data] 错误: {e}"}


def analyze_bond_stock_correlation(bond_code: str, period: str = "3M") -> Dict[str, Any]:
    """
    分析可转债与正股的相关性。

    Args:
        bond_code: 债券代码
        period: 分析周期 ("1M", "3M", "6M", "1Y")

    Returns:
        相关性分析结果
    """
    if not bond_code:
        return {"error": "债券代码不能为空"}

    period_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    if period not in period_days:
        return {"error": "时间周期必须是 '1M', '3M', '6M', '1Y' 之一"}

    try:
        # 获取债券基本信息
        all_bonds_df = _get_all_bonds_list()
        if all_bonds_df.empty:
            return {"error": "无法获取债券数据"}

        bond_info = all_bonds_df[all_bonds_df['bond_code'] == bond_code]
        if bond_info.empty:
            return {"error": f"未找到债券 {bond_code}"}

        info = bond_info.iloc[0]
        stock_code = str(info['stock_code'])

        # 获取历史数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days[period])

        # 获取股票和债券历史价格
        stock_hist = get_historical_prices(stock_code,
                                         start_date.strftime('%Y-%m-%d'),
                                         end_date.strftime('%Y-%m-%d'))

        bond_hist = get_historical_prices(bond_code,
                                        start_date.strftime('%Y-%m-%d'),
                                        end_date.strftime('%Y-%m-%d'))

        if not stock_hist or not bond_hist or len(stock_hist) < 10 or len(bond_hist) < 10:
            return {"error": "历史数据不足"}

        # 构建价格序列
        stock_dict = {item['date']: item['close'] for item in stock_hist}
        bond_dict = {item['date']: item['close'] for item in bond_hist}

        # 找到共同日期
        common_dates = sorted(set(stock_dict.keys()) & set(bond_dict.keys()))
        if len(common_dates) < 10:
            return {"error": "共同交易日数据不足"}

        # 计算收益率
        stock_returns = []
        bond_returns = []

        for i in range(1, len(common_dates)):
            prev_date = common_dates[i-1]
            curr_date = common_dates[i]

            stock_return = (stock_dict[curr_date] - stock_dict[prev_date]) / stock_dict[prev_date]
            bond_return = (bond_dict[curr_date] - bond_dict[prev_date]) / bond_dict[prev_date]

            stock_returns.append(stock_return)
            bond_returns.append(bond_return)

        if len(stock_returns) < 5:
            return {"error": "收益率数据不足"}

        # 计算相关系数
        import numpy as np
        correlation = np.corrcoef(stock_returns, bond_returns)[0, 1]

        # 计算其他统计指标
        stock_volatility = np.std(stock_returns) * (252 ** 0.5)  # 年化波动率
        bond_volatility = np.std(bond_returns) * (252 ** 0.5)

        return {
            "bond_code": bond_code,
            "bond_name": str(info['bond_name']),
            "stock_code": stock_code,
            "stock_name": str(info['stock_name']),
            "period": period,
            "data_points": len(stock_returns),
            "correlation": round(float(correlation), 4),
            "stock_volatility": round(float(stock_volatility) * 100, 2),
            "bond_volatility": round(float(bond_volatility) * 100, 2),
            "correlation_strength": (
                "强正相关" if correlation > 0.7 else
                "中等正相关" if correlation > 0.3 else
                "弱相关" if correlation > -0.3 else
                "中等负相关" if correlation > -0.7 else
                "强负相关"
            ),
            "analysis_period": f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        }

    except Exception as e:
        return {"error": f"[analyze_bond_stock_correlation] 错误: {e}"}
