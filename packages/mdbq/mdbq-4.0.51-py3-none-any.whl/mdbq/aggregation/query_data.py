# -*- coding: UTF-8 –*-
import re
from mdbq.mysql import uploader
from mdbq.mysql import s_query
from mdbq.myconf import myconf
from mdbq.log import mylogger
from mdbq.other import error_handler
from mdbq.aggregation.set_typ_dict import SET_TYP_DICT
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
from functools import wraps
import platform
import os
import time
import calendar
from collections.abc import Mapping, Sequence
import inspect

dir_path = os.path.expanduser("~")
parser = myconf.ConfigParser()
host, port, username, password = parser.get_section_values(
    file_path=os.path.join(dir_path, 'spd.txt'),
    section='mysql',
    keys=['host', 'port', 'username', 'password'],
)
# host = 'localhost'
uld = uploader.MySQLUploader(username=username, password=password, host=host, port=int(port), pool_size=10)

logger = mylogger.MyLogger(
    logging_mode='file',
    log_level='info',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,  # 是否启用异步日志
    sample_rate=1,  # 采样DEBUG/INFO日志
    sensitive_fields=[],  #  敏感字段过滤
    enable_metrics=False,  # 是否启用性能指标
)


def reorder_columns(df: pd.DataFrame, set_type) -> pd.DataFrame:
    """
    调整DataFrame的列顺序，按照set_type中的顺序排列，忽略大小写，set_type中不存在的列自动跳过。
    set_type可以是列表或字典（此时用字典的键名作为顺序）。
    不改变数据和数据类型。
    如果 set_type 为 None、空列表或空字典，则直接返回原 df，不做任何调整。
    """
    # 直接返回原 df 的情况
    if set_type is None:
        return df
    if isinstance(set_type, Mapping) and len(set_type) == 0:
        return df
    if isinstance(set_type, Sequence) and not isinstance(set_type, str) and len(set_type) == 0:
        return df

    # 如果set_type是字典，提取其键名
    if isinstance(set_type, Mapping):
        col_order = list(set_type.keys())
    elif isinstance(set_type, Sequence) and not isinstance(set_type, str):
        col_order = list(set_type)
    else:
        raise ValueError("set_type must be a list or a dict (or other mapping type)")

    # 构建原始列名的映射（小写->原始名）
    col_map = {col.lower(): col for col in df.columns}
    # 生成新顺序的列名（只保留df中存在的列，且顺序按set_type）
    new_cols = []
    used = set()
    for col in col_order:
        key = col.lower()
        if key in col_map and key not in used:
            new_cols.append(col_map[key])
            used.add(key)
    # 添加剩余未在set_type中出现的列，保持原顺序
    for col in df.columns:
        if col.lower() not in used:
            new_cols.append(col)
    # 返回新顺序的DataFrame
    return df[new_cols]


def upload_data_decorator(**upload_kwargs):
    """
    数据上传装饰器
    :param upload_kwargs: 上传参数，支持所有 upload_data 方法的参数
    :return: 装饰器函数
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            db_name = None
            table_name = None
            try:
                # 获取函数签名和参数
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                args_dict = bound_args.arguments

                # 获取所需参数
                def get_param_value(param_name, alternatives=None):
                    if alternatives is None:
                        alternatives = [param_name]
                    # 从 kwargs 或 args_dict 中获取参数值
                    for key in alternatives:
                        if key in kwargs:
                            return kwargs[key]
                        if key in args_dict:
                            return args_dict[key]
                    return None

                # 获取参数值
                set_type = get_param_value('set_type', ['set_type', 'set_typ'])
                db_name = get_param_value('db_name')
                table_name = get_param_value('table_name')
                # 参数摘要处理
                def summarize_value(val):
                    if isinstance(val, pd.DataFrame):
                        return f"DataFrame(shape={val.shape}, columns={list(val.columns)})"
                    elif isinstance(val, np.ndarray):
                        return f"ndarray(shape={val.shape}, dtype={val.dtype})"
                    elif isinstance(val, (list, tuple)):
                        return [summarize_value(v) for v in val]
                    elif isinstance(val, dict):
                        return {k: summarize_value(v) for k, v in val.items()}
                    elif hasattr(val, '__class__') and not isinstance(val, (str, int, float, bool, type(None))):
                        return f"{val.__class__.__name__}"
                    else:
                        return val
                args_summary = {k: summarize_value(v) for k, v in args_dict.items()}
                logger.info('更新', {'库': db_name, '表': table_name, 'func': func.__name__, 'args': args_summary, 'kwargs': kwargs})

                # 执行原始函数
                result = func(*args, **kwargs)
                
                if result is None:
                    logger.info('函数返回None，直接返回原结果，不执行上传', {'库': db_name, '表': table_name, 'func': func.__name__})
                    return None

                # 处理 DataFrame 结果
                if isinstance(result, (pd.DataFrame, list, dict)):
                    if set_type is not None:
                        if isinstance(result, pd.DataFrame):
                                result = reorder_columns(result, set_type)
                        elif isinstance(result, list):
                            # 如果是list，转换为DataFrame以调整列顺序
                            result = reorder_columns(pd.DataFrame(result), set_type)
                        elif isinstance(result, dict):
                            # 如果是dict，转换为DataFrame以调整列顺序
                            result = reorder_columns(pd.DataFrame([result]), set_type)
                    
                    # 合并参数
                    merged_kwargs = {
                        'check_duplicate': False,
                        'update_on_duplicate': True,
                        'allow_null': False,
                        'transaction_mode': 'batch',
                        **upload_kwargs
                    }
                    
                    uld.upload_data(data=result, **merged_kwargs)
                    logger.info('上传完成', {'库': db_name, '表': table_name, 'func': func.__name__})
                    return True

                # 处理元组结果
                elif isinstance(result, tuple):
                    if len(result) < 2:
                        logger.warning('函数返回的元组长度小于2，直接返回原结果，不执行上传', {'库': db_name, '表': table_name, 'func': func.__name__})
                        return result

                    df, extra_kwargs = result[0], result[1]
                    
                    if not isinstance(df, (pd.DataFrame, list, dict)):
                        logger.warning('函数返回的元组第一个元素不是DataFrame/list/dict，直接返回原结果，不执行上传', {'库': db_name, '表': table_name, 'func': func.__name__})
                        return result

                    if set_type is not None:
                        if isinstance(df, pd.DataFrame):
                                df = reorder_columns(df, set_type)
                        elif isinstance(df, list):
                            # 如果是list，转换为DataFrame以调整列顺序
                            df = reorder_columns(pd.DataFrame(df), set_type)
                        elif isinstance(df, dict):
                            # 如果是dict，转换为DataFrame以调整列顺序
                            df = reorder_columns(pd.DataFrame([df]), set_type)
                        result = (df, extra_kwargs) + result[2:]

                    # 合并参数
                    merged_kwargs = {
                        'check_duplicate': False,
                        'update_on_duplicate': True,
                        'allow_null': False,
                        'transaction_mode': 'batch',
                        **upload_kwargs,
                        **extra_kwargs
                    }
                    
                    uld.upload_data(data=df, **merged_kwargs)
                    logger.info('上传完成', {'库': db_name, '表': table_name, 'func': func.__name__})
                    return result if len(result) > 2 else True
                logger.info('上传完成', {'库': db_name, '表': table_name, 'func': func.__name__})
                return result

            except Exception as e:
                logger.error('数据上传失败', {'库': db_name, '表': table_name, 'func': func.__name__, '错误': str(e)})
                return False

        return wrapper
    return decorator


class MysqlDatasQuery:
    """
    从数据库中下载数据
    """
    def __init__(self, download_manager):
        self.months = 0  # 下载几个月数据, 0 表示当月, 1 是上月 1 号至今
        self.download_manager = download_manager
        self.pf_datas = []

    @upload_data_decorator()
    def shops_concat(self, db_name='聚合数据', table_name='多店聚合_日报'):
        shop_list = {
            'DS-WLM天猫旗舰店': '天猫',  # e3
            'DS-WLM淘宝商城C店': 'c店', 
            'DS-SJ天猫旗舰店': '圣积', 
            'wanlima万里马箱包outlet店': '奥莱', 
            'DS-WLM京东旗舰店': '京东pop', 
            '拼多多万里马箱包官方旗舰店': '拼多多_丹宁', 
            'WLM-拼多多TOGO牛皮官方旗舰店': '拼多多_togo', 
            '万里马官方旗舰店': '天猫',  # 平台
            '万里马官方企业店': 'c店',
            'saintjack旗舰店': '圣积',
            'wanlima万里马箱包outlet店': '奥莱',
            '万里马京东旗舰店': '京东pop',
            '万里马箱包官方旗舰店': '拼多多_丹宁',
            '万里马箱包皮具官方旗舰店': '拼多多_togo',
            '万里马箱包outlet店': '奥莱',  # 推广
            '京东箱包旗舰店': '京东pop',
            '京东自营旗舰店女包': '京东自营',
        }
        df_real_sales = self._get_real_sales(shop_list=shop_list)
        df_shop_gmv = self._get_shop_gmv(shop_list=shop_list)
        df_tg_data = self._get_tg_data(shop_list=shop_list)
        df = df_shop_gmv.merge(df_real_sales, on=['日期', '店铺名称'], how='outer')  # 平台数据合并销售数据
        df = df.merge(df_tg_data, on=['日期', '店铺名称'], how='outer')  # 合并推广数据
        df.fillna(0, inplace=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称']],  # 唯一约束列表
        }
    
    def _get_tg_data(self, db_name='聚合数据', table_name='多店推广场景_按日聚合', shop_list:dict=None):
        start_date, end_date = self.months_data(num=self.months)
        projection = ['日期', '店铺名称', '营销场景', '花费']
        df = self.download_manager.data_to_df(
            db_name=db_name,
            table_name=table_name,
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        if df.empty:
            return pd.DataFrame(columns=['日期', '店铺名称', '实际消耗'])
        df = df[(df['店铺名称'].isin(shop_list.keys()))]
        df = df.astype({
            '日期': 'datetime64[ns]',
            '花费': 'float64',
        })
        df = df.groupby(['日期', '店铺名称'], as_index=False).agg({'花费': 'sum'}).rename(columns={'花费': '实际消耗'})
        df['店铺名称'] = df['店铺名称'].map(shop_list)
        return df

    def _get_shop_gmv(self, db_name='生意参谋3', table_name='取数_店铺_整体流量', shop_list:dict=None):
        """获取平台数据"""
        start_date, end_date = self.months_data(num=self.months)
        projection = ['日期', '店铺名称', '粒度', '维度', '数据周期', '访客数', '浏览量', '支付金额', '支付买家数', '支付件数']
        df = self.download_manager.data_to_df(
            db_name=db_name,
            table_name=table_name,
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        if len(df) == 0:
            return pd.DataFrame(columns=['日期', '店铺名称', '访客数', '浏览量', '支付金额', '支付买家数', '支付件数'])
        df = df[(df['店铺名称'].isin(shop_list.keys())) & (df['粒度'] == '店铺') & (df['维度'] == '整体流量') & (df['数据周期'] == '分日')]
        df = df.astype({
            '日期': 'datetime64[ns]',
            '访客数': 'int64',
            '浏览量': 'int64',
            '支付金额': 'float64',
            '支付买家数': 'int64',
            '支付件数': 'int64'
        })
        df = df.groupby(['日期', '店铺名称'], as_index=False).agg({
            '访客数': 'sum',
            '浏览量': 'sum',
            '支付金额': 'sum',
            '支付买家数': 'sum',
            '支付件数': 'sum'
        })
        df['店铺名称'] = df['店铺名称'].map(shop_list)
        return df

    def _get_real_sales(self, db_name='生意经3', table_name='零售明细统计', shop_list:dict=None):
        """获取e3销售"""
        start_date, end_date = self.months_data(num=self.months)
        projection = ['验收日期', '商店名称', '商品代码', '金额']
        __res = []
        for year in range(2025, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name=db_name,
                table_name=f'{table_name}_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df_default = pd.DataFrame(columns=['日期', '店铺名称', '实际营收'])
        if len(__res) == 0:
            return df_default
        df = pd.concat(__res, ignore_index=True)
        if df.empty:
            return df_default
        df = df[(df['商品代码'] != '20160222') & (df['商店名称'].isin(shop_list.keys()))]  # 剔除补单数据
        if df.empty:
            return df_default
        df['商店名称'] = df['商店名称'].map(shop_list)
        df = df.astype({
            '验收日期': 'datetime64[ns]', '金额': 'float64'
            }).groupby(
                ['验收日期', '商店名称'], as_index=False
                ).agg({
                    '金额': 'sum'
                    }).rename(
                        columns={'商店名称': '店铺名称', '验收日期': '日期', '金额': '实际营收'}
                        )
        df_ziying_sales = self._get_ziying_sales(shop_list=shop_list)
        df = pd.concat([df, df_ziying_sales], ignore_index=True)  # e3 合并京东自营业绩
        return df

    def _get_ziying_sales(self, db_name='京东数据3', table_name='京东自营_vc品牌业绩', shop_list:dict=None):
        """获取京东自营业绩"""
        start_date, end_date = self.months_data(num=self.months)
        projection = ['日期', '店铺名称', '收入']
        df = self.download_manager.data_to_df(
            db_name=db_name,
            table_name=table_name,
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        if df.empty:
            return pd.DataFrame(columns=['日期', '店铺名称', '收入'])
        df = df[(df['店铺名称'].isin(shop_list.keys()))]
        df = df.astype({
            '日期': 'datetime64[ns]',
            '收入': 'float64'
        })
        df = df.groupby(['日期', '店铺名称'], as_index=False).agg({'收入': 'sum'}).rename(columns={'收入': '实际营收'})
        df['店铺名称'] = df['店铺名称'].map(shop_list)
        return df

    
    # @error_handler.log_on_exception(logger=logger)
    def tg_wxt(self, db_name='聚合数据', table_name='天猫_主体报表', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景名字': 1,
            '主体id': 1,
            '花费': 1,
            '展现量': 1,
            '点击量': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '自然流量曝光量': 1,
            '直接成交笔数': 1,
            '直接成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'主体报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df.rename(columns={
            '场景名字': '营销场景',
            '主体id': '商品id',
            '总购物车数': '加购量',
            '总成交笔数': '成交笔数',
            '总成交金额': '成交金额'
        }, inplace=True)
        df = df.astype({
            '商品id': str,
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '自然流量曝光量': 'int64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
        }, errors='raise')
        df = df[df['花费'] > 0]
        if is_maximize:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '加购量': ('加购量', np.max),
                   '成交笔数': ('成交笔数', np.max),
                   '成交金额': ('成交金额', np.max),
                   '自然流量曝光量': ('自然流量曝光量', np.max),
                   '直接成交笔数': ('直接成交笔数', np.max),
                   '直接成交金额': ('直接成交金额', np.max)
                   }
            )
        else:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '自然流量曝光量': ('自然流量曝光量', np.min),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        df.insert(loc=1, column='推广渠道', value='万相台无界版')
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        # 制作其他聚合表
        self.pf_datas.append(
            {
                '集合名称': '天猫汇总表调用',
                '数据主体': df[
                    ['日期', '店铺名称', '推广渠道', '营销场景', '商品id', '花费', '展现量', '点击量', '加购量',
                     '成交笔数', '成交金额', '直接成交笔数', '直接成交金额', '自然流量曝光量']]
            }
        )
        logger.info('更新', {'主机': f'{host}:{port}', '库': db_name, '表': table_name})
        
        uld.upload_data(
            db_name=db_name,
            table_name=table_name,
            data=df,
            set_typ=set_typ,  # 定义列和数据类型
            primary_keys=[],  # 创建唯一主键
            check_duplicate=False,  # 检查重复数据
            duplicate_columns=[],  # 指定排重的组合键
            update_on_duplicate=True,  # 更新旧数据
            allow_null=False,  # 允许插入空值
            partition_by=None,  # 分表方式
            partition_date_column='日期',  # 用于分表的日期列名，默认为'日期'
            indexes=[],  # 普通索引列
            transaction_mode='batch',  # 事务模式
            unique_keys=[['日期', '推广渠道', '店铺名称', '营销场景', '商品id', '花费', '展现量', '点击量', '自然流量曝光量']],  # 唯一约束列表
        )

        # df_pic：商品排序索引表, 给 powerbi 中的主推款排序用的,(从上月1号到今天的总花费进行排序)
        today = datetime.date.today()
        last_month = today - datetime.timedelta(days=30)
        if last_month.month == 12:
            year_my = today.year - 1
        else:
            year_my = today.year
        # 截取 从上月1日 至 今天的花费数据, 推广款式按此数据从高到低排序（商品图+排序）
        # df_pic_lin = df[df['店铺名称'] == '万里马官方旗舰店']
        df_pic = df.groupby(['日期', '店铺名称', '商品id'], as_index=False).agg({'花费': 'sum'})
        if len(df_pic) == 0:
            return True
        df_pic = df_pic[~df_pic['商品id'].isin([''])]  # 指定列中删除包含空值的行
        date_obj = datetime.datetime.strptime(f'{year_my}-{last_month.month}-01', '%Y-%m-%d').date()
        df_pic = df_pic[(df_pic['日期'] >= date_obj)]
        df_pic = df_pic.groupby(['店铺名称', '商品id'], as_index=False).agg({'花费': 'sum'})
        df_pic.sort_values('花费', ascending=False, ignore_index=True, inplace=True)
        df_pic.reset_index(inplace=True)
        df_pic['index'] = df_pic['index'] + 100
        df_pic.rename(columns={'index': '商品索引'}, inplace=True)
        df_pic['商品索引'].fillna(1000, inplace=True)
        df_pic.pop('花费')
        p= df_pic.pop('商品索引')
        df_pic.insert(loc=2, column='商品索引', value=p)  # df中插入新列
        df_pic['更新时间'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        set_typ = SET_TYP_DICT['属性设置3_商品索引表_主推排序调用']
        logger.info('更新', {'主机': f'{host}:{port}', '库': '属性设置3', '表': '商品索引表_主推排序调用'})
        uld.upload_data(
            db_name='属性设置3',
            table_name='商品索引表_主推排序调用',
            data=df_pic,
            set_typ=set_typ,  # 定义列和数据类型
            primary_keys=[],  # 创建唯一主键
            check_duplicate=False,  # 检查重复数据
            duplicate_columns=[],  # 指定排重的组合键
            update_on_duplicate=True,  # 更新旧数据
            allow_null=False,  # 允许插入空值
            partition_by=None,  # 分表方式
            partition_date_column='日期',  # 用于分表的日期列名，默认为'日期'
            indexes=[],  # 普通索引列
            transaction_mode='batch',  # 事务模式
            unique_keys=[['商品id']],  # 唯一约束列表
        )
        return True

    @upload_data_decorator()
    def _tb_wxt(self, db_name='聚合数据', table_name='淘宝_主体报表', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景名字': 1,
            '主体id': 1,
            '花费': 1,
            '展现量': 1,
            '点击量': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '自然流量曝光量': 1,
            '直接成交笔数': 1,
            '直接成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name='推广数据_淘宝店',
                table_name=f'主体报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df.rename(columns={
            '场景名字': '营销场景',
            '主体id': '商品id',
            '总购物车数': '加购量',
            '总成交笔数': '成交笔数',
            '总成交金额': '成交金额'
        }, inplace=True)
        df = df.astype({
            '商品id': str,
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '自然流量曝光量': 'int64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
        }, errors='raise')
        df = df[df['花费'] > 0]
        if is_maximize:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '加购量': ('加购量', np.max),
                   '成交笔数': ('成交笔数', np.max),
                   '成交金额': ('成交金额', np.max),
                   '自然流量曝光量': ('自然流量曝光量', np.max),
                   '直接成交笔数': ('直接成交笔数', np.max),
                   '直接成交金额': ('直接成交金额', np.max)
                   }
            )
        else:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '自然流量曝光量': ('自然流量曝光量', np.min),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        df.insert(loc=1, column='推广渠道', value='万相台无界版')  # df中插入新列
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '推广渠道', '店铺名称', '营销场景', '商品id', '花费', '展现量', '点击量', '自然流量曝光量']],  # 唯一约束列表
        }

    @upload_data_decorator()
    def _ald_wxt(self, db_name='聚合数据', table_name='奥莱店_主体报表', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景名字': 1,
            '主体id': 1,
            '花费': 1,
            '展现量': 1,
            '点击量': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '自然流量曝光量': 1,
            '直接成交笔数': 1,
            '直接成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name='推广数据_奥莱店',
                table_name=f'主体报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df.rename(columns={
            '场景名字': '营销场景',
            '主体id': '商品id',
            '总购物车数': '加购量',
            '总成交笔数': '成交笔数',
            '总成交金额': '成交金额'
        }, inplace=True)
        df = df.astype({
            '商品id': str,
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '自然流量曝光量': 'int64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
        }, errors='raise')
        df = df[df['花费'] > 0]
        if is_maximize:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '加购量': ('加购量', np.max),
                   '成交笔数': ('成交笔数', np.max),
                   '成交金额': ('成交金额', np.max),
                   '自然流量曝光量': ('自然流量曝光量', np.max),
                   '直接成交笔数': ('直接成交笔数', np.max),
                   '直接成交金额': ('直接成交金额', np.max)
                   }
            )
        else:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '自然流量曝光量': ('自然流量曝光量', np.min),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        df.insert(loc=1, column='推广渠道', value='万相台无界版')  # df中插入新列
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '推广渠道', '店铺名称', '营销场景', '商品id', '花费', '展现量', '点击量', '自然流量曝光量']],  # 唯一约束列表
        }

    @upload_data_decorator()
    def _sj_wxt(self, db_name='聚合数据', table_name='圣积天猫店_主体报表', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景名字': 1,
            '主体id': 1,
            '花费': 1,
            '展现量': 1,
            '点击量': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '自然流量曝光量': 1,
            '直接成交笔数': 1,
            '直接成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2025, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name='推广数据_圣积天猫店',
                table_name=f'主体报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df.rename(columns={
            '场景名字': '营销场景',
            '主体id': '商品id',
            '总购物车数': '加购量',
            '总成交笔数': '成交笔数',
            '总成交金额': '成交金额'
        }, inplace=True)
        df = df.astype({
            '商品id': str,
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '自然流量曝光量': 'int64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
        }, errors='raise')
        df = df[df['花费'] > 0]
        if is_maximize:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '加购量': ('加购量', np.max),
                   '成交笔数': ('成交笔数', np.max),
                   '成交金额': ('成交金额', np.max),
                   '自然流量曝光量': ('自然流量曝光量', np.max),
                   '直接成交笔数': ('直接成交笔数', np.max),
                   '直接成交金额': ('直接成交金额', np.max)
                   }
            )
        else:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '自然流量曝光量': ('自然流量曝光量', np.min),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        df.insert(loc=1, column='推广渠道', value='万相台无界版')  # df中插入新列
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '推广渠道', '店铺名称', '营销场景', '商品id', '花费', '展现量', '点击量', '自然流量曝光量']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def syj(self, db_name='聚合数据', table_name='生意经_宝贝指标'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '宝贝id': 1,
            '商家编码': 1,
            '行业类目': 1,
            '销售额': 1,
            '销售量': 1,
            '订单数': 1,
            '退货量': 1,
            '退款额': 1,
            '退款额_发货后': 1,
            '退货量_发货后': 1,
            '店铺名称': 1,
            '更新时间': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='生意经3',
                table_name=f'宝贝指标_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df['宝贝id'] = df['宝贝id'].astype(str)
        # 仅保留最新日期的数据
        idx = df.groupby(['日期', '店铺名称', '宝贝id'])['更新时间'].idxmax()
        df = df.loc[idx]
        df = df[['日期', '店铺名称', '宝贝id', '行业类目', '销售额', '销售量', '订单数', '退货量', '退款额', '退款额_发货后', '退货量_发货后']]
        df['件均价'] = np.where(df['销售量'] > 0, df['销售额'] / df['销售量'], 0).round(0)
        df['价格带'] = df['件均价'].apply(
            lambda x: '2000+' if x >= 2000
            else '1000+' if x >= 1000
            else '500+' if x >= 500
            else '300+' if x >= 300
            else '300以下'
        )
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '宝贝id']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def tg_rqbb(self, db_name='聚合数据', table_name='天猫_人群报表', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景名字': 1,
            '主体id': 1,
            '花费': 1,
            '展现量': 1,
            '点击量': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '直接成交笔数': 1,
            '直接成交金额': 1,
            '人群名字': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'人群报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df.rename(columns={
            '场景名字': '营销场景',
            '主体id': '商品id',
            '总购物车数': '加购量',
            '总成交笔数': '成交笔数',
            '总成交金额': '成交金额'
        }, inplace=True)
        df.fillna(0, inplace=True)
        df = df.astype({
            '商品id': str,
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'int64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
        }, errors='raise')
        if is_maximize:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量', '人群名字'],
                            as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '加购量': ('加购量', np.max),
                    '成交笔数': ('成交笔数', np.max),
                    '成交金额': ('成交金额', np.max),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        else:
            df = df.groupby(['日期', '店铺名称', '营销场景', '商品id', '花费', '点击量', '人群名字'],
                            as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        df.insert(loc=1, column='推广渠道', value='万相台无界版')
        # 开始处理用户特征
        df_sx = self.download_manager.data_to_df(
            db_name='达摩盘3',
            table_name=f'我的人群属性',
            start_date=start_date,
            end_date=end_date,
            projection={'人群名称': 1, '消费能力等级': 1, '用户年龄': 1},
        )
        df_sx['人群名称'] = '达摩盘：' + df_sx['人群名称']
        df_sx.rename(columns={'消费能力等级': '消费力层级'}, inplace=True)
        df = pd.merge(df, df_sx, left_on=['人群名字'], right_on=['人群名称'], how='left')
        df.pop('人群名称')
        df['消费力层级'] = df['消费力层级'].apply(
            lambda x: f'L{"".join(re.findall(r'L(\d)', str(x)))}' if str(x) != 'nan'  else x)
        df['用户年龄'] = df['用户年龄'].apply(
            lambda x: "~".join(re.findall(r'(\d{2})\D.*(\d{2})岁', str(x))[0])
            if str(x) != 'nan' and re.findall(r'(\d{2})\D.*(\d{2})岁', str(x)) else x)
        # 1. 匹配 L后面接 2 个或以上数字，不区分大小写，示例：L345
        # 2. 其余情况，L 后面接多个数字的都会被第一条 if 命中，不区分大小写
        df['消费力层级'] = df.apply(
            lambda x:
            ''.join(re.findall(r'(l\d+)', x['人群名字'].upper(), re.IGNORECASE))
            if re.findall(r'(l\d{2,})', x['人群名字'], re.IGNORECASE) and str(x['消费力层级']) == 'nan'
            else 'L5' if re.findall(r'(l\d*5)', x['人群名字'], re.IGNORECASE) and str(x['消费力层级']) == 'nan'
            else 'L4' if re.findall(r'(l\d*4)', x['人群名字'], re.IGNORECASE) and str(x['消费力层级']) == 'nan'
            else 'L3' if re.findall(r'(l\d*3)', x['人群名字'], re.IGNORECASE) and str(x['消费力层级']) == 'nan'
            else 'L2' if re.findall(r'(l\d*2)', x['人群名字'], re.IGNORECASE) and str(x['消费力层级']) == 'nan'
            else 'L1' if re.findall(r'(l\d*1)', x['人群名字'], re.IGNORECASE) and str(x['消费力层级']) == 'nan'
            else x['消费力层级'], axis=1)
        # 1. 匹配连续的 4 个数字且后面不能接数字或"元"或汉字，筛掉的人群示例：月均消费6000元｜受众20240729175213｜xxx2024真皮公文包
        # 2. 匹配 2数字_2数字且前面不能是数字，合法匹配：人群_30_50_促； 非法示例：L345_3040 避免识别出 35～20 岁用户的情况
        # pattern = r'(\d{4})(?!\d|[\u4e00-\u9fa5])'  # 匹配 4 个数字，后面不能接数字或汉字
        # pattern = r'(?<![\d\u4e00-\u9fa5])(\d{4})' # 匹配前面不是数字或汉字的 4 个连续数字
        # 匹配 4 个数字，前面和后面都不能是数字或汉字
        pattern1 = r'(?<![\d\u4e00-\u9fa5])(\d{4})(?!\d|[\u4e00-\u9fa5])'
        # 匹配指定字符，前面不能是数字或 l 或 L 开头
        pattern2 = r'(?<![\dlL])(\d{2}_\d{2})'
        df['用户年龄'] = df.apply(
            lambda x:
            ''.join(re.findall(pattern1, x['人群名字'].upper()))
            if re.findall(pattern1, x['人群名字']) and str(x['用户年龄']) == 'nan'
            else ''.join(re.findall(pattern2, x['人群名字'].upper()))
            if re.findall(pattern2, x['人群名字']) and str(x['用户年龄']) == 'nan'
            else ''.join(re.findall(r'(\d{2}-\d{2})岁', x['人群名字'].upper()))
            if re.findall(r'(\d{2}-\d{2})岁', x['人群名字']) and str(x['用户年龄']) == 'nan'
            else x['用户年龄'], axis=1)
        df['用户年龄'] = df['用户年龄'].apply(
            lambda x: f'{x[:2]}~{x[2:4]}' if str(x).isdigit()
            else str(x).replace('_', '~') if '_' in str(x)
            else str(x).replace('-', '~') if '-' in str(x)
            else x
        )
        # 年龄层不能是 0 开头
        df['用户年龄'] = np.where(df['用户年龄'].astype(str).str.startswith('0'), '', df['用户年龄'])
        df['用户年龄'] = df['用户年龄'].apply(
            lambda x:
            re.sub(f'~50', '~49' ,str(x)) if '~50' in str(x) else
            re.sub(f'~40', '~39', str(x)) if '~40' in str(x) else
            re.sub(f'~30', '~29' ,str(x)) if '~30' in str(x) else
            re.sub(r'\d{4}~', '', str(x)) if str(x) != 'nan' else
            x
        )
        # 下面是添加人群 AIPL 分类
        dir_file = f'\\\\192.168.1.198\\时尚事业部\\01.运营部\\0-电商周报-每周五更新\\分类配置文件.xlsx'
        dir_file2 = '/Volumes/时尚事业部/01.运营部/0-电商周报-每周五更新/分类配置文件.xlsx'
        if platform.system() == 'Windows':
            dir_file3 = 'C:\\同步空间\\BaiduSyncdisk\\原始文件3\\分类配置文件.xlsx'
        else:
            dir_file3 = '/Users/xigua/数据中心/原始文件3/分类配置文件.xlsx'
        if not os.path.isfile(dir_file):
            dir_file = dir_file2
        if not os.path.isfile(dir_file):
            dir_file = dir_file3
        if os.path.isfile(dir_file):
            df_fl = pd.read_excel(dir_file, sheet_name='人群分类', header=0)
            df_fl = df_fl[['人群名字', '人群分类']]
            # 合并并获取分类信息
            df = pd.merge(df, df_fl, left_on=['人群名字'], right_on=['人群名字'], how='left')
            df['人群分类'].fillna('', inplace=True)
        if '人群分类' in df.columns.tolist():
            # 这行决定了，从文件中读取的分类信息优先级高于内部函数的分类规则
            # 这个 lambda 适配人群名字中带有特定标识的分类，强匹配，自定义命名
            df['人群分类'] = df.apply(
                lambda x: self.set_crowd(keyword=str(x['人群名字']), as_file=False) if x['人群分类'] == ''
                else x['人群分类'], axis=1
            )
            # 这个 lambda 适配人群名字中聚类的特征字符，弱匹配
            df['人群分类'] = df.apply(
                lambda x: self.set_crowd2(keyword=str(x['人群名字']), as_file=False) if x['人群分类'] == ''
                else x['人群分类'], axis=1
            )
        else:
            df['人群分类'] = df['人群名字'].apply(lambda x: self.set_crowd(keyword=str(x), as_file=False))
            df['人群分类'] = df.apply(
                lambda x: self.set_crowd2(keyword=str(x['人群名字']), as_file=False) if x['人群分类'] == ''
                else x['人群分类'], axis=1
            )
        df['人群分类'] = df['人群分类'].apply(lambda x: str(x).upper() if x else x)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        df.fillna(0, inplace=True)
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '推广渠道', '店铺名称', '营销场景', '商品id', '人群名字']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def tg_gjc(self, db_name='聚合数据', table_name='天猫_关键词报表', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景名字': 1,
            '宝贝id': 1,
            '词类型': 1,
            '词名字_词包名字': 1,
            '花费': 1,
            '展现量': 1,
            '点击量': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '直接成交笔数': 1,
            '直接成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'关键词报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df.rename(columns={
            '场景名字': '营销场景',
            '宝贝id': '商品id',
            '总购物车数': '加购量',
            '总成交笔数': '成交笔数',
            '总成交金额': '成交金额'
        }, inplace=True)
        df.fillna(0, inplace=True)
        df = df.astype({
            '商品id': str,
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
        }, errors='raise')
        if is_maximize:
            df = df.groupby(
                ['日期', '店铺名称', '营销场景', '商品id', '词类型', '词名字_词包名字', '花费', '点击量'],
                as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '加购量': ('加购量', np.max),
                    '成交笔数': ('成交笔数', np.max),
                    '成交金额': ('成交金额', np.max),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        else:
            df = df.groupby(
                ['日期', '店铺名称', '营销场景', '商品id', '词类型', '词名字_词包名字', '花费', '点击量'],
                as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max)
                }
            )
        df.insert(loc=1, column='推广渠道', value='万相台无界版')  # df中插入新列
        df['是否品牌词'] = df['词名字_词包名字'].str.contains('万里马|wanlima', regex=True)
        df['是否品牌词'] = df['是否品牌词'].apply(lambda x: '品牌词' if x else '-')
        dir_file = f'\\\\192.168.1.198\\时尚事业部\\01.运营部\\0-电商周报-每周五更新\\分类配置文件.xlsx'
        dir_file2 = '/Volumes/时尚事业部/01.运营部/0-电商周报-每周五更新/分类配置文件.xlsx'
        if not os.path.isfile(dir_file):
            dir_file = dir_file2
        if os.path.isfile(dir_file):
            df_fl = pd.read_excel(dir_file, sheet_name='关键词分类', header=0)
            df_fl = df_fl[['关键词', '词分类']]
            # 合并并获取词分类信息
            df = pd.merge(df, df_fl, left_on=['词名字_词包名字'], right_on=['关键词'], how='left')
            df.pop('关键词')
            df['词分类'].fillna('', inplace=True)
        if '词分类' in df.columns.tolist():
            # 这行决定了，从文件中读取的词分类信息优先级高于 ret_keyword 函数的词分类
            df['词分类'] = df.apply(
                lambda x: self.ret_keyword(keyword=str(x['词名字_词包名字']), as_file=False) if x['词分类'] == ''
                else x['词分类'], axis=1
            )
        else:
            df['词分类'] = df['词名字_词包名字'].apply(lambda x: self.ret_keyword(keyword=str(x), as_file=False))
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '推广渠道', '店铺名称', '营销场景', '商品id', '词类型', '词名字_词包名字']],  # 唯一约束列表
        }

    def tg_cjzb_qzt(self, projection=None, is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        if not projection:
            projection = {
                '日期': 1,
                '场景名字': 1,
                '计划id': 1,
                '全站花费': 1,
                '全站观看次数': 1,
                '全站宝贝点击量': 1,
                '全站成交金额': 1,
                '全站成交笔数': 1,
                '店铺名称': 1,
            }
        __res = []
        for year in range(2025, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'超级直播_全站推广报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        if len(df) == 0:
            return pd.DataFrame()
        return df

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def tg_cjzb(self, db_name='聚合数据', table_name='天猫_超级直播', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景名字': 1,
            '人群名字': 1,
            '计划名字': 1,
            '花费': 1,
            '展现量': 1,
            '进店量': 1,
            '粉丝关注量': 1,
            '观看次数': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '直接成交笔数': 1,
            '直接成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'超级直播报表_人群_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        # 直播全站推广不包含的超级直播报表，所以单独添加   2025-03-07
        cjzb_qzt = self.tg_cjzb_qzt(is_maximize=True)
        if len(cjzb_qzt) > 0:
            # 这里的重命名要注意，因为 tg_cjzb 函数还要重命名一次，注意改为 tg_cjzb 命名前的列名
            cjzb_qzt.rename(columns={
                '全站花费': '花费',
                '全站观看次数': '观看次数',
                '全站宝贝点击量': '点击量',
                '全站成交金额': '总成交金额',
                '全站成交笔数': '总成交笔数'
            }, inplace=True)
            for col in df.columns.tolist():
                if col not in cjzb_qzt.columns.tolist():
                    cjzb_qzt[col] = 0
            df = pd.concat([df, cjzb_qzt], ignore_index=True)
        df.rename(columns={
            '观看次数': '观看次数',
            '总购物车数': '加购量',
            '总成交笔数': '成交笔数',
            '总成交金额': '成交金额',
            '场景名字': '营销场景',
        }, inplace=True)
        df['营销场景'] = '超级直播'
        df.fillna(0, inplace=True)
        df = df.astype({
            '花费': 'float64',
            # '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '进店量': 'int64',
            '粉丝关注量': 'int64',
            '观看次数': 'int64',
        }, errors='raise')
        df = df[df['花费'] > 0]
        df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
        if is_maximize:
            df = df.groupby(['日期', '店铺名称', '营销场景', '人群名字', '计划名字', '花费', '观看次数'],
                            as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '进店量': ('进店量', np.max),
                    '粉丝关注量': ('粉丝关注量', np.max),
                    '加购量': ('加购量', np.max),
                    '成交笔数': ('成交笔数', np.max),
                    '成交金额': ('成交金额', np.max),
                    '直接成交笔数': ('直接成交笔数', np.max),
                    '直接成交金额': ('直接成交金额', np.max),
                }
            )
        else:
            df = df.groupby(['日期', '店铺名称', '营销场景', '人群名字', '计划名字', '花费', '观看次数'],
                            as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '进店量': ('进店量', np.min),
                    '粉丝关注量': ('粉丝关注量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '直接成交笔数': ('直接成交笔数', np.min),
                    '直接成交金额': ('直接成交金额', np.min),
                }
            )
        df.insert(loc=1, column='推广渠道', value='万相台无界版')  # df中插入新列
        self.pf_datas.append(
            {
                '集合名称': table_name,
                '数据主体': df[['日期', '店铺名称', '推广渠道', '营销场景', '花费', '展现量', '观看次数', '加购量', '成交笔数', '成交金额', '直接成交笔数', '直接成交金额']]
            },
        )  # 制作其他聚合表
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '推广渠道', '店铺名称', '营销场景', '人群名字', '计划名字']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    def pxb_zh(self, db_name='聚合数据', table_name='天猫_品销宝账户报表', is_maximize=True):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '报表类型': 1,
            '搜索量': 1,
            '搜索访客数': 1,
            '展现量': 1,
            # '自然流量增量曝光': 1,
            '消耗': 1,
            '点击量': 1,
            '宝贝加购数': 1,
            '成交笔数': 1,
            '成交金额': 1,
            # '成交访客数': 1
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'品销宝_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df = df[df['报表类型'] == '账户']
        df.fillna(value=0, inplace=True)
        df.rename(columns={
            '消耗': '花费',
            '宝贝加购数': '加购量',
            '搜索量': '品牌搜索量',
            '搜索访客数': '品牌搜索人数'
        }, inplace=True)
        df = df.astype({
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'int64',
            '品牌搜索量': 'int64',
            '品牌搜索人数': 'int64',
        }, errors='raise')
        if is_maximize:
            df = df.groupby(['日期', '店铺名称', '报表类型', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '加购量': ('加购量', np.max),
                    '成交笔数': ('成交笔数', np.max),
                    '成交金额': ('成交金额', np.max),
                    '品牌搜索量': ('品牌搜索量', np.max),
                    '品牌搜索人数': ('品牌搜索人数', np.max),
                }
            )
        else:
            df = df.groupby(['日期', '店铺名称', '报表类型', '花费', '点击量'], as_index=False).agg(
                **{
                    '展现量': ('展现量', np.min),
                    '加购量': ('加购量', np.min),
                    '成交笔数': ('成交笔数', np.min),
                    '成交金额': ('成交金额', np.min),
                    '品牌搜索量': ('品牌搜索量', np.min),
                    '品牌搜索人数': ('品牌搜索人数', np.min),
                }
            )
        df.insert(loc=1, column='推广渠道', value='品销宝')  # df中插入新列
        df.insert(loc=2, column='营销场景', value='品销宝')  # df中插入新列
        self.pf_datas.append(
            {
                '集合名称': table_name,
                '数据主体': df[['日期', '店铺名称', '推广渠道', '营销场景', '花费', '展现量', '点击量', '加购量', '成交笔数', '成交金额']]
            },
        )  # 制作其他聚合表
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        logger.info('更新', {'主机': f'{host}:{port}', '库': db_name, '表': table_name})
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '推广渠道', '店铺名称', '营销场景', '报表类型', '花费', '展现量']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    def idbm(self, db_name='聚合数据', table_name='商品id编码表'):
        """ 用生意经日数据制作商品 id 和编码对照表 """
        projection = {
            '日期': 1,
            '商品id': 1,
            '商家编码': 1,
            '一级类目': 1,
            '二级类目': 1,
            '三级类目': 1,
            '更新时间': 1
        }
        df = self.download_manager.data_to_df(
            db_name='属性设置3',
            table_name='商品sku属性',
            start_date='2024-11-17',
            end_date='2049-12-31',
            projection=projection,
        )
        # 仅保留最新日期的数据
        idx = df.groupby(['日期', '商品id'])['更新时间'].idxmax()
        df = df.loc[idx]
        df.rename(columns={'商品id': '宝贝id'}, inplace=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        logger.info('更新', {'主机': f'{host}:{port}', '库': db_name, '表': table_name})
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['宝贝id']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def sp_picture(self, db_name='聚合数据', table_name='商品id图片对照表'):
        """  """
        projection = {
            '日期': 1,
            '商品id': 1,
            '白底图': 1,
            '商家编码': 1,
            'sku_id': 1,
            'sku地址': 1,
            '更新时间': 1
        }
        df = self.download_manager.data_to_df(
            db_name='属性设置3',
            table_name='商品sku属性',
            start_date='2024-11-17',
            end_date='2049-12-31',
            projection=projection,
        )
        # 仅保留最新日期的数据
        idx = df.groupby(['日期', 'sku_id'])['更新时间'].idxmax()
        df = df.loc[idx]
        df.rename(columns={'白底图': '商品图片'}, inplace=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['sku_id']],  # 唯一约束列表
        }

    @upload_data_decorator()
    def item_up(self, db_name='聚合数据', table_name='淘宝店铺货品'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {}
        df_set = self.download_manager.data_to_df(
            db_name='属性设置3',
            table_name=f'货品年份基准',
            start_date=start_date,
            end_date=end_date,
            projection={'商品id':1, '上市年份':1},
        )
        df = self.download_manager.data_to_df(
            db_name='市场数据3',
            table_name=f'淘宝店铺数据',
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        df.pop('data_sku')
        df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
        df_set['商品id'] = df_set['商品id'].astype('int64')
        df['商品id'] = df['商品id'].astype('int64')
        df_set.sort_values('商品id', ascending=False, ignore_index=True, inplace=True)

        # 仅保留最新日期的数据
        idx = df.groupby(['商品id'])['更新时间'].idxmax()
        df = df.loc[idx]

        def check_year(item_id):
            for item in df_set.to_dict(orient='records'):
                if item_id > item['商品id']:
                    return item['上市年份']

        df['上市年份'] = df['商品id'].apply(lambda x: check_year(x))
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺id', '商品id']],  # 唯一约束列表
        }

    @upload_data_decorator()
    def spph(self, db_name='聚合数据', table_name='天猫_商品排行'):
        """  """
        start_date, end_date = self.months_data(num=self.months)
        projection = {}
        __res = []
        for year in range(2024, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name='生意参谋3',
                table_name=f'商品排行_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)

        projection = {}
        df_set = self.download_manager.data_to_df(
            db_name='属性设置3',
            table_name=f'货品年份基准',
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        # 保留最新日期的数据
        idx = df.groupby(['日期', '店铺名称', '商品id'])['更新时间'].idxmax()
        df = df.loc[idx]

        df_set['商品id'] = df_set['商品id'].astype('int64')
        df_set = df_set[['商品id', '上市年份']]
        df['商品id'] = df['商品id'].astype('int64')
        df_set.sort_values('商品id', ascending=False, ignore_index=True, inplace=True)

        def check_year(item_id):
            for item in df_set.to_dict(orient='records'):
                if item_id > item['商品id']:
                    return item['上市年份']

        df['上市年份'] = df['商品id'].apply(lambda x: check_year(x))
        p = df.pop('上市年份')
        df.insert(loc=7, column='上市年月', value=p)
        df['上市年份_f'] = df['上市年月'].apply(lambda x: '0' if x == '历史悠久' else re.findall(r'(\d+)年', x)[0])
        p = df.pop('上市年份_f')
        df.insert(loc=7, column='上市年份_f', value=p)

        def check_jijie(string):
            pattern = re.findall(r'\d+年(\d+)月', string)
            if not pattern:
                return '-'
            pattern = pattern[0]
            if 0 < int(pattern) < 4:
                return '春'
            elif 4 < int(pattern) < 6:
                return '夏'
            elif 6 < int(pattern) < 9:
                return '秋'
            else:
                return '冬'

        df['上市季节'] = df['上市年月'].apply(lambda x: check_jijie(x))
        p = df.pop('上市季节')
        df.insert(loc=9, column='上市季节', value=p)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '商品id']],  # 唯一约束列表
        }

    # @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def dplyd(self, db_name='聚合数据', table_name='店铺流量来源构成'):
        """ 新旧版取的字段是一样的 """
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '店铺名称': 1,
            '类别': 1,
            '来源构成': 1,
            '一级来源': 1,
            '二级来源': 1,
            '三级来源': 1,
            '访客数': 1,
            '支付金额': 1,
            '支付买家数': 1,
            '支付转化率': 1,
            '加购人数': 1,
            '加购件数': 1,
            '下单买家数': 1,
            '关注店铺人数': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name='生意参谋3',
                table_name=f'店铺流量来源构成_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df = df.astype({'访客数': 'int64'}, errors='ignore')
        df = df[df['访客数'] > 0]
        df.drop_duplicates(subset=['日期', '店铺名称', '类别', '来源构成', '一级来源', '二级来源', '三级来源', '访客数'], keep='last', inplace=True, ignore_index=True)
        # 包含三级来源名称和预设索引值列
        # 截取 从上月1日 至 今天的花费数据, 推广款式按此数据从高到低排序（商品图+排序）
        last_month, ii = get_day_of_month(1)
        df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
        df_visitor3 = df[df['日期'] >= pd.to_datetime(last_month)]
        df_visitor3 = df_visitor3[(df_visitor3['三级来源'] != '汇总') & (df_visitor3['三级来源'] != '0')]
        df_visitor3 = df_visitor3.groupby(['三级来源'], as_index=False).agg({'访客数': 'sum'})
        df_visitor3.sort_values('访客数', ascending=False, ignore_index=True, inplace=True)
        df_visitor3.reset_index(inplace=True)
        df_visitor3['index'] = df_visitor3['index'] + 100
        df_visitor3.rename(columns={'index': '三级来源索引'}, inplace=True)
        df_visitor3 = df_visitor3[['三级来源', '三级来源索引']]
        # 包含二级来源名称和预设索引值列
        df_visitor2 = df[df['日期'] >= pd.to_datetime(last_month)]
        df_visitor2 = df_visitor2[(df_visitor2['二级来源'] != '汇总') & (df_visitor2['二级来源'] != '0')]
        df_visitor2 = df_visitor2.groupby(['二级来源'], as_index=False).agg({'访客数': 'sum'})
        df_visitor2.sort_values('访客数', ascending=False, ignore_index=True, inplace=True)
        df_visitor2.reset_index(inplace=True)
        df_visitor2['index'] = df_visitor2['index'] + 100
        df_visitor2.rename(columns={'index': '二级来源索引'}, inplace=True)
        df_visitor2 = df_visitor2[['二级来源', '二级来源索引']]
        # 包含一级来源名称和预设索引值列
        df_visitor1 = df[df['日期'] >= pd.to_datetime(last_month)]
        df_visitor1 = df_visitor1[(df_visitor1['一级来源'] != '汇总') & (df_visitor1['一级来源'] != '0')]
        df_visitor1 = df_visitor1.groupby(['一级来源'], as_index=False).agg({'访客数': 'sum'})
        df_visitor1.sort_values('访客数', ascending=False, ignore_index=True, inplace=True)
        df_visitor1.reset_index(inplace=True)
        df_visitor1['index'] = df_visitor1['index'] + 100
        df_visitor1.rename(columns={'index': '一级来源索引'}, inplace=True)
        df_visitor1 = df_visitor1[['一级来源', '一级来源索引']]

        df = pd.merge(df, df_visitor1, how='left', left_on='一级来源', right_on='一级来源')
        df = pd.merge(df, df_visitor2, how='left', left_on='二级来源', right_on='二级来源')
        df = pd.merge(df, df_visitor3, how='left', left_on='三级来源', right_on='三级来源')
        for col in ['一级来源索引', '二级来源索引', '三级来源索引']:
            df[col] = df[col].apply(lambda x: 1000 if str(x) == 'nan' else x)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '类别', '来源构成', '一级来源', '二级来源', '三级来源']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def sp_cost(self, db_name='聚合数据', table_name='商品成本'):
        """ 电商定价 """
        data_values = self.download_manager.columns_to_list(
            db_name='属性设置3',
            table_name='电商定价',
            columns_name=['日期', '款号', '年份季节', '吊牌价', '商家平台', '成本价', '天猫页面价', '天猫中促价'],
        )
        df = pd.DataFrame(data=data_values)
        df.sort_values(by=['款号', '日期'], ascending=[False, True], ignore_index=True, inplace=True)
        df.drop_duplicates(subset=['款号'], keep='last', inplace=True, ignore_index=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['款号']],  # 唯一约束列表
        }

    # @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def jdjzt(self, db_name='聚合数据', table_name='京东_京准通'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '产品线': 1,
            '触发sku_id': 1,
            '跟单sku_id': 1,
            '花费': 1,
            '展现数': 1,
            '点击数': 1,
            '直接订单行': 1,
            '直接订单金额': 1,
            '总订单行': 1,
            '总订单金额': 1,
            '直接加购数': 1,
            '总加购数': 1,
            'spu_id': 1,
            '店铺名称':1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                    db_name='京东数据3',
                    table_name=f'推广数据_京准通_{year}',
                    start_date=start_date,
                    end_date=end_date,
                    projection=projection,
                )
            __res.append(df)
        # 新增加自营店数据 2025-03-19
        for year in range(2025, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                    db_name='京东数据3',
                    table_name=f'推广数据_京准通_自营店_{year}',
                    start_date=start_date,
                    end_date=end_date,
                    projection=projection,
                )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df = df.groupby(
            ['日期', '店铺名称', '产品线', '触发sku_id', '跟单sku_id', 'spu_id', '花费', '展现数', '点击数'],
            as_index=False).agg(
            **{
                '直接订单行': ('直接订单行', np.max),
                '直接订单金额': ('直接订单金额', np.max),
                '总订单行': ('总订单行', np.max),
                '总订单金额': ('总订单金额', np.max),
                '直接加购数': ('直接加购数', np.max),
                '总加购数': ('总加购数', np.max),
            }
        )
        df = df[df['花费'] > 0]
        projection={
            'sku_id': 1,
            'spu_id': 1,
        }
        df_sku = self.download_manager.data_to_df(
            db_name='属性设置3',
            table_name='京东商品属性',
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        if 'spu_id' in df.columns:
            df = df.drop(columns=['spu_id'])  # 删除原有 spu_id，避免冲突
        df = pd.merge(df, df_sku, how='left', left_on='跟单sku_id', right_on='sku_id')
        df = df.drop(columns=['sku_id'])  # 删除 merge 进来的 sku_id
        df['spu_id'] = df['spu_id'].fillna(0)  # 填充 spu_id 空值
        # 调整 spu_id 到第3列
        cols = list(df.columns)
        cols.insert(3, cols.pop(cols.index('spu_id')))
        df = df[cols]
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '产品线', '触发sku_id', '跟单sku_id', '花费']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def jdqzyx(self, db_name='聚合数据', table_name='京东_京准通_全站营销'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '店铺名称': 1,
            '产品线': 1,
            '花费': 1,
            '全站投产比': 1,
            '全站交易额': 1,
            '全站订单行': 1,
            '全站订单成本': 1,
            '全站费比': 1,
            '核心位置展现量': 1,
            '核心位置点击量': 1,
        }
        df = self.download_manager.data_to_df(
            db_name='京东数据3',
            table_name='推广数据_全站营销',  # 暂缺
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        if len(df) == 0:
            return None, None
        df = df.groupby(['日期', '店铺名称', '产品线', '花费'], as_index=False).agg(
            **{
                '全站投产比': ('全站投产比', np.max),
                '全站交易额': ('全站交易额', np.max),
                '全站订单行': ('全站订单行', np.max),
                '全站订单成本': ('全站订单成本', np.max),
                '全站费比': ('全站费比', np.max),
                '核心位置展现量': ('核心位置展现量', np.max),
                '核心位置点击量': ('核心位置点击量', np.max),
            }
        )
        df = df[df['花费'] > 0]
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '产品线']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def jd_gjc(self, db_name='聚合数据', table_name='京东_关键词报表'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '产品线': 1,
            '计划类型': 1,
            '计划id': 1,
            '推广计划': 1,
            '搜索词': 1,
            '关键词': 1,
            '关键词购买类型': 1,
            '广告定向类型': 1,
            '花费': 1,
            '展现数': 1,
            '点击数': 1,
            '直接订单行': 1,
            '直接订单金额': 1,
            '总订单行': 1,
            '总订单金额': 1,
            '总加购数': 1,
            '领券数': 1,
            '商品关注数': 1,
            '店铺关注数': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                    db_name='京东数据3',
                    table_name=f'推广数据_关键词报表_{year}',
                    start_date=start_date,
                    end_date=end_date,
                    projection=projection,
                )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df_lin = df[['计划id', '推广计划']]
        df_lin.drop_duplicates(subset=['计划id'], keep='last', inplace=True, ignore_index=True)
        df = df.groupby(
            ['日期', '产品线', '计划类型', '计划id', '搜索词', '关键词', '关键词购买类型', '广告定向类型', '展现数',
             '点击数', '花费'],
            as_index=False).agg(
            **{
                '直接订单行': ('直接订单行', np.max),
                '直接订单金额': ('直接订单金额', np.max),
                '总订单行': ('总订单行', np.max),
                '总订单金额': ('总订单金额', np.max),
                '总加购数': ('总加购数', np.max),
                '领券数': ('领券数', np.max),
                '商品关注数': ('商品关注数', np.max),
                '店铺关注数': ('店铺关注数', np.max)
            }
        )
        df = pd.merge(df, df_lin, how='left', left_on='计划id', right_on='计划id')
        df['k_是否品牌词'] = df['关键词'].str.contains('万里马|wanlima', regex=True)
        df['k_是否品牌词'] = df['k_是否品牌词'].apply(lambda x: '品牌词' if x else '-')
        df['s_是否品牌词'] = df['搜索词'].str.contains('万里马|wanlima', regex=True)
        df['s_是否品牌词'] = df['s_是否品牌词'].apply(lambda x: '品牌词' if x else '-')
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '产品线', '计划id', '搜索词', '关键词']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def sku_sales(self, db_name='聚合数据', table_name='京东_sku_商品明细'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '店铺名称': 1,
            '商品id': 1,
            '货号': 1,
            '成交单量': 1,
            '成交金额': 1,
            '访客数': 1,
            '成交客户数': 1,
            '加购商品件数': 1,
            '加购人数': 1,
            '更新时间': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='京东数据3',
                table_name=f'京东商智_sku_商品明细_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df = df[df['商品id'] != '合计']
        # 仅保留最新日期的数据
        idx = df.groupby(['日期', '店铺名称', '商品id', '货号', '访客数', '成交客户数', '加购商品件数', '加购人数'])['更新时间'].idxmax()
        df = df.loc[idx]
        df = df[['日期', '店铺名称', '商品id', '货号', '访客数', '成交客户数', '加购商品件数', '加购人数', '成交单量', '成交金额']]
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '商品id']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def spu_sales(self, db_name='聚合数据', table_name='京东_spu_商品明细'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '店铺名称': 1,
            '商品id': 1,
            '货号': 1,
            '成交单量': 1,
            '成交金额': 1,
            '访客数': 1,
            '成交客户数': 1,
            '加购商品件数': 1,
            '加购人数': 1,
            '更新时间': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df = self.download_manager.data_to_df(
                db_name='京东数据3',
                table_name=f'京东商智_spu_商品明细_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        df = df[df['商品id'] != '合计']
        # 仅保留最新日期的数据
        idx = df.groupby(['日期', '店铺名称', '商品id', '货号', '访客数', '成交客户数', '加购商品件数', '加购人数'])['更新时间'].idxmax()
        df = df.loc[idx]
        df = df[['日期', '店铺名称', '商品id', '货号', '访客数', '成交客户数', '加购商品件数', '加购人数', '成交单量', '成交金额']]
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '商品id']],  # 唯一约束列表
        }

    @staticmethod
    def months_data(num=0, end_date=None):
        """ 读取近 num 个月的数据, 0 表示读取当月的数据 """
        if not end_date:
            end_date = datetime.datetime.now()
        start_date = end_date - relativedelta(months=num)  # n 月以前的今天
        start_date = f'{start_date.year}-{start_date.month}-01'  # 替换为 n 月以前的第一天
        return pd.to_datetime(start_date), pd.to_datetime(end_date)

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def se_search(self, db_name='聚合数据', table_name='天猫店铺来源_手淘搜索'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '店铺名称': 1,
            '搜索词': 1,
            '词类型': 1,
            '访客数': 1,
            '加购人数': 1,
            '商品收藏人数': 1,
            '支付转化率': 1,
            '支付买家数': 1,
            '支付金额': 1,
            '新访客': 1,
            '客单价': 1,
            'uv价值': 1,
            '更新时间': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year+1):
            df = self.download_manager.data_to_df(
                db_name='生意参谋3',
                table_name=f'手淘搜索_本店引流词_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df)
        df = pd.concat(__res, ignore_index=True)
        idx = df.groupby(['日期', '店铺名称', '词类型', '搜索词'])['更新时间'].idxmax()
        df = df.loc[idx]
        df = df[['日期', '店铺名称', '词类型', '搜索词', '访客数', '加购人数', '支付金额', '支付转化率', '支付买家数', '客单价', 'uv价值']]
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '词类型', '搜索词']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def zb_ccfx(self, db_name='聚合数据', table_name='生意参谋_直播场次分析'):
        start_date, end_date = self.months_data(num=self.months)
        df = self.download_manager.data_to_df(
            db_name='生意参谋3',
            table_name='直播分场次效果',
            start_date=start_date,
            end_date=end_date,
            projection={},
        )
        df.drop_duplicates(subset=['场次id'], keep='first', inplace=True, ignore_index=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        ordered_columns = [
            '日期',
            '店铺名称',
            '场次信息',
            '场次id',
            '直播开播时间',
            '开播时长',
            '封面图点击率',
            '观看人数',
            '观看次数',
            '新增粉丝数',
            '流量券消耗',
            '观看总时长',
            '人均观看时长',
            '次均观看时长',
            '商品点击人数',
            '商品点击次数',
            '商品点击率',
            '加购人数',
            '加购件数',
            '加购次数',
            '成交金额',
            '成交人数',
            '成交件数',
            '成交笔数',
            '成交转化率',
            '退款人数',
            '退款笔数',
            '退款件数',
            '退款金额',
            '预售定金支付金额',
            '预售预估总金额',
        ]
        # 使用reindex重排列顺序，未定义的列会自动放在最后
        df = df.reindex(columns=[col for col in ordered_columns if col in df.columns] + 
                              [col for col in df.columns if col not in ordered_columns])
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['场次id']],  # 唯一约束列表
        }

    # @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def tg_by_day(self, db_name='聚合数据', table_name='多店推广场景_按日聚合'):
        """
        汇总各个店铺的推广数据，按日汇总
        """
        df_tm = pd.DataFrame()  # 天猫营销场景
        df_tb = pd.DataFrame()  # 淘宝营销场景
        df_al = pd.DataFrame()  # 奥莱营销场景
        df_tb_qzt = pd.DataFrame()  # 淘宝全站推广
        df_tm_pxb = pd.DataFrame()  # 天猫品销宝
        df_tm_living = pd.DataFrame()  # 天猫超级直播
        df_jd = pd.DataFrame()  # 京东推广
        df_jd_qzyx = pd.DataFrame()  # 京东全站推广
        df_jd_ziying = pd.DataFrame()  # 京东推广
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '场景id': 1,
            '场景名字': 1,
            '花费': 1,
            '展现量': 1,
            '点击量': 1,
            '总购物车数': 1,
            '总成交笔数': 1,
            '总成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df_tm = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'营销场景报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df_tm)
        df_tm = pd.concat(__res, ignore_index=True)
        if len(df_tm) > 0:
            df_tm.rename(columns={'场景名字': '营销场景'}, inplace=True)
            df_tm = df_tm.groupby(
                ['日期', '店铺名称', '场景id', '营销场景', '花费', '展现量'],
                as_index=False).agg(
                **{
                    # '展现量': ('展现量', np.max),
                    '点击量': ('点击量', np.max),
                    '加购量': ('总购物车数', np.max),
                    '成交笔数': ('总成交笔数', np.max),
                    '成交金额': ('总成交金额', np.max)
                }
            )
        # 奥莱店
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df_al = self.download_manager.data_to_df(
                db_name='推广数据_奥莱店',
                table_name=f'营销场景报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df_al)
        df_al = pd.concat(__res, ignore_index=True)
        if len(df_al) > 0:
            df_al.rename(columns={'场景名字': '营销场景'}, inplace=True)
            df_al['店铺名称'] = df_al['店铺名称'].apply(lambda x: '万里马箱包outlet店' if x == 'Wanlima万里马箱包outlet店' else x)
            df_al = df_al.groupby(
                ['日期', '店铺名称', '场景id', '营销场景', '花费', '展现量'],
                as_index=False).agg(
                **{
                    # '展现量': ('展现量', np.max),
                    '点击量': ('点击量', np.max),
                    '加购量': ('总购物车数', np.max),
                    '成交笔数': ('总成交笔数', np.max),
                    '成交金额': ('总成交金额', np.max)
                }
            )
        # sj圣积
        __res = []
        for year in range(2025, datetime.datetime.today().year + 1):
            df_sj = self.download_manager.data_to_df(
                db_name='推广数据_圣积天猫店',
                table_name=f'营销场景报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df_sj)
        df_sj = pd.concat(__res, ignore_index=True)
        if len(df_sj) > 0:
            df_sj.rename(columns={'场景名字': '营销场景'}, inplace=True)
            df_sj['店铺名称'] = df_sj['店铺名称'].apply(lambda x: 'saintJack旗舰店' if x == 'SAINTJACK旗舰店' else x)
            df_sj = df_sj.groupby(
                ['日期', '店铺名称', '场景id', '营销场景', '花费', '展现量'],
                as_index=False).agg(
                **{
                    # '展现量': ('展现量', np.max),
                    '点击量': ('点击量', np.max),
                    '加购量': ('总购物车数', np.max),
                    '成交笔数': ('总成交笔数', np.max),
                    '成交金额': ('总成交金额', np.max)
                }
            )
        # 淘宝店
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df_tb = self.download_manager.data_to_df(
                db_name='推广数据_淘宝店',
                table_name=f'营销场景报表_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df_tb)
        df_tb = pd.concat(__res, ignore_index=True)
        if len(df_tb) > 0:
            df_tb.rename(columns={'场景名字': '营销场景'}, inplace=True)
            df_tb = df_tb.groupby(
                ['日期', '店铺名称', '场景id', '营销场景', '花费', '展现量'],
                as_index=False).agg(
                **{
                    # '展现量': ('展现量', np.max),
                    '点击量': ('点击量', np.max),
                    '加购量': ('总购物车数', np.max),
                    '成交笔数': ('总成交笔数', np.max),
                    '成交金额': ('总成交金额', np.max)
                }
            )
        #  天猫的全站推广包含在营销场景报表中，淘宝店不包含
        df_tb_qzt = pd.DataFrame()
        if '全站推广' not in df_tb['营销场景'].tolist():
            projection = {
                '日期': 1,
                '主体id': 1,
                '花费': 1,
                '展现量': 1,
                '点击量': 1,
                '总购物车数': 1,
                '总成交笔数': 1,
                '总成交金额': 1,
                '店铺名称': 1,
            }
            __res = []
            for year in range(2024, datetime.datetime.today().year + 1):
                df_tb_qzt = self.download_manager.data_to_df(
                    db_name='推广数据_淘宝店',
                    table_name=f'全站推广报表_{year}',
                    start_date=start_date,
                    end_date=end_date,
                    projection=projection,
                )
                __res.append(df_tb_qzt)
            df_tb_qzt = pd.concat(__res, ignore_index=True)
            if len(df_tb_qzt) > 0:
                # 这一步是排重
                df_tb_qzt = df_tb_qzt.groupby(
                    ['日期', '店铺名称', '主体id', '花费'],
                    as_index=False).agg(
                    **{
                        '展现量': ('展现量', np.max),
                        '点击量': ('点击量', np.max),
                        '加购量': ('总购物车数', np.max),
                        '成交笔数': ('总成交笔数', np.max),
                        '成交金额': ('总成交金额', np.max)
                    }
                )
                # 这一步是继续聚合，因为这个报表统计的是场景维度，不需要商品维度
                df_tb_qzt = df_tb_qzt.groupby(
                    ['日期', '店铺名称', '花费'],
                    as_index=False).agg(
                    **{
                        '展现量': ('展现量', np.sum),
                        '点击量': ('点击量', np.sum),
                        '加购量': ('加购量', np.sum),
                        '成交笔数': ('成交笔数', np.sum),
                        '成交金额': ('成交金额', np.sum)
                    }
                )
                df_tb_qzt['营销场景'] = '全站推广'
        # 品销宝报表
        projection = {
            '日期': 1,
            '报表类型': 1,
            '消耗': 1,
            '展现量': 1,
            '点击量': 1,
            '宝贝加购数': 1,
            '成交笔数': 1,
            '成交金额': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df_tm_pxb = self.download_manager.data_to_df(
                db_name='推广数据2',
                table_name=f'品销宝_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df_tm_pxb)
        df_tm_pxb = pd.concat(__res, ignore_index=True)
        if len(df_tm_pxb) > 0:
            df_tm_pxb = df_tm_pxb[df_tm_pxb['报表类型'] == '账户']
            df_tm_pxb = df_tm_pxb.groupby(
                ['日期', '店铺名称', '报表类型', '消耗'],
                as_index=False).agg(
                **{
                    '展现量': ('展现量', np.max),
                    '点击量': ('点击量', np.max),
                    '加购量': ('宝贝加购数', np.max),
                    '成交笔数': ('成交笔数', np.max),
                    '成交金额': ('成交金额', np.max)
                }
            )
            df_tm_pxb.rename(columns={'报表类型': '营销场景', '消耗': '花费'}, inplace=True)
            df_tm_pxb['营销场景'] = '品销宝'
        # 因为 2024.04.16及之前的营销场景报表不含超级直播，所以在此添加
        if start_date < pd.to_datetime('2024-04-17'):
            projection = {
                '日期': 1,
                '场景名字': 1,
                '花费': 1,
                '展现量': 1,
                '观看次数': 1,
                '总购物车数': 1,
                '总成交笔数': 1,
                '总成交金额': 1,
                '店铺名称': 1,
            }
            __res = []
            for year in range(2024, datetime.datetime.today().year + 1):
                df_tm_living = self.download_manager.data_to_df(
                    db_name='推广数据2',
                    table_name=f'超级直播报表_人群_{year}',
                    start_date=start_date,
                    end_date=pd.to_datetime('2024-04-16'),  # 只可以取此日期之前的数据
                    projection=projection,
                )
                __res.append(df_tm_living)
            df_tm_living = pd.concat(__res, ignore_index=True)
            if len(df_tm_living) > 0:
                df_tm_living.rename(columns={'场景名字': '营销场景'}, inplace=True)
                df_tm_living = df_tm_living.groupby(
                    ['日期', '店铺名称', '营销场景', '花费'],
                    as_index=False).agg(
                    **{
                        '展现量': ('展现量', np.max),
                        '点击量': ('观看次数', np.max),
                        '加购量': ('总购物车数', np.max),
                        '成交笔数': ('总成交笔数', np.max),
                        '成交金额': ('总成交金额', np.max)
                    }
                )
        # 京东数据
        projection = {
            '日期': 1,
            '产品线': 1,
            '触发sku_id': 1,
            '跟单sku_id': 1,
            '花费': 1,
            '展现数': 1,
            '点击数': 1,
            '直接订单行': 1,
            '直接订单金额': 1,
            '总订单行': 1,
            '总订单金额': 1,
            '直接加购数': 1,
            '总加购数': 1,
            'spu_id': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df_jd = self.download_manager.data_to_df(
                    db_name='京东数据3',
                    table_name=f'推广数据_京准通_{year}',
                    start_date=start_date,
                    end_date=end_date,
                    projection=projection,
                )
            __res.append(df_jd)
        df_jd = pd.concat(__res, ignore_index=True)
        if len(df_jd) > 0:
            df_jd = df_jd.groupby(['日期', '店铺名称', '产品线', '触发sku_id', '跟单sku_id', 'spu_id', '花费', '展现数', '点击数'],
                            as_index=False).agg(
                **{
                    '直接订单行': ('直接订单行', np.max),
                    '直接订单金额': ('直接订单金额', np.max),
                    '成交笔数': ('总订单行', np.max),
                    '成交金额': ('总订单金额', np.max),
                    '直接加购数': ('直接加购数', np.max),
                    '加购量': ('总加购数', np.max),
                }
            )
            df_jd = df_jd[['日期', '店铺名称', '产品线', '花费', '展现数', '点击数', '加购量', '成交笔数', '成交金额']]
            df_jd.rename(columns={'产品线': '营销场景', '展现数': '展现量', '点击数': '点击量'}, inplace=True)
            df_jd = df_jd[df_jd['花费'] > 0]
        projection = {
            '日期': 1,
            '产品线': 1,
            '花费': 1,
            '全站投产比': 1,
            '全站交易额': 1,
            '全站订单行': 1,
            '全站订单成本': 1,
            '全站费比': 1,
            '核心位置展现量': 1,
            '核心位置点击量': 1,
            '店铺名称': 1,
        }
        df_jd_qzyx = self.download_manager.data_to_df(
            db_name='京东数据3',
            table_name='推广数据_全站营销',
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        if len(df_jd_qzyx) > 0:
            df_jd_qzyx = df_jd_qzyx.groupby(['日期', '店铺名称', '产品线', '花费'], as_index=False).agg(
                **{'全站投产比': ('全站投产比', np.max),
                   '成交金额': ('全站交易额', np.max),
                   '成交笔数': ('全站订单行', np.max),
                   '全站订单成本': ('全站订单成本', np.max),
                   '全站费比': ('全站费比', np.max),
                   '展现量': ('核心位置展现量', np.max),
                   '点击量': ('核心位置点击量', np.max),
                   }
            )
            df_jd_qzyx.rename(columns={'产品线': '营销场景'}, inplace=True)
            df_jd_qzyx = df_jd_qzyx[['日期', '店铺名称', '营销场景', '花费', '展现量', '点击量', '成交笔数', '成交金额']]
            df_jd_qzyx = df_jd_qzyx[df_jd_qzyx['花费'] > 0]
        # 京东自营店数据
        projection = {
            '日期': 1,
            '产品线': 1,
            '触发sku_id': 1,
            '跟单sku_id': 1,
            '花费': 1,
            '展现数': 1,
            '点击数': 1,
            '直接订单行': 1,
            '直接订单金额': 1,
            '总订单行': 1,
            '总订单金额': 1,
            '直接加购数': 1,
            '总加购数': 1,
            'spu_id': 1,
            '店铺名称': 1,
        }
        __res = []
        for year in range(2025, datetime.datetime.today().year + 1):
            df_jd_ziying = self.download_manager.data_to_df(
                db_name='京东数据3',
                table_name=f'推广数据_京准通_自营店_{year}',
                start_date=start_date,
                end_date=end_date,
                projection=projection,
            )
            __res.append(df_jd_ziying)
        df_jd_ziying = pd.concat(__res, ignore_index=True)
        if len(df_jd_ziying) > 0:
            df_jd_ziying = df_jd_ziying.groupby(
                ['日期', '店铺名称', '产品线', '触发sku_id', '跟单sku_id', 'spu_id', '花费', '展现数', '点击数'],
                as_index=False).agg(
                **{
                    '直接订单行': ('直接订单行', np.max),
                    '直接订单金额': ('直接订单金额', np.max),
                    '成交笔数': ('总订单行', np.max),
                    '成交金额': ('总订单金额', np.max),
                    '直接加购数': ('直接加购数', np.max),
                    '加购量': ('总加购数', np.max),
                }
            )
            df_jd_ziying = df_jd_ziying[['日期', '店铺名称', '产品线', '花费', '展现数', '点击数', '加购量', '成交笔数', '成交金额']]
            df_jd_ziying.rename(columns={'产品线': '营销场景', '展现数': '展现量', '点击数': '点击量'}, inplace=True)
            df_jd_ziying = df_jd_ziying[df_jd_ziying['花费'] > 0]

        _datas = [item for item in  [df_tm, df_tb, df_tb_qzt, df_al, df_sj, df_tm_pxb, df_tm_living, df_jd, df_jd_qzyx, df_jd_ziying] if len(item) > 0]  # 阻止空的 dataframe
        df = pd.concat(_datas, axis=0, ignore_index=True)
        # 超级直播全站推广不包含在营销场景报表中，所以单独添加  2025-03-05
        projection = {
            '日期': 1,
            '店铺名称': 1,
            '场景id': 1,
            '场景名字': 1,
            '全站花费': 1,
            '全站观看次数': 1,
            '全站宝贝点击量': 1,
            '全站成交笔数': 1,
            '全站成交金额': 1,
        }
        cjzb_qzt = self.tg_cjzb_qzt(projection=projection, is_maximize=True)
        if len(cjzb_qzt) > 0:
            cjzb_qzt.rename(columns={
                '场景名字': '营销场景',
                '全站花费': '花费',
                '全站观看次数': '展现量',
                '全站宝贝点击量': '点击量',
                '全站成交笔数': '成交笔数',
                '全站成交金额': '成交金额',
            }, inplace=True)
            cjzb_qzt = cjzb_qzt.groupby(
                    ['日期', '店铺名称', '场景id', '营销场景'],
                    as_index=False).agg(
                    **{
                        '花费': ('花费', np.max),
                        '展现量': ('展现量', np.max),
                        '点击量': ('点击量', np.max),
                        '成交笔数': ('成交笔数', np.max),
                        '成交金额': ('成交金额', np.max)
                    }
                )
            for col in df.columns.tolist():
                if col not in cjzb_qzt.columns.tolist():
                    cjzb_qzt[col] = 0
            df = pd.concat([df, cjzb_qzt], ignore_index=True)
        df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
        df = df.groupby(
            ['日期', '店铺名称', '营销场景'],
            as_index=False).agg(
            **{
                '花费': ('花费', np.sum),
                '展现量': ('展现量', np.sum),
                '点击量': ('点击量', np.sum),
                '加购量': ('加购量', np.sum),
                '成交笔数': ('成交笔数', np.sum),
                '成交金额': ('成交金额', np.sum)
            }
        )
        df.sort_values(['日期', '店铺名称', '花费'], ascending=[False, False, False], ignore_index=True, inplace=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '营销场景']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def aikucun_bd_spu(self, db_name='聚合数据', table_name='爱库存_商品spu榜单'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '平台': 1,
            '店铺名称': 1,
            'spuid': 1,
            '商品名称': 1,
            '品牌名': 1,
            '商品款号': 1,
            '一级类目名称': 1,
            '二级类目名称': 1,
            '三级类目名称': 1,
            '转发次数': 1,
            '转发爱豆人数': 1,
            '访客量': 1,
            '浏览量': 1,
            '下单gmv': 1,
            '成交gmv': 1,
            '供货额': 1,
            '供货价': 1,
            '销售爱豆人数': 1,
            '支付人数_交易': 1,
            '支付人数_成交': 1,
            '销售量_成交': 1,
            '销售量_交易': 1,
            '订单数_成交': 1,
            '订单数_交易': 1,
            '成交率_交易': 1,
            '成交率_成交': 1,
            '可售库存数': 1,
            '售罄率': 1,
            '在架sku数': 1,
            '可售sku数': 1,
            '下单sku数': 1,
            '成交sku数': 1,
            '图片': 1,
            '更新时间': 1,
        }
        projection = {}
        df = self.download_manager.data_to_df(
            db_name='爱库存2',
            table_name='爱库存_spu榜单',
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        idx = df.groupby(['日期', '店铺名称', 'spuid'])['更新时间'].idxmax()
        df = df.loc[idx]
        # 调整列顺序, 定义需要前置的列
        cols_to_move = ['日期','平台','店铺名称','品牌名','商品名称', '商品款号','spuid', '一级类目名称', '二级类目名称', '三级类目名称']
        # 生成新的列顺序：前置列 + 剩余列（保持原顺序）
        new_columns = cols_to_move + [col for col in df.columns if col not in cols_to_move]
        # 调整DataFrame列顺序
        df = df[new_columns]
        df['更新时间'] = df.pop('更新时间')
        df = df.astype({'日期': 'datetime64[ns]'}, errors='ignore')
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '商品款号', 'spuid']],  # 唯一约束列表
        }

    @upload_data_decorator()
    def deeplink(self, db_name='聚合数据', table_name='达摩盘_deeplink人群洞察'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {}
        df = self.download_manager.data_to_df(
            db_name='达摩盘3',
            table_name='店铺deeplink人群洞察',
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        df.drop_duplicates(subset=['日期', '人群类型', '店铺名称', '人群规模', '广告投入金额'], keep='last', inplace=True, ignore_index=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '人群类型', '店铺名称', '人群规模']],  # 唯一约束列表
        }

    @upload_data_decorator()
    def global_insights(self, db_name='聚合数据', table_name='全域洞察'):
        start_date, end_date = self.months_data(num=self.months)
        exclude_projection = ['日期', '结束日期', '在投计划数', 'bizcode', 'channeltype', 'urlonebp', '渠道策略']
        __res = []
        for year in range(2025, datetime.datetime.today().year + 1):
            df_global = self.download_manager.data_to_df(
                db_name='达摩盘3',
                table_name=f'全域洞察_{year}',
                start_date=start_date,
                end_date=end_date,
                projection={},
                exclude_projection=exclude_projection,
                date_column='起始日期',
            )
            __res.append(df_global)
        df = pd.concat(__res, ignore_index=True)
        if len(df) == 0:
            return None, None
        df.rename(columns={'起始日期': '日期'}, inplace=True)

        # df.drop_duplicates(subset=['日期', '店铺名称', '场景id', '父渠道id'], keep='last', inplace=True, ignore_index=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '场景id', '父渠道id']],  # 唯一约束列表
        }

    # @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def dmp_crowd(self, db_name='聚合数据', table_name='达摩盘_人群报表'):
        start_date, end_date = self.months_data(num=self.months)
        projection = {
            '日期': 1,
            '人群id': 1,
            '人群规模': 1,
            '用户年龄': 1,
            '消费能力等级': 1,
            '用户性别': 1,
        }
        df_crowd = self.download_manager.data_to_df(
            db_name='达摩盘3',
            table_name='我的人群属性',
            start_date=start_date,
            end_date=end_date,
            projection=projection,
        )
        df_crowd.sort_values('日期', ascending=True, ignore_index=True, inplace=True)
        df_crowd.drop_duplicates(subset=['人群id',], keep='last', inplace=True, ignore_index=True)
        df_crowd.pop('日期')
        df_crowd = df_crowd.astype({'人群id': 'int64'}, errors='ignore')
        projection = {}
        __res = []
        for year in range(2024, datetime.datetime.today().year + 1):
            df_dmp = self.download_manager.data_to_df(
                        db_name='达摩盘3',
                        table_name=f'dmp人群报表_{year}',
                        start_date=start_date,
                        end_date=end_date,
                        projection=projection,
                    )
            __res.append(df_dmp)
        df_dmp = pd.concat(__res, ignore_index=True)
        df_dmp = df_dmp.astype({'人群id': 'int64'}, errors='ignore')
        df_dmp.sort_values('日期', ascending=True, ignore_index=True, inplace=True)
        df_dmp.drop_duplicates(subset=['日期', '人群id', '消耗_元'], keep='last', inplace=True, ignore_index=True)
        df = pd.merge(df_dmp, df_crowd, left_on=['人群id'], right_on=['人群id'], how='left')
        # 清除一些不必要的字符
        df['用户年龄'] = df['用户年龄'].apply(lambda x: '~'.join(re.findall(r'^(\d+).*-(\d+)岁$', str(x))[0]) if '岁' in str(x) else x)
        df['消费能力等级'] = df['消费能力等级'].apply(lambda x: f'L{''.join(re.findall(r'(\d)', str(x)))}' if '购买力' in str(x) else x)
        df.rename(columns={'消耗_元': '消耗'}, inplace=True)
        set_typ = SET_TYP_DICT[f'{db_name}_{table_name}']
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '人群id', '营销渠道', '计划基础信息', '推广单元信息']],  # 唯一约束列表
        }

    @error_handler.log_on_exception(logger=logger)
    def ret_keyword(self, keyword, as_file=False):
        """ 推广关键词报表，关键词分类， """
        datas = [
            {
                '类别': '品牌词',
                '值': [
                    '万里马',
                    'wanlima',
                    'fion',
                    '菲安妮',
                    '迪桑娜',
                    'dissona',
                    'hr',
                    'vh',
                    'songmont',
                    'vanessahogan',
                    'dilaks',
                    'khdesign',
                    'peco',
                    'giimmii',
                    'cassile',
                    'grotto',
                    'why',
                    'roulis',
                    'lesschic',
                    'amazing song',
                    'mytaste',
                    'bagtree',
                    '红谷',
                    'hongu',
                ]
            },
            {
                '类别': '智选',
                '值': [
                    '智选',
                ]
            },
            {
                '类别': '智能',
                '值': [
                    '智能',
                ]
            },
            {
                '类别': '年份',
                '值': [
                    '20',
                ]
            },
            {
                '类别': '材质',
                '值': [
                    '皮',
                    '牛仔',
                    '丹宁',
                    '帆布',
                ]
            },
            {
                '类别': '季节',
                '值': [
                    '春',
                    '夏',
                    '秋',
                    '冬',
                ]
            },
            {
                '类别': '一键起量',
                '值': [
                    '一键起量',
                ]
            },
            {
                '类别': '款式',
                '值': [
                    '水桶',
                    '托特',
                    '腋下',
                    '小方',
                    '通用款',
                    '手拿',
                    '马鞍',
                    '链条',
                    '菜篮',
                    'hobo',
                    '波士顿',
                    '凯莉',
                    '饺子',
                    '盒子',
                    '牛角',
                    '公文',
                    '月牙',
                    '单肩',
                    '枕头',
                    '斜挎',
                    '手提',
                    '手拎',
                    '拎手',
                    '斜肩',
                    '棒球',
                    '饺包',
                    '保龄球',
                    '戴妃',
                    '半月',
                    '弯月',
                    '法棍',
                    '流浪',
                    '拎包',
                    '中式',
                    '手挽',
                    '皮带',
                    '眼镜',
                    '斜跨',
                    '律师',
                    '斜背',
                ]
            },
            {
                '类别': '品类词',
                '值': [
                    '老花',
                    '包包',
                    '通勤',
                    '轻奢',
                    '包',
                    '新款',
                    '小众',
                    '爆款',
                    '工作',
                    '精致',
                    '奢侈',
                    '袋',
                    '腰带',
                    '裤带',
                    '女士',
                    '复古',
                    '高级',
                    '容量',
                    '时尚',
                    '商务',
                ],
            },
        ]
        result = ''
        res = []
        is_continue = False
        for data in datas:
            for item in data['值']:
                if item == '20':
                    pattern = r'\d\d'
                    res = re.findall(f'{item}{pattern}', str(keyword), re.IGNORECASE)
                else:
                    res = re.findall(item, str(keyword), re.IGNORECASE)
                if res:
                    result = data['类别']
                    is_continue = True
                    break
            if is_continue:
                break
        return result

    @error_handler.log_on_exception(logger=logger)
    def set_crowd(self, keyword, as_file=False):
        """ 推广人群报表，人群分类， """
        result_a = re.findall('_a$|_a_|_ai|^a_', str(keyword), re.IGNORECASE)
        result_i = re.findall('_i$|_i_|^i_', str(keyword), re.IGNORECASE)
        result_p = re.findall('_p$|_p_|_pl|^p_||^pl_', str(keyword), re.IGNORECASE)
        result_l = re.findall('_l$|_l_|^l_', str(keyword), re.IGNORECASE)
        datas = [
            {
                '类别': 'A',
                '值': result_a,
            },
            {
                '类别': 'I',
                '值': result_i,
            },
            {
                '类别': 'P',
                '值': result_p,
            },
            {
                '类别': 'L',
                '值': result_l,
            }
        ]
        is_res = False
        for data in datas:
            if data['值']:
                data['值'] = [item for item in data['值'] if item != '']
                if data['值']:
                    return data['类别']
        if not is_res:
            return ''

    @error_handler.log_on_exception(logger=logger)
    def set_crowd2(self, keyword, as_file=False):
        """ 推广人群报表，人群分类， """
        datas = [
            {
                '类别': 'A',
                '值': [
                    '相似宝贝',
                    '相似店铺',
                    '类目',
                    '88VIP',
                    '拉新',
                    '潮流',
                    '会场',
                    '意向',
                    '>>',  # 系统推荐的搜索相关人群
                    '关键词：',  # 系统推荐的搜索相关人群
                    '关键词_',  # 自建的搜索相关人群
                    '扩展',
                    '敏感人群',
                    '尝鲜',
                    '小二推荐',
                    '竞争',
                    '资深',
                    '女王节',
                    '本行业',
                    '618',
                    '包包树',
                    '迪桑娜',
                    '菲安妮',
                    '卡思乐',
                    '场景词',
                    '竞对',
                    '精选',
                    '发现',
                    '行业mvp'
                    '特征继承',
                    '机会',
                    '推荐',
                    '智能定向',
                    'AI',
                ]
            },
            {
                '类别': 'I',
                '值': [
                    '行动',
                    '收加',
                    '收藏',
                    '加购',
                    '促首购',
                    '店铺优惠券',
                    '高转化',
                    '认知',
                    '喜欢我',  # 系统推荐宝贝/店铺访问相关人群
                    '未购买',
                    '种草',
                    '兴趣',
                    '本店',
                    '领券',
                ]
            },
            {
                '类别': 'P',
                '值': [
                    '万里马',
                    '购买',
                    '已购',
                    '促复购'
                    '店铺会员',
                    '店铺粉丝',
                    '转化',
                ]
            },
            {
                '类别': 'L',
                '值': [
                    'L人群',
                ]
            },
        ]
        result = ''
        res = []
        is_continue = False
        for data in datas:
            for item in data['值']:
                res = re.findall(item, str(keyword), re.IGNORECASE)
                if res:
                    result = data['类别']
                    is_continue = True
                    break
            if is_continue:
                break
        return result

    # @error_handler.log_on_exception(logger=logger)
    @upload_data_decorator()
    def performance_concat(self, db_name, table_name, bb_tg=True):
        tg = [item['数据主体'] for item in self.pf_datas if item['集合名称'] == '天猫汇总表调用'][0]
        zb = [item['数据主体'] for item in self.pf_datas if item['集合名称'] == '天猫_超级直播'][0]
        pxb = [item['数据主体'] for item in self.pf_datas if item['集合名称'] == '天猫_品销宝账户报表'][0]
        zb = zb.groupby(['日期', '店铺名称', '推广渠道', '营销场景'], as_index=False).agg(
            **{
                '花费': ('花费', np.sum),
                '展现量': ('展现量', np.sum),
                '观看次数': ('观看次数', np.sum),
                '加购量': ('加购量', np.sum),
                '成交笔数': ('成交笔数', np.sum),
                '成交金额': ('成交金额', np.sum),
                '直接成交笔数': ('直接成交笔数', np.sum),
                '直接成交金额': ('直接成交金额', np.sum),
            }
        )
        pxb = pxb.groupby(['日期', '店铺名称', '推广渠道', '营销场景'], as_index=False).agg(
            **{
                '花费': ('花费', np.sum),
                '展现量': ('展现量', np.sum),
                '点击量': ('点击量', np.sum),
                '加购量': ('加购量', np.sum),
                '成交笔数': ('成交笔数', np.sum),
                '成交金额': ('成交金额', np.sum)
            }
        )
        zb.rename(columns={
            '观看次数': '点击量',
        }, inplace=True)
        zb.fillna(0, inplace=True)  # astype 之前要填充空值
        tg.fillna(0, inplace=True)
        zb = zb.astype({
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
        }, errors='raise')
        tg = tg.astype({
            '商品id': str,
            '花费': 'float64',
            '展现量': 'int64',
            '点击量': 'int64',
            '加购量': 'int64',
            '成交笔数': 'int64',
            '成交金额': 'float64',
            '直接成交笔数': 'int64',
            '直接成交金额': 'float64',
            '自然流量曝光量': 'int64',
        }, errors='raise')
        df = pd.concat([tg, zb, pxb], axis=0, ignore_index=True)
        df.fillna(0, inplace=True)  # concat 之后要填充空值
        df = df.astype({
            '商品id': str,
            '自然流量曝光量': 'int64',
            })
        df.replace(to_replace='', value=0, inplace=True)
        set_typ = {
            '日期': 'date',
            '店铺名称': 'varchar(255)',
            '推广渠道': 'varchar(100)',
            '营销场景': 'varchar(100)',
            '商品id': 'bigint',
            '花费': 'decimal(12,2)',
            '展现量': 'int',
            '点击量': 'int',
            '加购量': 'int',
            '成交笔数': 'int',
            '成交金额': 'decimal(12,2)',
            '直接成交笔数': 'int',
            '直接成交金额': 'decimal(12,2)',
            '自然流量曝光量': 'int',
        }
        df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')
        return df, {
            'db_name': db_name,
            'table_name': table_name,
            'set_typ': set_typ,
            'primary_keys': [],  # 创建唯一主键
            'check_duplicate': False,  # 检查重复数据
            'duplicate_columns': [],  # 指定排重的组合键
            'update_on_duplicate': True,  # 更新旧数据
            'allow_null': False,  # 允许插入空值
            'partition_by': None,  # 分表方式
            'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
            'indexes': [],  # 普通索引列
            'transaction_mode': 'batch',  # 事务模式
            'unique_keys': [['日期', '店铺名称', '推广渠道', '营销场景', '商品id']],  # 唯一约束列表
        }


def get_day_of_month(num):
    """
    num: 获取n月以前的第一天和最后一天, num=0时, 返回当月第一天和最后一天
    """
    _today = datetime.date.today()
    months_ago = _today - relativedelta(months=num)  # n 月以前的今天
    _, _lastDay = calendar.monthrange(months_ago.year, months_ago.month)  # 返回月的第一天的星期和当月总天数
    _firstDay = datetime.date(months_ago.year, months_ago.month, day=1).strftime('%Y-%m-%d')
    _lastDay = datetime.date(months_ago.year, months_ago.month, day=_lastDay).strftime('%Y-%m-%d')
    return _firstDay, _lastDay


@upload_data_decorator()
def date_table():
    """
    生成 pbix 使用的日期表
    """
    start_date = '2022-01-07'  # 日期表的起始日期
    yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
    dic = pd.date_range(start=start_date, end=yesterday)
    df = pd.DataFrame(dic, columns=['日期'])
    df.sort_values('日期', ascending=True, ignore_index=True, inplace=True)
    df.reset_index(inplace=True)
    # inplace 添加索引到 df
    p = df.pop('index')
    df['月2'] = df['日期']
    df['月2'] = df['月2'].dt.month
    df['日期'] = df['日期'].dt.date  # 日期格式保留年月日，去掉时分秒
    df['年'] = df['日期'].apply(lambda x: str(x).split('-')[0] + '年')
    df['月'] = df['月2'].apply(lambda x: str(x) + '月')
    # df.drop('月2', axis=1, inplace=True)
    mon = df.pop('月2')
    df['日'] = df['日期'].apply(lambda x: str(x).split('-')[2])
    df['年月'] = df.apply(lambda x: x['年'] + x['月'], axis=1)
    df['月日'] = df.apply(lambda x: x['月'] + x['日'] + '日', axis=1)
    df['第n周'] = df['日期'].apply(lambda x: x.strftime('第%W周'))

    # 重构 df，添加 1 列，从周五～下周四作为 1 周 汇总
    df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')  # 转换日期列
    grouped = df.groupby(pd.Grouper(key='日期', freq='7D'))
    __res = []
    num = 1
    for name, group in grouped:
        if num > 52:
            num = 1
        group['第n周_new'] = f'第{num}周'
        num += 1
        __res.append(group.copy())
    df = pd.concat(__res, ignore_index=True)
    df['weekname'] = df['日期'].dt.day_name()
    dict_dt = {
        'Monday': '星期一',
        'Tuesday': '星期二',
        'Wednesday': '星期三',
        'Thursday': '星期四',
        'Friday': '星期五',
        'Saturday': '星期六',
        'Sunday': '星期日',
    }
    df['星期'] = df['weekname'].apply(lambda x: dict_dt[x])
    df['索引'] = p
    df['月索引'] = mon
    df.sort_values('日期', ascending=False, ignore_index=True, inplace=True)
    df = df.reset_index(drop=True)
    df = df.reset_index(drop=False)
    df.rename(columns={'index': 'id'}, inplace=True)
    df['id'] = df['id'].apply(lambda x: x + 1)
    set_typ = SET_TYP_DICT['聚合数据_日期表']
    return df, {
        'db_name': '聚合数据',
        'table_name': '日期表',
        'set_typ': set_typ,
        'primary_keys': [],  # 创建唯一主键
        'check_duplicate': False,  # 检查重复数据
        'duplicate_columns': [],  # 指定排重的组合键
        'update_on_duplicate': True,  # 更新旧数据
        'allow_null': False,  # 允许插入空值
        'partition_by': None,  # 分表方式
        'partition_date_column': '日期',  # 用于分表的日期列名，默认为'日期'
        'indexes': [],  # 普通索引列
        'transaction_mode': 'batch',  # 事务模式
        'unique_keys': [['日期']],  # 唯一约束列表
    }


def query1(months=1, download_manager=None):
    sdq = MysqlDatasQuery(download_manager=download_manager)  # 实例化数据处理类
    sdq.months = months  # 设置数据周期， 1 表示近 2 个月
    # 依赖表  -- >>
    sdq.tg_wxt(db_name='聚合数据', table_name='天猫_主体报表')
    sdq.tg_cjzb(db_name='聚合数据', table_name='天猫_超级直播')
    sdq.pxb_zh(db_name='聚合数据', table_name='天猫_品销宝账户报表')
    # 依赖表  << --

    sdq.syj(db_name='聚合数据', table_name='生意经_宝贝指标')
    sdq.idbm(db_name='聚合数据', table_name='商品id编码表')
    sdq.sp_picture(db_name='聚合数据', table_name='商品id图片对照表')
    sdq.sp_cost(db_name='聚合数据', table_name='商品成本')
    sdq.jdjzt(db_name='聚合数据', table_name='京东_京准通')
    sdq.sku_sales(db_name='聚合数据', table_name='京东_sku_商品明细')

    sdq._ald_wxt(db_name='聚合数据', table_name='奥莱店_主体报表')
    sdq._sj_wxt(db_name='聚合数据', table_name='圣积天猫店_主体报表')
    sdq._tb_wxt(db_name='聚合数据', table_name='淘宝_主体报表')
    sdq.jdqzyx(db_name='聚合数据', table_name='京东_京准通_全站营销')
    sdq.spu_sales(db_name='聚合数据', table_name='京东_spu_商品明细')
    sdq.zb_ccfx(db_name='聚合数据', table_name='生意参谋_直播场次分析')
    sdq.tg_by_day(db_name='聚合数据', table_name='多店推广场景_按日聚合')
    sdq.performance_concat(bb_tg=False, db_name='聚合数据', table_name='天猫_推广汇总')  # _推广商品销售


def query2(months=1, download_manager=None):
    sdq = MysqlDatasQuery(download_manager=download_manager)  # 实例化数据处理类
    sdq.months = months  # 设置数据周期， 1 表示近 2 个月
    sdq.dplyd(db_name='聚合数据', table_name='店铺流量来源构成')
    sdq.tg_rqbb(db_name='聚合数据', table_name='天猫_人群报表')
    sdq.tg_gjc(db_name='聚合数据', table_name='天猫_关键词报表')
    sdq.jd_gjc(db_name='聚合数据', table_name='京东_关键词报表')
    sdq.se_search(db_name='聚合数据', table_name='天猫店铺来源_手淘搜索')
    # sdq.aikucun_bd_spu(db_name='聚合数据', table_name='爱库存_商品spu榜单')
    sdq.dmp_crowd(db_name='聚合数据', table_name='达摩盘_人群报表')
    sdq.deeplink(db_name='聚合数据', table_name='达摩盘_deeplink人群洞察')
    sdq.global_insights(db_name='聚合数据', table_name='全域洞察')


def query3(months=1, download_manager=None):
    sdq = MysqlDatasQuery(download_manager=download_manager)  # 实例化数据处理类
    sdq.months = months  # 设置数据周期， 1 表示近 2 个月
    sdq.spph(db_name='聚合数据', table_name='天猫_商品排行')
    sdq.item_up(db_name='聚合数据', table_name='淘宝店铺货品')


def main(months=3):
    logger.info('数据聚合任务开始')
    # 1. 更新日期表  更新货品年份基准表， 属性设置 3 - 货品年份基准
    date_table()
    # 2. 数据聚合
    db_config = {
        'username': username,
        'password': password,
        'host': host,
        'port': int(port),
        'pool_size': 20,
        'mincached': 5,
        'maxcached': 10,
    }
    with s_query.QueryDatas(**db_config) as download_manager:
        query1(download_manager=download_manager, months=months)
        query2(download_manager=download_manager, months=months)
        query3(download_manager=download_manager, months=months)
    
    logger.info('数据聚合完成')


if __name__ == '__main__':
    # main(months=3)
    pass

    download_manager = s_query.QueryDatas(
        username=username, 
        password=password, 
        host=host, 
        port=int(port),
        pool_size=10,
        )
    sdq = MysqlDatasQuery(download_manager=download_manager) 
    sdq.months = 1
    sdq.shops_concat(db_name='聚合数据', table_name='多店聚合_日报')
