import streamlit as st
st.title("나의 데이터 과학 포트폴리오")
st.write("반갑습니다! 이제부터 여기에 제 작업을 기록합니다.")
from datetime import datetime, timedelta
import zoneinfo
import pandas as pd
import requests
import streamlit as st

# Streamlit 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(page_title="일별 박스오피스", layout="wide")


# -------------------------------------------------------------------
# 1. API 데이터 가져오기 (캐시 적용)
# -------------------------------------------------------------------
# st.cache_data를 사용하여 동일한 날짜 요청은 1시간(3600초) 동안 저장(캐싱)합니다.
@st.cache_data(ttl=3600)
def fetch_box_office_data(target_date: str, api_key: str):
    """KOBIS API를 호출하여 해당 날짜의 일별 박스오피스 데이터를 가져옵니다."""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        # API 요청 보내기 (타임아웃 10초 설정)
        response = requests.get(url, params=params, timeout=10)

        # HTTP status code 오류 확인
        if response.status_code != 200:
            return None, f"서버 응답 오류 (상태 코드: {response.status_code})"

        data = response.json()

        # 1) API 인증키 오류 등의 예외 처리 (faultInfo 확인)
        if "faultInfo" in data:
            message = data["faultInfo"].get(
                "message", "인증키 또는 요청 문제 발생"
            )
            return None, f"API 오류 발생: {message}"

        # 2) 데이터 정상 구조 확인 및 영화 목록 추출
        box_office_result = data.get("boxOfficeResult", {})
        daily_list = box_office_result.get("dailyBoxOfficeList", [])

        # 3) 데이터가 비어있는 경우 처리
        if not daily_list:
            return (
                None,
                "EMPTY_DATA",
            )  # 데이터가 빈 경우 식별을 위한 특수 플래그 전달

        return daily_list, None

    except requests.exceptions.RequestException as e:
        # 네트워크 연결 문제 등의 예외 처리
        return None, f"네트워크 요청 실패: {e}"


# -------------------------------------------------------------------
# 2. 메인 화면 및 날짜 선택 UI 구성
# -------------------------------------------------------------------
st.title("🎬 일별 박스오피스 조회")

# KOBIS 인증키 불러오기 (secrets.toml 또는 Streamlit Cloud Secrets)
api_key = st.secrets.get("KOBIS_KEY")

# 인증키 미설정 시 안내
if not api_key:
    st.error("API 키가 설정되지 않았습니다.")
    st.info(
        "💡 **확인해 주세요:**\n"
        "Streamlit Cloud의 App Settings > Secrets 항목에 `KOBIS_KEY = '발급받은_키'`를 추가했는지 확인해 주세요."
    )
    st.stop()

# 한국 표준시(KST) 기준 어제 날짜 계산 (선택 가능한 가장 늦은 날짜)
kst_tz = zoneinfo.ZoneInfo("Asia/Seoul")
now_kst = datetime.now(kst_tz).date()
yesterday_kst = now_kst - timedelta(days=1)

# 달력 UI로 날짜 선택 (기본값: 어제, max_value: 어제)
selected_date = st.date_input(
    "조회할 날짜를 선택하세요 (오늘 날짜 이전만 선택 가능)",
    value=yesterday_kst,
    max_value=yesterday_kst,
)

target_date_str = selected_date.strftime("%Y%m%d")  # API 조회용 (YYYYMMDD)
formatted_date_display = selected_date.strftime(
    "%Y년 %m월 %d일"
)  # 화면 표시용

st.caption(
    f"선택한 날짜: **{formatted_date_display}** (한국 시간 기준)"
)

# API 호출
daily_list, error_msg = fetch_box_office_data(target_date_str, api_key)

# API 오류 및 예외 상황 처리 안내
if error_msg:
    if error_msg == "EMPTY_DATA":
        # 고른 날짜의 영화 목록이 비어 있는 경우 특수 안내
        st.info("💡 그날은 아직 집계 전입니다.")
    else:
        # 기타 API 오류 발생 시 안내
        st.error("데이터를 불러오지 못했습니다.")
        st.warning(f"**상세 원인:** {error_msg}")
        st.info(
            "💡 **해결 가이드:**\n"
            "1. KOBIS 개발자 센터에서 API 키가 올바르게 발급되었는지 확인해 주세요.\n"
            "2. Secrets에 입력한 `KOBIS_KEY` 값 앞뒤에 공백이 들어가지 않았는지 확인해 주세요.\n"
            "3. KOBIS API 서버 점검 또는 네트워크 통신 문제일 수 있으니 잠시 후 다시 시도해 주세요."
        )
    st.stop()

# -------------------------------------------------------------------
# 3. 데이터 전처리 (문자열 -> 숫자 변환 및 표현 가공)
# -------------------------------------------------------------------
df = pd.DataFrame(daily_list)

# 숫자로 변환할 컬럼 목록
numeric_columns = [
    "rank",
    "rankInten",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
    "showCnt",
]

# 문자열 데이터를 정수형(int64)으로 변환
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# 순위(rank) 기준으로 정렬
df = df.sort_values("rank").reset_index(drop=True)


# [기능 추가] 전날 대비 순위 증감(rankInten) 화살표 표시 함수
def format_rank_change(change):
    if change > 0:
        return f"🔺 {change}"  # 순위 상승 (빨간색 위 화살표)
    elif change < 0:
        return f"🔹 {abs(change)}"  # 순위 하락 (파란색 아래 화살표)
    else:
        return "-"  # 변동 없음


df["rankChange"] = df["rankInten"].apply(format_rank_change)


# [기능 추가] 누적 관객 100만 명 이상 영화 제목 옆 트로피 이모지 붙이기
def format_movie_title(row):
    title = row["movieNm"]
    if row["audiAcc"] >= 1_000_000:
        return f"🏆 {title}"
    return title


df["displayTitle"] = df.apply(format_movie_title, axis=1)


# -------------------------------------------------------------------
# 4. 1위 영화 지표 카드 (Metrics)
# -------------------------------------------------------------------
top_1 = df.iloc[0]

st.subheader(f"🥇 1위: {top_1['displayTitle']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        label="일일 관객수", value=f"{top_1['audiCnt']:,} 명"
    )  # 천 단위 쉼표 표기
with col2:
    st.metric(label="누적 관객수", value=f"{top_1['audiAcc']:,} 명")
with col3:
    st.metric(label="스크린수", value=f"{top_1['scrnCnt']:,} 개")

st.markdown("---")

# -------------------------------------------------------------------
# 5. 관객수 상위 5편 막대그래프
# -------------------------------------------------------------------
st.subheader("📊 관객수 상위 5개 영화")

# 상위 5개 데이터 추출
top_5_df = df.head(5)

# Streamlit 내장 막대그래프 사용 (X축: 영화명, Y축: 일일 관객수)
st.bar_chart(data=top_5_df, x="movieNm", y="audiCnt", color="#FF4B4B")

st.markdown("---")

# -------------------------------------------------------------------
# 6. 전체 박스오피스 순위 표
# -------------------------------------------------------------------
st.subheader("📋 전체 박스오피스 순위")

# 화면에 보여줄 컬럼 선택 및 순서 변경
display_df = df[
    [
        "rank",
        "rankChange",
        "displayTitle",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
    ]
].copy()

# 출력용 열 이름으로 변경
display_df.columns = [
    "순위",
    "전날 대비",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수",
]

# 데이터프레임 출력 (숫자 포맷팅 적용)
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "관객수": st.column_config.NumberColumn(format="%d명"),
        "누적관객": st.column_config.NumberColumn(format="%d명"),
        "스크린수": st.column_config.NumberColumn(format="%d개"),
    },
)
