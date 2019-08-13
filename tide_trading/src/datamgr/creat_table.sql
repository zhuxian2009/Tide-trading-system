CREATE DATABASE kdata;

CREATE TABLE t_kdata (
	id INT auto_increment  PRIMARY KEY,
	code CHAR(10) NOT NULL COMMENT '股票代码',
	trade_day CHAR(10) NOT NULL COMMENT '交易日期',
	open DECIMAL(10,2) NOT NULL COMMENT '开盘价',
	close DECIMAL(10,2) NOT NULL COMMENT '收盘价',
	high DECIMAL(10,2) NOT NULL COMMENT '最高价',
	low DECIMAL(10,2) NOT NULL COMMENT '最低价',
	amount DECIMAL(25,2) COMMENT '成交额(千元)',
	vol DECIMAL(25,2) COMMENT '成交量(手)',
	ma5vol DECIMAL(25,2)  COMMENT '5日平均成交量',
	ma10vol DECIMAL(25,2) COMMENT '10日平均成交量',
	ma20vol DECIMAL(25,2) COMMENT '20日平均成交量',
	ma30vol DECIMAL(25,2) COMMENT '30日平均成交量',
	ma5 DECIMAL(10,2) COMMENT '5日平均收盘价',
	ma10 DECIMAL(10,2) COMMENT '10日平均收盘价',
	ma20 DECIMAL(10,2) COMMENT '20日平均收盘价',
	ma30 DECIMAL(10,2) COMMENT '30日平均收盘价',
	ma60 DECIMAL(10,2) COMMENT '60日平均收盘价',
	pct_chg DECIMAL(10,2) COMMENT '涨跌幅',
	macd DECIMAL(10,3) COMMENT 'macd红绿柱',
	dea DECIMAL(10,3) COMMENT '讯号线dea',
	dif DECIMAL(10,3) COMMENT '差离值dif',
	UNIQUE KEY `UK_code`(`code`,`trade_day`)
)ENGINE=innodb DEFAULT CHARSET=utf8;

CREATE TABLE t_kdata_down (
	id INT auto_increment  PRIMARY KEY,
	code CHAR(10) NOT NULL COMMENT '股票代码',
	trade_day CHAR(10) NOT NULL COMMENT '交易日期',
	open DECIMAL(10,2) NOT NULL COMMENT '开盘价',
	close DECIMAL(10,2) NOT NULL COMMENT '收盘价',
	high DECIMAL(10,2) NOT NULL COMMENT '最高价',
	low DECIMAL(10,2) NOT NULL COMMENT '最低价',
	amount DECIMAL(25,2) COMMENT '成交额(千元)',
	vol DECIMAL(25,2) COMMENT '成交量(手)',
	ma5vol DECIMAL(25,2)  COMMENT '5日平均成交量',
	ma10vol DECIMAL(25,2) COMMENT '10日平均成交量',
	ma20vol DECIMAL(25,2) COMMENT '20日平均成交量',
	ma30vol DECIMAL(25,2) COMMENT '30日平均成交量',
	ma5 DECIMAL(10,2) COMMENT '5日平均收盘价',
	ma10 DECIMAL(10,2) COMMENT '10日平均收盘价',
	ma20 DECIMAL(10,2) COMMENT '20日平均收盘价',
	ma30 DECIMAL(10,2) COMMENT '30日平均收盘价',
	ma60 DECIMAL(10,2) COMMENT '60日平均收盘价',
	pct_chg DECIMAL(10,2) COMMENT '涨跌幅',
	macd DECIMAL(10,3) COMMENT 'macd红绿柱',
	dea DECIMAL(10,3) COMMENT '讯号线dea',
	dif DECIMAL(10,3) COMMENT '差离值dif',
	UNIQUE KEY `UK_code`(`code`,`trade_day`)
)ENGINE=innodb DEFAULT CHARSET=utf8;

#新增MACD指标字段macd dif dea
ALTER TABLE  t_kdata ADD macd DECIMAL(10,3) COMMENT 'macd红绿柱';
ALTER TABLE  t_kdata ADD dea DECIMAL(10,3) COMMENT '讯号线dea';
ALTER TABLE  t_kdata ADD dif DECIMAL(10,3) COMMENT '差离值dif';


CREATE TABLE t_trade_day (
	id INT auto_increment  PRIMARY KEY,
	trade_day CHAR(10) NOT NULL UNIQUE COMMENT '交易日期'
)ENGINE=innodb DEFAULT CHARSET=utf8;


CREATE TABLE t_stock_basic (
	id INT auto_increment  PRIMARY KEY,
	ts_code CHAR(10) NOT NULL UNIQUE COMMENT 'TS代码,如：000001.SZ',
	symbol CHAR(10) NOT NULL UNIQUE COMMENT '股票代码,如000001',
	name CHAR(40) NOT NULL COMMENT '股票名称',
	area CHAR(20) NOT NULL COMMENT '所在地域',
	market CHAR(20) NOT NULL COMMENT '市场类型 （主板/中小板/创业板）',
	list_status CHAR(10) NOT NULL COMMENT '上市状态： L上市 D退市 P暂停上市'
)ENGINE=innodb DEFAULT CHARSET=utf8;


#双底回测结果
CREATE TABLE t_backtest_wbottom (
	id INT auto_increment  PRIMARY KEY,
	ts_code CHAR(10) NOT NULL UNIQUE COMMENT 'TS代码,如：000001.SZ',
	bottom1 DECIMAL(10,3) COMMENT '底1',
	bottom2 DECIMAL(10,3) COMMENT '底2',
	trade_day1 CHAR(10) COMMENT '底1日期',
	trade_day2 CHAR(10) COMMENT '底2日期',
	trade_day CHAR(10) COMMENT '回测时的日期',
	minrange TINYINT  COMMENT '小区间的大小',
	UNIQUE KEY `UK_code`(`ts_code`,`trade_day1`,`trade_day2`)
)ENGINE=innodb DEFAULT CHARSET=utf8;

#热点概念
CREATE TABLE t_hot_consept (
	id INT auto_increment  PRIMARY KEY,
	consept CHAR(100) NOT NULL COMMENT '概念',
	times TINYINT NOT NULL COMMENT '命中次数',
	update_time CHAR(30) COMMENT '刷新时间'
)ENGINE=innodb DEFAULT CHARSET=utf8;

#清空表数据
truncate table t_kdata;
truncate table t_kdata_bak;

#删除表
DROP TABLE t_kdata;
DROP TABLE t_backtest_wbottom;
DROP TABLE t_kdata_bak;

#备份表
INSERT INTO t_kdata_bak SELECT * FROM t_kdata;


#查看数据库中表占用的内存空间
use information_schema;
select concat(round(sum(data_length/1024/1024),2),'MB') as data from tables where table_schema='kdata' and table_name='t_kdata';


#交换两列数据
update t_kdata as a, t_kdata as b set a.dea=b.

#统计去除重复项后，总行数
SELECT COUNT(DISTINCT code) FROM t_kdata_down;
+----------------------+
| COUNT(DISTINCT code) |
+----------------------+
|                 3649 |
+----------------------+
1 row in set (0.10 sec)

#删除某条记录
delete from t_kdata_down where trade_day='20190802';
delete from t_trade_day where trade_day='20190802';
select count(*) from t_kdata_down where code = '000001.SZ' and trade_day>='20190802' and trade_day<='20190802';
select open,close,high,low,vol,trade_day from t_kdata_down where code = '000001.SZ' and trade_day>=%s and trade_day<=%s order by trade_day ASC limit %s;
              