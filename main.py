import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # 원본 선 + 이동평균 선을 함께 그리기 위해 사용

# ------------------------------------------------------------
# 기본 페이지 설정
# ------------------------------------------------------------
st.set_page_config(page_title="박스오피스 대시보드", layout="wide")
st.title("🎬 박스오피스 데이터 대시보드")

# 데이터가 들어있는 CSV 파일 주소
DATA_URL = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"


# ------------------------------------------------------------
# [1] 데이터 불러오기
# ------------------------------------------------------------
# @st.cache_data 를 붙이면, 같은 함수를 다시 호출해도
# 이미 계산해 둔 결과를 재사용합니다.
# 즉, 앱이 새로고침될 때마다 인터넷에서 CSV를 다시 받아오지 않고
# 처음 한 번만 받아온 뒤 저장해 둔 데이터를 그대로 씁니다.
@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    # pandas로 CSV 파일을 읽어옵니다.
    df = pd.read_csv(url)

    # ------------------------------------------------------------
    # [2] 날짜 전처리
    # ------------------------------------------------------------
    # 결측치(비어있는 값)가 하나라도 있는 행은 통째로 삭제합니다.
    df = df.dropna()

    # "기준일자" 컬럼을 문자열(yyyy-mm-dd)에서 진짜 날짜(datetime) 형식으로 바꿉니다.
    # 날짜 형식으로 바꿔두면 이후에 날짜순 정렬이나 그래프 그리기가 편해집니다.
    df["기준일자"] = pd.to_datetime(df["기준일자"], format="%Y-%m-%d")

    # 기준일자를 기준으로 오래된 날짜 -> 최신 날짜 순서로 정렬합니다.
    df = df.sort_values("기준일자").reset_index(drop=True)

    return df


# 위에서 만든 함수를 호출해서 데이터를 불러옵니다.
# 캐시 덕분에 이 줄은 앱이 처음 켜질 때 딱 한 번만 실제로 실행됩니다.
df = load_data(DATA_URL)


# ------------------------------------------------------------
# [3] 영화 선택 기능
# ------------------------------------------------------------
st.header("🔍 영화 선택")

# 영화별 "가장 최근 누적관객수"를 기준으로 순위를 매기기 위해
# 영화명으로 그룹을 묶고, 각 영화의 최대 누적관객수를 구합니다.
# (누적관객수는 계속 증가하는 값이므로, 최댓값이 곧 최신 누적관객수입니다.)
movie_ranking = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)  # 누적관객수가 많은 순으로 내림차순 정렬
)

# 정렬된 순서를 그대로 리스트로 만들어 선택 목록에 사용합니다.
movie_list = movie_ranking.index.tolist()

# 사용자가 드롭다운에서 영화를 하나 선택할 수 있게 합니다.
selected_movie = st.selectbox("영화를 선택하세요 (누적관객수 내림차순)", movie_list)


# ------------------------------------------------------------
# [4] 선그래프 그리기: 일자별 해당일관객수 변화
# ------------------------------------------------------------
st.header("📈 그래프 1. 일자별 관객수 변화")

# 선택한 영화에 해당하는 데이터만 뽑아냅니다.
movie_df = df[df["영화명"] == selected_movie].sort_values("기준일자")

# Plotly로 선 그래프를 그립니다.
# x축: 기준일자, y축: 해당일관객수
fig1 = px.line(
    movie_df,
    x="기준일자",
    y="해당일관객수",
    markers=True,  # 각 데이터 포인트에 점을 표시해서 더 잘 보이게 함
    title=f"'{selected_movie}'의 일자별 관객수 변화",
)
fig1.update_layout(xaxis_title="기준일자", yaxis_title="해당일 관객수")

st.plotly_chart(fig1, use_container_width=True)

# 그래프 아래에 이 그래프로 알 수 있는 것을 적는 자리입니다.
# 문구는 원하는 내용으로 자유롭게 수정해서 사용하세요.
st.caption("💡 이 그래프로 알 수 있는 것: (여기에 문장을 채워주세요)")


# ------------------------------------------------------------
# [5] 앞으로 그래프를 추가할 구역
# ------------------------------------------------------------
# 아래에 새로운 그래프를 계속 추가할 수 있도록
# st.header(), st.subheader() 등으로 구역을 나눠 두었습니다.
# 예시) 그래프 2를 추가하고 싶다면 아래 형태를 참고해서 작성하세요.
#
# st.header("📈 그래프 2. (그래프 제목)")
# fig2 = px.line(...)
# st.plotly_chart(fig2, use_container_width=True)
# st.caption("💡 이 그래프로 알 수 있는 것: (문장을 채워주세요)")

st.header("📈 그래프 2. 일자별 누적관객수 변화 (영역차트)")

# 그래프 1과 같은 영화(movie_df)의 데이터를 그대로 사용합니다.
# 영역차트(area chart)는 선 아래 영역을 색으로 채워서
# 값이 누적되어 커지는 흐름을 한눈에 보기 좋게 보여줍니다.
fig2 = px.area(
    movie_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}'의 일자별 누적관객수 변화",
)
fig2.update_layout(xaxis_title="기준일자", yaxis_title="누적 관객수")

st.plotly_chart(fig2, use_container_width=True)

# 그래프 아래에 이 그래프로 알 수 있는 것을 적는 자리입니다.
st.caption("💡 이 그래프로 알 수 있는 것: (여기에 문장을 채워주세요)")


st.header("📈 그래프 3. 누적관객수 상위 5개 영화 비교 (다중 선그래프)")

# 이 데이터는 하루하루의 "박스오피스 TOP10" 기록이기 때문에,
# 한 영화가 df에 등장한 행(row)의 개수 = 그 영화가 TOP10에 든 일수가 됩니다.
top10_days_count = df.groupby("영화명").size()

# TOP10에 20일 미만으로 등장한 영화는 꾸준한 흥행이라 보기 어려우므로 제외합니다.
qualified_movies = top10_days_count[top10_days_count >= 20].index

# 조건을 만족하는 영화들만 대상으로, 누적관객수 기준으로 다시 순위를 매깁니다.
qualified_ranking = movie_ranking[movie_ranking.index.isin(qualified_movies)]

# 그중 누적관객수가 가장 높은 5개 영화를 선택합니다.
top5_movies = qualified_ranking.head(5).index.tolist()

# 전체 데이터(df)에서 상위 5개 영화에 해당하는 행만 골라냅니다.
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("기준일자")

# Plotly에서 color="영화명"을 지정하면
# 영화별로 자동으로 다른 색의 선이 그려지고, 범례(legend)도 함께 표시됩니다.
fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화별로 선 색을 다르게, 범례도 자동 생성
    title="TOP10 20일 이상 등장 영화 중 누적관객수 상위 5개 영화의 일자별 누적관객수 변화",
)
fig3.update_layout(
    xaxis_title="기준일자",
    yaxis_title="누적 관객수",
    legend_title="영화명",
)

st.plotly_chart(fig3, use_container_width=True)

# 그래프 아래에 이 그래프로 알 수 있는 것을 적는 자리입니다.
st.caption("💡 이 그래프로 알 수 있는 것: (여기에 문장을 채워주세요)")


# ------------------------------------------------------------
# [그래프 4] TOP10 전체 합계 관객수 + 7일 이동평균
# ------------------------------------------------------------
st.header("📈 그래프 4. TOP10 전체 합계 관객수와 7일 이동평균")

# 하루하루 TOP10에 오른 영화들의 "해당일관객수"를 모두 더해서
# 그날의 전체 박스오피스(TOP10) 관객수 합계를 구합니다.
daily_total = df.groupby("기준일자")["해당일관객수"].sum().reset_index()
daily_total.columns = ["기준일자", "합계관객수"]

# 날짜순으로 정렬되어 있는지 다시 한 번 확인합니다.
daily_total = daily_total.sort_values("기준일자")

# rolling(window=7)은 "최근 7개 값의 평균"을 구해줍니다.
# 날짜별로 정렬된 상태에서 사용하면 "최근 7일간의 평균"이 됩니다.
# 요일에 따른 들쭉날쭉함(주말에 관객이 몰리는 등)을 완화해서
# 전체적인 추세를 더 부드럽게 볼 수 있게 해줍니다.
daily_total["7일_이동평균"] = daily_total["합계관객수"].rolling(window=7).mean()

# 원본 선과 이동평균 선을 한 그래프에 겹쳐 그리기 위해
# plotly.express 대신 graph_objects(go)를 사용합니다.
fig4 = go.Figure()

# 원본 합계값 선: 연하게(투명도 낮춤) 표시해서 배경처럼 보이게 합니다.
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["합계관객수"],
        mode="lines",
        name="일별 합계 관객수 (원본)",
        line=dict(color="royalblue", width=1),
        opacity=0.35,  # 값이 낮을수록 더 연하게 표시됩니다.
    )
)

# 7일 이동평균 선: 진하고 두껍게 표시해서 추세가 잘 보이게 합니다.
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="royalblue", width=3),
    )
)

fig4.update_layout(
    title="TOP10 전체 합계 관객수 (원본) 및 7일 이동평균",
    xaxis_title="기준일자",
    yaxis_title="합계 관객수",
    legend_title="구분",
)

st.plotly_chart(fig4, use_container_width=True)

# 그래프 아래에 이 그래프로 알 수 있는 것을 적는 자리입니다.
st.caption("💡 이 그래프로 알 수 있는 것: (여기에 문장을 채워주세요)")


# ------------------------------------------------------------
# 앞으로 그래프를 추가할 구역 (예: 그래프 5)
# ------------------------------------------------------------
# st.header("📈 그래프 5. (그래프 제목)")
# fig5 = px.line(...) 또는 px.area(...), px.bar(...) 등
# st.plotly_chart(fig5, use_container_width=True)
# st.caption("💡 이 그래프로 알 수 있는 것: (문장을 채워주세요)")
