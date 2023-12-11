import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
from matplotlib.font_manager import fontManager
from matplotlib.lines import Line2D
import streamlit as st

def adding_coordinates(uploaded_file):
    df = pd.read_excel(uploaded_file)
    if '書名' in df.columns:
        have_book_name = True
        df_1 = pd.read_excel('愛如生方志庫書目（添加時代和坐標）.xlsx')
        df1_dict = df_1.set_index('書名')[['時代作者', '版本', '時間段', '地域','X', 'Y', 'sys_id', 'uri']].to_dict(orient='index')
        def get_infor(x):
            return df1_dict.get(x, {'時代作者': None, '版本': None, '時間段': None, '地域': None, 'X': None, 'Y': None,  'sys_id': None, 'uri': None}) 
        df[['時代作者', '版本', '時間段', '地域','X', 'Y', 'sys_id', 'uri']] = df['書名'].apply(get_infor).apply(pd.Series) 
    else:
        have_book_name = False
        st.warning("xlsx文件中需要有“書名”列！")
    return df ,have_book_name
    

def plot_map(df, map_title,alpha=1):
    # 設置中文字體
    current_directory = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_directory, 'SimHei.ttf')
    fontManager.addfont(font_path) 
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.rcParams['axes.unicode_minus']=False

    # 讀取底圖 shapefile 文件  
    base_map_path = '省.shp'
    base_map = gpd.read_file(base_map_path)

    # 讀取 XY 數據
    xy_df = df.drop_duplicates(subset=['書名'])
    

    # 創建 Point
    geometry = [Point(xy) for xy in zip(xy_df['X'], xy_df['Y'])]

    # 創建 Geopandas GeoDataFrame
    points_gdf = gpd.GeoDataFrame(xy_df, geometry=geometry, crs=base_map.crs) # crs：坐標參考系統（Coordinate Reference System）

    # 定義不同時代的顏色和順序，並進行排序
    time_periods_order = ['秦漢', '魏晉南北朝','隋唐五代', '宋', '元', '明', '清', '民國']
    reversed_time_periods_order = time_periods_order[::-1]

    colors = {'秦漢': 'yellow', '魏晉南北朝': 'purple', '隋唐五代': 'orange', '宋': 'cyan', '元': 'magenta', '明': 'green',
              '清': 'red', '民國': 'blue'}

    # 繪製底圖
    fig, ax = plt.subplots(figsize=(10, 8))
    base_map.plot(ax=ax, color='silver', edgecolor='white')  # 修改地圖背景顏色和邊界顏色

    # 根據時代分組倒序繪製不同顏色點，以免後面的朝代覆蓋前面的朝代
    for time_period in reversed_time_periods_order:
        if time_period in points_gdf['時間段'].unique():
            group = points_gdf[points_gdf['時間段'] == time_period]
            ax.scatter(group['geometry'].x, group['geometry'].y, color=colors.get(time_period, 'black'), s=20, label=time_period, alpha=alpha)

    # 顯示圖例
    legend_elements = [Line2D([0], [0], marker='o', color='w', label=time_period, markersize=7, markerfacecolor=colors.get(time_period, 'black')) for time_period in time_periods_order if time_period in points_gdf['時間段'].unique()]
    legend = ax.legend(handles=legend_elements, loc='lower right')

    # 調整圖例位置
    legend.set_bbox_to_anchor((1.0, 0.25)) 
    legend.set_title('時代', prop={'size': 12})

    plt.title(f'“{map_title}”空間分佈圖')
    st.pyplot(fig)
    #呈現df
    df = df[['書名', '時代作者', '版本', '時間段', '地域','X', 'Y', 'sys_id', 'uri']]
    st.dataframe(df)

def main():
    st.title("繪製古代地方志地圖")
    st.write('輸入包含地方志書名的xlsx文件自動繪製地圖，地圖標題是文件名。')
    st.write('注意：（1）xlsx文件中需要有“書名”列；（2）衹能繪製愛如生方志庫書目中的地方志地圖，方志名保持愛如生數據庫的原樣。例如“（乾隆）湖南通志174卷”。')
    # 添加文件上傳器
    uploaded_file = st.file_uploader("請上傳xlsx文件:", type="xlsx")
    # 設置透明度
    alpha_values = [i / 10 for i in range(11)]  # 0.0 到 1.0，步長爲0.1
    alpha = st.select_slider("設置坐標點透明度（調低透明度可看見被覆蓋的重疊區域）：", options=alpha_values, value=1.0)
    # 檢查上傳的文件
    if uploaded_file is not None:
        file_name = os.path.splitext(uploaded_file.name)[0]
        df, have_book_name = adding_coordinates(uploaded_file)
        if have_book_name:
            plot_map(df, file_name, alpha=alpha)

if __name__ == "__main__":
    main()