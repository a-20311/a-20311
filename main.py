import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide"
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

# 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)
    
    # 장르 전처리 (세로막대 기호 '|'로 구분된 첫 번째 장르만 추출)
    df['genre_clean'] = df['genre'].dropna().astype(str).apply(lambda x: x.split('|')[0])
    
    return df

df = load_data()

# ---------------------------------------------------------
# 첫 번째 그래프 구역: 장르별 영화 편수 (도넛 그래프)
# ---------------------------------------------------------
st.header("1. 장르별 영화 분포")

# 장르별 영화 편수 집계
genre_counts = df['genre_clean'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화 편수']

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    names='장르',
    values='영화 편수',
    hole=0.4,
    title="장르별 영화 편수 비율"
)

# 호버 툴팁 설정 (편수와 비율 표시)
fig1.update_traces(
    textinfo='percent+label',
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percent}"
)

# 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 설명 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write("박스오피스 상위권 영화 중 특정 장르(예: 드라마다 액션 등)가 차지하는 비중과 전체적인 장르 분포 다양성을 한눈에 파악할 수 있습니다.")
