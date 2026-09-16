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
st.write("박스오피스 상위권 영화 중 특정 장르(예: 드라마, 액션 등)가 차지하는 비중과 전체적인 장르 분포 다양성을 한눈에 파악할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 두 번째 그래프 구역: 장르 및 영화별 총 관객 수 (트리맵)
# ---------------------------------------------------------
st.header("2. 장르 및 영화별 총 관객 수 분포")

# 트리맵에 표시하기 위해 데이터 결측치 처리
df_tree = df.dropna(subset=['genre_clean', 'movieNm', 'total_audi']).copy()

# Plotly 트리맵 생성 (계층 구조: 장르 -> 영화명, 크기: total_audi)
fig2 = px.treemap(
    df_tree,
    path=[px.Constant("전체 장르"), 'genre_clean', 'movieNm'],
    values='total_audi',
    title="장르 및 영화별 총 관객 수 트리맵"
)

# 호버 툴팁 설정 (영화명 및 총 관객 수 표시)
fig2.update_traces(
    hovertemplate="<b>%{label}</b><br>총 관객 수: %{value:,}명"
)

# 그래프 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 설명 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write("각 장르가 전체 관객 수에서 차지하는 비중뿐만 아니라, 특정 장르 내에서 어떤 영화가 흥행을 주도했는지(관객 수 규모)를 직관적으로 비교할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 세 번째 그래프 구역: 총 관객 수 분포 (히스토그램)
# ---------------------------------------------------------
st.header("3. 총 관객 수 분포")

# Plotly 히스토그램 생성
fig3 = px.histogram(
    df,
    x='total_audi',
    nbins=30,
    title="영화별 총 관객 수 분포 히스토그램",
    labels={'total_audi': '총 관객 수 (명)', 'count': '영화 수'},
    color_discrete_sequence=['#636EFA']
)

fig3.update_traces(
    hovertemplate="관객 수 구간: %{x}<br>영화 수: %{y}편"
)

# Y축 레이블 명시
fig3.update_layout(yaxis_title="영화 수")

# 그래프 출력
st.plotly_chart(fig3, use_container_width=True)

# 동적 문구 생성을 위한 데이터 계산
max_movie = df.loc[df['total_audi'].idxmax()]
max_movie_name = max_movie['movieNm']
max_movie_audi = max_movie['total_audi']

# 그래프 설명 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write(
    f"대부분의 영화가 **낮은 관객 수 구간(초반 구간)**에 촘촘히 몰려 있는 왼쪽으로 치우친(Right-skewed) 분포를 보이며, "
    f"가장 관객이 많은 영화는 **'{max_movie_name}'**(총 {max_movie_audi:,}명)입니다."
)

st.divider()

# ---------------------------------------------------------
# 네 번째 그래프 구역: 개봉일 스크린 수와 총 관객 수의 관계 (산점도)
# ---------------------------------------------------------
st.header("4. 개봉일 스크린 수와 총 관객 수의 관계")

# Plotly 산점도 생성
fig4 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    color='genre_clean',
    hover_name='movieNm',
    title="개봉일 스크린 수 vs 총 관객 수 산점도",
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'genre_clean': '장르'
    }
)

# 점 크기 및 불투명도 조정
fig4.update_traces(marker=dict(size=9, opacity=0.8))

# 그래프 출력
st.plotly_chart(fig4, use_container_width=True)

# 그래프 설명 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write("개봉 첫날 확보한 스크린 수가 많을수록 대체로 총 관객 수도 증가하는 양의 관계를 나타내지만, 스크린 수 대비 흥행 실적이 유독 뛰어난 영화나 반대로 스크린 확보 대비 아쉬운 성과를 낸 아웃라이어 영화들의 장르별 분포 차이를 함께 확인할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 다섯 번째 그래프 구역: 주요 장르별 총 관객 수 상자 그림 (박스플롯)
# ---------------------------------------------------------
st.header("5. 주요 장르별 총 관객 수 상자 그림")

# 영화가 10편 이상인 장르만 필터링
genre_counts_series = df['genre_clean'].value_counts()
major_genres = genre_counts_series[genre_counts_series >= 10].index
df_major_genres = df[df['genre_clean'].isin(major_genres)]

# Plotly 박스플롯 생성
fig5 = px.box(
    df_major_genres,
    x='genre_clean',
    y='total_audi',
    color='genre_clean',
    hover_name='movieNm',
    points='outliers',
    title="영화 수 10편 이상 장르의 총 관객 수 박스플롯",
    labels={
        'genre_clean': '장르',
        'total_audi': '총 관객 수 (명)'
    }
)

# 그래프 출력
st.plotly_chart(fig5, use_container_width=True)

# 그래프 설명 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write("영화 수가 10편 이상인 주요 장르 간 관객 수의 중간값과 스펙트럼(사분위수 범위)을 비교할 수 있으며, 박스 밖으로 튄 이상치 점을 통해 해당 장르의 대흥행작(아웃라이어)을 명확하게 파악할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 여섯 번째 그래프 구역: 개봉 첫 주 관객 수를 반영한 버블 차트
# ---------------------------------------------------------
st.header("6. 스크린 수, 총 관객 수, 개봉 첫 주 관객 수 (버블 차트)")

# Plotly 버블 차트 생성 (size=first_week_audi 추가)
fig6 = px.scatter(
    df,
    x='first_scrn',
    y='total_audi',
    size='first_week_audi',
    color='genre_clean',
    hover_name='movieNm',
    size_max=40,
    title="개봉일 스크린 수 vs 총 관객 수 (버블 크기: 개봉 첫 주 관객 수)",
    labels={
        'first_scrn': '개봉일 스크린 수 (개)',
        'total_audi': '총 관객 수 (명)',
        'first_week_audi': '첫 주 관객 수 (명)',
        'genre_clean': '장르'
    }
)

fig6.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<br>첫 주 관객 수: %{marker.size:,}명"
)

# 그래프 출력
st.plotly_chart(fig6, use_container_width=True)

# 그래프 설명 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write("초반 흥행 동력(개봉 첫 주 관객 수)이 장기 흥행(총 관객 수) 및 초기 스크린 확보 수와 어떤 관련이 있는지 원의 크기를 통해 3차원적인 관점에서 분석할 수 있습니다.")

st.divider()

# ---------------------------------------------------------
# 일곱 번째 그래프 구역: 제작 국가별 장르 구성 (선버스트 그래프)
# ---------------------------------------------------------
st.header("7. 제작 국가 및 장르별 영화 편수 선버스트")

# 선버스트 그래프에 사용할 데이터 정리 (결측치 제거 및 편수 집계)
df_sunburst = df.dropna(subset=['nation', 'genre_clean']).copy()

# Plotly 선버스트 차트 생성 (계층 구조: nation -> genre_clean)
fig7 = px.sunburst(
    df_sunburst,
    path=['nation', 'genre_clean'],
    title="제작 국가별 장르 분포 (칸 크기: 영화 편수)"
)

fig7.update_traces(
    hovertemplate="<b>%{label}</b><br>영화 편수: %{value}편<br>비율: %{percentParent:.1%}"
)

# 그래프 출력
st.plotly_chart(fig7, use_container_width=True)

# 그래프 설명 구역
st.subheader("💡 이 그래프로 알 수 있는 것")
st.write("한국, 미국 등 각 제작 국가별로 어떤 장르의 영화들이 주로 제작되어 상위권에 진입했는지 계층적 비중(영화 편수 기준)을 다차원적으로 파악할 수 있습니다.")
