"""
MCP Server for convertible bond analysis.

This module creates and configures the Model Context Protocol server
using FastMCP framework to expose bond analysis tools.
"""

import argparse
import logging
import sys
from typing import Any, Dict, List

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # Fallback for basic MCP server
    from mcp.server import Server as FastMCP

from .tools import (
    # 第一类：基础数据获取工具
    get_all_convertible_bonds,
    get_realtime_quotes,
    get_bond_static_info,
    get_stock_financials,
    get_historical_prices,
    get_company_announcements,

    # 第二类：核心指标计算工具
    calculate_conversion_value,
    calculate_conversion_premium_rate,
    calculate_pure_bond_value,
    calculate_ytm,

    # 第三类：条款状态与博弈分析工具
    check_clause_trigger_status,
    get_major_bondholders_info,

    # 第四类：筛选与监控工具
    screen_bonds_by_premium,
    screen_bonds_by_price_and_ytm,
    screen_for_clause_plays,

    # 第五类：深度分析与辅助决策工具
    calculate_implied_volatility,
    get_option_greeks,
    get_historical_premium_chart_data,
    analyze_bond_stock_correlation,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_server() -> FastMCP:
    """
    Create and configure the MCP server with all bond analysis tools.
    
    Returns:
        FastMCP: Configured server instance
    """
    # Create MCP server instance
    mcp = FastMCP(
        name="BigAMCP Bond Analysis Server",
        description="A comprehensive MCP server for convertible bond analysis using akshare data",
        version="0.1.0"
    )
    
    # ========================================================================
    # 第一类：基础数据获取工具 (Data Acquisition Tools)
    # ========================================================================

    @mcp.tool()
    def get_all_bonds() -> List[Dict[str, Any]]:
        """获取所有活跃可转债的代码和名称"""
        return get_all_convertible_bonds()

    @mcp.tool()
    def get_quotes(codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """获取指定债券和股票的实时报价"""
        return get_realtime_quotes(codes)

    @mcp.tool()
    def get_bond_info(bond_code: str) -> Dict[str, Any]:
        """获取指定可转债的详细静态信息"""
        return get_bond_static_info(bond_code)

    @mcp.tool()
    def get_financials(stock_code: str) -> Dict[str, Any]:
        """获取正股的关键财务数据"""
        return get_stock_financials(stock_code)

    @mcp.tool()
    def get_history(code: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """获取指定代码的历史价格数据"""
        return get_historical_prices(code, start_date, end_date)

    @mcp.tool()
    def get_announcements(stock_code: str, count: int = 10) -> List[Dict[str, Any]]:
        """获取公司最新公告信息"""
        return get_company_announcements(stock_code, count)

    # ========================================================================
    # 第二类：核心指标计算工具 (Indicator Calculation Tools)
    # ========================================================================

    @mcp.tool()
    def calc_conversion_value(stock_price: float, conversion_price: float) -> float:
        """计算转股价值"""
        return calculate_conversion_value(stock_price, conversion_price)

    @mcp.tool()
    def calc_premium_rate(bond_price: float, conversion_value: float) -> float:
        """计算转股溢价率"""
        return calculate_conversion_premium_rate(bond_price, conversion_value)

    @mcp.tool()
    def calc_pure_bond_value(bond_code: str) -> Dict[str, Any]:
        """计算纯债价值（债底）"""
        return calculate_pure_bond_value(bond_code)

    @mcp.tool()
    def calc_ytm(bond_code: str, bond_price: float) -> Dict[str, Any]:
        """计算到期收益率"""
        return calculate_ytm(bond_code, bond_price)

    # ========================================================================
    # 第三类：条款状态与博弈分析工具 (Clause Analysis Tools)
    # ========================================================================

    @mcp.tool()
    def check_clause_status(bond_code: str) -> Dict[str, Any]:
        """检查可转债条款触发状态"""
        return check_clause_trigger_status(bond_code)

    @mcp.tool()
    def get_bondholders(bond_code: str) -> Dict[str, Any]:
        """获取可转债主要持有人信息"""
        return get_major_bondholders_info(bond_code)

    # ========================================================================
    # 第四类：筛选与监控工具 (Screening & Monitoring Tools)
    # ========================================================================

    @mcp.tool()
    def screen_by_premium(min_premium: float, max_premium: float) -> List[Dict[str, Any]]:
        """按溢价率范围筛选可转债"""
        return screen_bonds_by_premium(min_premium, max_premium)

    @mcp.tool()
    def screen_by_price_ytm(max_price: float, min_ytm: float) -> List[Dict[str, Any]]:
        """按价格和到期收益率筛选可转债"""
        return screen_bonds_by_price_and_ytm(max_price, min_ytm)

    @mcp.tool()
    def screen_clause_plays(play_type: str) -> List[Dict[str, Any]]:
        """筛选特定条款博弈机会"""
        return screen_for_clause_plays(play_type)

    # ========================================================================
    # 第五类：深度分析与辅助决策工具 (Deep Analysis & Auxiliary Decision Tools)
    # ========================================================================

    @mcp.tool()
    def calc_implied_vol(bond_code: str) -> Dict[str, Any]:
        """计算可转债的隐含波动率"""
        return calculate_implied_volatility(bond_code)

    @mcp.tool()
    def get_greeks(bond_code: str) -> Dict[str, Any]:
        """计算可转债的期权希腊字母"""
        return get_option_greeks(bond_code)

    @mcp.tool()
    def get_premium_chart(bond_code: str, period: str = "3M") -> Dict[str, Any]:
        """获取可转债历史溢价率图表数据"""
        return get_historical_premium_chart_data(bond_code, period)

    @mcp.tool()
    def analyze_correlation(bond_code: str, period: str = "3M") -> Dict[str, Any]:
        """分析可转债与正股的相关性"""
        return analyze_bond_stock_correlation(bond_code, period)
    
    return mcp


def main():
    """
    Main entry point for the MCP server.
    """
    parser = argparse.ArgumentParser(description="BigAMCP Bond Analysis MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport method for MCP communication"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for SSE transport (default: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)"
    )
    
    args = parser.parse_args()
    
    # Create and configure the server
    server = create_server()
    
    try:
        if args.transport == "stdio":
            logger.info("Starting MCP server with stdio transport")
            server.run(transport="stdio")
        elif args.transport == "sse":
            logger.info(f"Starting MCP server with SSE transport on {args.host}:{args.port}")
            server.run(transport="sse", host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
