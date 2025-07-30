#!/opt/anaconda3/envs/mcp_env/bin/python
from mcp.server.fastmcp import FastMCP
import requests
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Optional
from enum import IntEnum, StrEnum

# 解析命令行参数
parser = argparse.ArgumentParser(description='广告素材数据查询MCP服务')
parser.add_argument('--token', type=str, required=True, help='API访问token')
args = parser.parse_args()

# 创建MCP服务器
mcp = FastMCP("广告素材数据查询服务")


class AdQualityOption(IntEnum):
    DEFAULT = -1
    HIGH_QUALITY = 1
    LOW_QUALITY = 2


class Whether(StrEnum):
    use = "true"
    not_use = "false"


def get_token_from_config():
    # 只从命令行获取token
    if args.token:
        return args.token
    else:
        raise ValueError("必须提供命令行参数--token")


# 从命令行获取token
@mcp.tool()
def get_ad_material_list(
        version: str = "0.1.86",
        appid: str = "59",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        zhibiao_list: Optional[List[str]] = None,
        media: Optional[List[str]] = None,
        self_cid: Optional[List[str]] = None,
        toushou: Optional[List[str]] = None,
        component_id: Optional[List[str]] = None,
        vp_adgroup_id: Optional[List[str]] = None,
        creative_id: Optional[List[str]] = None,
        group_key: Optional[str] = None,
        producer: Optional[List[str]] = None,
        creative_user: Optional[List[str]] = None,
        vp_originality_id: Optional[List[str]] = None,
        vp_originality_name: Optional[List[str]] = None,
        vp_originality_type: Optional[List[str]] = None,
        is_inefficient_material: AdQualityOption = AdQualityOption.DEFAULT,
        is_ad_low_quality_material: AdQualityOption = AdQualityOption.DEFAULT,
        is_old_table: Whether = Whether.not_use,
        is_deep: Whether = Whether.not_use
) -> dict:
    """
    广告素材数据相关功能。
    version：版本号
    appid：游戏id
    start_time：查询范围开始时间
    end_time：查询范围结束时间
    zhibiao_list：指标
    media：媒体
    self_cid：广告账户id
    toushou：投手
    component_id：组件id
    vp_adgroup_id：计划id
    creative_id：创意id
    group_key：分组
    producer：制作人
    creative_user：创意人
    vp_originality_id：素材id
    vp_originality_name：素材名
    vp_originality_type：素材类型
    is_inefficient_material：低效素材，取值 -1（全选）、1（是）、2（否）
    is_ad_low_quality_material：AD优/低质:取值 -1(全选)、1(低质)、2(优质)
    is_old_table：旧报表:取值true(是)、false(否)，当media中包含["gdt"](广点通)时可选
    is_deep：下探:取值`true`(是)、`false`(否)
    """

    token = get_token_from_config()

    # 设置默认值
    if start_time is None:
        # 默认查询昨天的数据
        yesterday = datetime.now() - timedelta(days=1)
        start_time = yesterday.strftime("%Y-%m-%d")

    if end_time is None:
        # 默认查询到今天
        end_time = datetime.now().strftime("%Y-%m-%d")
    if zhibiao_list is None:
        zhibiao_list = ["日期", "素材id", "素材名称", "素材类型", "素材封面uri", "制作人", "创意人", "素材创造时间",
                        "3秒播放率", "完播率", "是否低效素材", "是否AD低质素材", "是否AD优质素材", "低质原因",
                        "新增注册", "新增创角", "创角率", "点击率", "激活率", "点击成本", "活跃用户", "当日充值",
                        "当日付费次数", "当日充值人数", "新增付费人数", "首充付费人数", "新增付费金额", "首充付费金额",
                        "新增付费率", "活跃付费率", "活跃arppu", "新增arppu", "小游戏注册首日广告变现金额",
                        "小游戏注册首日广告变现ROI", "新增付费成本", "消耗", "付费成本", "注册成本", "创角成本",
                        "首日ROI", "累计ROI", "分成后首日ROI", "分成后累计ROI"]

    # API接口地址
    url = "https://bi.dartou.com/testapi/ad/GetMaterialCountList"

    # 设置请求头
    headers = {
        "X-Token": token,
        "X-Ver": version,
        "Content-Type": "application/json"
    }

    # 构建请求体
    payload = {
        "appid": appid,
        "start_time": start_time,
        "end_time": end_time,
        "zhibiao_list": zhibiao_list,
        "media": media,
        "self_cid": self_cid,
        "toushou": toushou,
        "component_id": component_id,
        "vp_adgroup_id": vp_adgroup_id,
        "creative_id": creative_id,
        "group_key": group_key,
        "producer": producer,
        "creative_user": creative_user,
        "vp_originality_id": vp_originality_id,
        "vp_originality_name": vp_originality_name,
        "vp_originality_type": vp_originality_type,
        "is_ad_low_quality_material": is_ad_low_quality_material.value,
        "is_inefficient_material": is_inefficient_material.value,
        "is_old_table": is_old_table.value,
        "is_deep": is_deep.value
    }

    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # 解析响应
        result = response.json()

        # 检查响应状态
        if result.get("code") == 0:
            print("请求成功!")
            return result
        else:
            print(f"请求失败: {result.get('msg')}")
            return result

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return {"code": -1, "msg": str(e)}


def main() -> None:
    mcp.run(transport="stdio")
