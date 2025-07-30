from datetime import datetime
from sqlalchemy import func
from clickhouse_sqlalchemy import Table, engines, types, make_session
from clickhouse_driver import errors as ch_errors

class CHDB:
    def __init__(self, ch_session, default_time_field='time'):
        self.db = ch_session
        self.default_time_field = default_time_field

    def apply_filters(self, query, model, params):
        # 这里只做简单的等值和时间范围过滤
        time_field_name = params.get('_time', self.default_time_field)
        time_field = getattr(model.c, time_field_name, None)

        if 'startTime' in params and time_field is not None:
            start = datetime.strptime(params['startTime'], '%Y-%m-%d %H:%M:%S')
            query = query.where(time_field >= start)
        if 'endTime' in params and time_field is not None:
            end = datetime.strptime(params['endTime'], '%Y-%m-%d %H:%M:%S')
            query = query.where(time_field <= end)

        for key, value in params.items():
            if key in ['startTime', 'endTime', '_start', '_count', '_order', '_by', '_time']:
                continue
            col = getattr(model.c, key, None)
            if col is not None:
                # 支持简单等值过滤，ClickHouse不支持复杂join过滤
                query = query.where(col == value)
        return query

    def fetch_all_by(self, model, params):
        """
        ClickHouse不支持join复杂关联，功能简化：
        支持简单字段过滤、时间过滤、排序、分页
        """
        query = model.select()

        query = self.apply_filters(query, model, params)

        # 排序
        if '_order' in params and '_by' in params:
            _order = params['_order'].lower()
            _by = params['_by']
            col = getattr(model.c, _by, None)
            if col is not None:
                query = query.order_by(col.asc() if _order == 'asc' else col.desc())

        # 分页
        if '_start' in params and '_count' in params:
            start = int(params['_start'])
            count = int(params['_count'])
            query = query.limit(count).offset(start)

        try:
            result = self.db.execute(query).fetchall()
            # 返回字典列表
            keys = result[0].keys() if result else []
            result_dict = []
            for row in result:
                d = {}
                for key in keys:
                    val = row[key]
                    if isinstance(val, datetime):
                        d[key] = val.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        d[key] = val
                result_dict.append(d)
            return result_dict

        except ch_errors.Error as e:
            raise ValueError(f"查询失败: {str(e)}") from e

    def insert_data(self, model, data):
        """
        插入数据，自动生成id
        """
        from uuid import uuid4
        if 'id' not in data:
            data['id'] = str(uuid4())
        ins = model.insert().values(**data)
        try:
            self.db.execute(ins)
            self.db.commit()
            return data['id']
        except ch_errors.Error as e:
            self.db.rollback()
            raise ValueError(f"插入失败: {str(e)}") from e

    def delete_by_id(self, model, record_id):
        """
        ClickHouse 不支持 DELETE 操作，通常通过 TTL 或替换表实现软删除
        此处抛异常提醒
        """
        raise NotImplementedError("ClickHouse 不支持 DELETE 操作")

    def update_by_id(self, model, record_id, update_data):
        """
        ClickHouse 不支持 UPDATE，推荐插入新版本数据或使用替换表
        此处抛异常提醒
        """
        raise NotImplementedError("ClickHouse 不支持 UPDATE 操作")
