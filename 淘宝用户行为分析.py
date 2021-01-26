import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

data=pd.read_csv('tianchi.csv')
#data.isnull().sum()

#拆分数据集,将时间分开
data['date']=data['time'].map(lambda s: re.compile(' ').split(s)[0])
data['hour']=data['time'].map(lambda s: re.compile(' ').split(s)[1])
data['date']=pd.to_datetime(data['date'])
data['time']=pd.to_datetime(data['time'])
data['hour']=data['hour'].astype('int64')



data=data.sort_values(by='time',ascending=True).reset_index()
data=data.drop('index',axis=1)

data.describe()

#PV(访问量)：即Page View, 具体是指网站的是页面浏览量或者点击量，页面被刷新一次就计算一次。
#UV(独立访客)：即Unique Visitor,访问您网站的一台电脑客户端为一个访客。


#每天访问量分析
#pv值计算网页每一天的被访问量，uv值计算每一天访问的用户数量
pv=data.groupby('date')['user_id'].count().reset_index().rename(columns={'user_id':'pv'})
uv=data.groupby('date')['user_id'].apply(lambda x:x.drop_duplicates().count()).reset_index().rename(columns={'user_id':'uv'})

fig,axes=plt.subplots(2,1,sharex=True)
pv.plot(x='date',y='pv',ax=axes[0])
uv.plot(x='date',y='uv',ax=axes[1])
axes[0].set_title('pv_daily')
axes[1].set_title('uv_daily')

#每个小时访问量分析
#pv_hour记录每小时用户操作次数，uv_hour记录每小时不同的上线用户数量
pv_hour=data.groupby('hour')['user_id'].count().reset_index().rename(columns={'user_id':'pv'})
uv_hour=data.groupby('hour')['user_id'].apply(lambda x:x.drop_duplicates().count()).reset_index().rename(columns={'user_id':'uv'})
fig,axes=plt.subplots(2,1,sharex=True)
pv_hour.plot(x='hour',y='pv',ax=axes[0])
uv_hour.plot(x='hour',y='uv',ax=axes[1])
axes[0].set_title('pv_hour')
axes[1].set_title('uv_hour')

#不同行为类型用户pv分析
pv_detail=data.groupby(['behavior_type','hour'])['user_id'].count().reset_index().rename(columns={'user_id':'total_pv'})
fig,axes=plt.subplots(2,1,sharex=True)
sns.pointplot(x='hour',y='total_pv',hue='behavior_type',data=pv_detail,ax=axes[0])
sns.pointplot(x='hour',y='total_pv',hue='behavior_type',data=pv_detail[pv_detail['behavior_type']!=1],ax=axes[1])
axes[0].set_title('pv_different_behavior_type')
axes[1].set_title('pv_different_behavior_type_except1')

#用户购买次数情况分析
data_user_buy=data[data['behavior_type']==4].groupby('user_id')['behavior_type'].count()
sns.distplot(data_user_buy,kde=False)
plt.title('daily_user_buy')


#总体人均消费次数=消费总次数/消费人数
data_use_buy1=data[data['behavior_type']==4].groupby(['date','user_id'])['behavior_type'].count().reset_index().rename(columns={'behavior_type':'total'})
data_use_buy1.groupby('date').apply(lambda x:x.total.sum()/x.total.count()).plot()
plt.title('daily_ARPPU')
#或者按照如下操作
x=data_use_buy1.groupby('date')['total'].count().reset_index()
y=data_use_buy1.groupby('date')['total'].sum().reset_index()
average=pd.DataFrame(y['total']/x['total'])
plt.figure(figsize=(20,6))
plt.plot(x['date'],average['total'],'bo-')
plt.xticks(x['date'],rotation=45)

#活跃用户数平均消费次数=活跃用户的消费总次数/活跃用户人数(每天有操作行为的为活跃)
data['operation']=1
data_use_buy2=data.groupby(['date','user_id','behavior_type'])['operation'].count().reset_index().rename(columns={'operation':'total'})
data_use_buy2.groupby('date').apply(lambda x:x[x.behavior_type==4].total.sum()/len(x.user_id.unique())).plot()
plt.title('daily_ARPU')

#付费率=消费人数/活跃用户人数
data_use_buy2.groupby('date').apply(lambda x:x[x.behavior_type==4].total.count()/len(x.user_id.unique())).plot()
plt.title('daily_afford_rate')

#同一时间段用户消费次数分布
data_user_buy3=data[data.behavior_type==4].groupby(['user_id','date','hour'])['operation'].sum().rename('buy_count')
sns.distplot(data_user_buy3)
print('大多数用户消费：{}次'.format(data_user_buy3.mode()[0]))


#复购情况，即两天以上有购买行为,一天多次购买算一次;复购率=有复购行为的用户数/有购买行为的用户总数
date_rebuy=data[data.behavior_type==4].groupby('user_id')['date'].apply(lambda x:len(x.unique())).rename('rebuy_count')
print('复购率:',round(date_rebuy[date_rebuy>=2].count()/date_rebuy.count(),4))

#或者如下操作
data_rebuy=data[data.behavior_type==4].groupby('user_id')['date'].count().to_frame().reset_index().rename(columns={'date':'rebuy'})
rebuy_rate=len(data_rebuy[data_rebuy.rebuy>=2]['user_id'])/len(data_rebuy['user_id']


#所有复购时间间隔消费次数分布
data_day_buy=data[data.behavior_type==4].groupby(['user_id','date']).operation.count().reset_index()
data_user_buy4=data_day_buy.groupby('user_id').date.apply(lambda x:x.sort_values().diff(1).dropna())
data_user_buy4=data_user_buy4.map(lambda x:x.days)
data_user_buy4.value_counts().plot(kind='bar')
plt.title('time_gap')
plt.xlabel('gap_day')
plt.ylabel('gap_count')


#漏斗分析是一套流程式数据分析，它能够科学反映用户行为状态以及从起点到终点各阶段用户转化率情况的重要分析模型。
data_user_count=data.groupby(['behavior_type']).count()
data_user_count.head()
pv_all=data['user_id'].count()
print(pv_all)



#用户行为与商品种类关系分析,不同用户行为类别的转化率
data_category=data[data.behavior_type!=2].groupby(['item_category','behavior_type']).operation.count().unstack(1).rename(columns={1:'点击量',3:'加入购物车量',4:'购买量'}).fillna(0)
data_category.head()






























